import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sentinel import calendar_guard, episodes, scoring  # noqa: E402
from sentinel.util import canon, sha12  # noqa: E402

CFG = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config", "sentinel.json"), encoding="utf-8"))
Q = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config", "queries.json"), encoding="utf-8"))
INST = {i["key"]: i for i in json.load(open(os.path.join(os.path.dirname(__file__), "..", "config",
                                                          "instruments.json"), encoding="utf-8"))["instruments"]}
NOW = 1_800_000_000.0


def series(price_now, price_60m_ago, price_240m_ago=None, step=300):
    """Pravi seriju svakih 5 min tako da je pomak za 60 min tacan."""
    pts = []
    for k in range(60, -1, -1):  # 300 min unazad
        t = NOW - k * step
        if k * step >= 240 * 60 and price_240m_ago:
            p = price_240m_ago
        elif k * step >= 60 * 60:
            p = price_60m_ago
        else:
            f = 1 - (k * step) / 3600.0
            p = price_60m_ago + (price_now - price_60m_ago) * f
        pts.append((t, p))
    return pts


def psig(key, now_px, ref_px, second=None, sigma=None):
    return scoring.price_signal(INST[key], series(now_px, ref_px), "test", second, sigma, CFG, NOW)


class PriceTests(unittest.TestCase):
    def test_trigger_and_direction(self):
        p = psig("BRENT", 97.0, 100.0)
        self.assertTrue(p["trig"])
        self.assertEqual(p["dir"], "down")
        self.assertAlmostEqual(p["m60"], -3.0, places=1)

    def test_below_threshold(self):
        self.assertFalse(psig("BRENT", 99.0, 100.0)["trig"])

    def test_stale_price_is_ignored(self):
        s = [(NOW - 3600, 100.0), (NOW - 1800, 97.0)]
        p = scoring.price_signal(INST["BRENT"], s, "test", None, None, CFG, NOW)
        self.assertTrue(p["stale"])

    def test_sigma_raises_trigger(self):
        # 2.6% je preko praga 2.5, ali sigma 1% x 4 = 4% zahteva vise
        self.assertFalse(psig("BRENT", 97.4, 100.0, sigma=1.0)["trig"])
        self.assertTrue(psig("BRENT", 97.4, 100.0, sigma=0.3)["trig"])

    def test_second_provider_confirms_only_same_direction(self):
        ok = psig("BRENT", 97.0, 100.0, second=series(96.9, 100.0))
        bad = psig("BRENT", 97.0, 100.0, second=series(103.0, 100.0))
        flat = psig("BRENT", 97.0, 100.0, second=series(99.9, 100.0))
        self.assertTrue(ok["confirmed"])
        self.assertFalse(bad["confirmed"])
        self.assertFalse(flat["confirmed"])


def evaluate(psigs, head_items=(), movers=(), offi=(), vix=None):
    cross = scoring.cross_signal(psigs, CFG, vix)
    head = scoring.headline_signal(list(head_items), NOW, CFG, Q)
    return scoring.evaluate_themes(psigs, cross, head, list(offi), list(movers), {"fired": False}, CFG)


def news(title, source, age_min=5):
    return {"title": title, "source": source, "ts": NOW - age_min * 60}


class TierTests(unittest.TestCase):
    def test_news_without_price_never_exceeds_n1(self):
        items = [news("War erupts as missile strike hits Hormuz tanker, oil", "Reuters"),
                 news("Blockade of Hormuz raises oil war fears", "BBC")]
        out = evaluate([psig("BRENT", 100.0, 100.0)], items)
        self.assertIn(out["OIL"]["tier"], ("N1", None))

    def test_price_only_confirmed_is_n1(self):
        p = psig("BRENT", 96.5, 100.0, second=series(96.4, 100.0))  # 3.5%, 1.4x prag
        out = evaluate([p])
        self.assertEqual(out["OIL"]["tier"], "N1")

    def test_extreme_move_confirmed_is_n2(self):
        p = psig("BRENT", 94.0, 100.0, second=series(94.1, 100.0))  # 6%, 2.4x prag: P2 + PX
        out = evaluate([p])
        self.assertEqual(out["OIL"]["tier"], "N2")

    def test_price_plus_news_plus_prediction_is_n3(self):
        p = psig("BRENT", 94.0, 100.0, second=series(94.1, 100.0))
        items = [news("Hormuz blockade war escalates, oil tanker attack", "Reuters"),
                 news("Missile strike war oil Hormuz crude surge", "Al Jazeera")]
        movers = [{"id": "1", "q": "Will Iran strike oil tanker?", "p": 0.6, "ref": 0.3, "delta": 0.3,
                   "themes": ["OIL"]}]
        out = evaluate([p], items, movers)
        self.assertEqual(out["OIL"]["tier"], "N3")
        self.assertGreaterEqual(out["OIL"]["score"], 4.5)

    def test_headlines_need_two_publishers(self):
        items = [news("War missile strike oil Hormuz blockade", "Reuters"),
                 news("War missile strike oil Hormuz blockade escalates", "Reuters")]
        h = scoring.headline_signal(items, NOW, CFG, Q)
        self.assertFalse(h["themes"]["OIL"]["fired"])

    def test_old_headlines_are_ignored(self):
        items = [news("War missile strike oil Hormuz blockade", "Reuters", 120),
                 news("War missile strike oil Hormuz blockade", "BBC", 120)]
        self.assertEqual(scoring.headline_signal(items, NOW, CFG, Q)["n"], 0)

    def test_cross_asset(self):
        ps = [psig("BRENT", 97.0, 100.0), psig("GOLD", 4100.0, 4050.0), psig("SP500", 7700.0, 7800.0)]
        self.assertTrue(scoring.cross_signal(ps, CFG)["fired"])
        self.assertFalse(scoring.cross_signal(ps[:2], CFG)["fired"])

    def test_prediction_mover(self):
        hist = {"1": [[NOW - 3000, 0.30]]}
        mk = [{"id": "1", "q": "Will Iran close Hormuz?", "p": 0.50, "vol24": 90000.0}]
        m = scoring.prediction_signal(mk, hist, NOW, CFG, Q)
        self.assertEqual(len(m), 1)
        mk[0]["vol24"] = 1000.0
        self.assertEqual(scoring.prediction_signal(mk, hist, NOW, CFG, Q), [])


class EpisodeTests(unittest.TestCase):
    def ev(self, tier, m60):
        p = psig("BRENT", 100.0 * (1 + m60 / 100.0), 100.0)
        return {"tier": tier, "instruments": ["BRENT"]}, [p]

    def test_open_then_quiet_then_escalate_then_close(self):
        eps = {}
        e, ps = self.ev("N2", -3.0)
        self.assertEqual(episodes.step("OIL", e, ps, NOW, eps, CFG)["kind"], "open")
        self.assertIsNone(episodes.step("OIL", e, ps, NOW + 600, eps, CFG))  # isti nivo, bez novog koraka
        e3, ps3 = self.ev("N3", -3.2)
        self.assertEqual(episodes.step("OIL", e3, ps3, NOW + 900, eps, CFG)["kind"], "escalate")
        calm = {"tier": "N1", "instruments": []}
        self.assertIsNone(episodes.step("OIL", calm, [], NOW + 900 + 60 * 60, eps, CFG))
        self.assertEqual(episodes.step("OIL", calm, [], NOW + 900 + 121 * 60, eps, CFG)["kind"], "closed")
        self.assertNotIn("OIL", eps)

    def test_new_step_fires_only_after_cooldown(self):
        eps = {}
        e, ps = self.ev("N2", -3.0)
        episodes.step("OIL", e, ps, NOW, eps, CFG)
        e2, ps2 = self.ev("N2", -6.5)
        self.assertIsNone(episodes.step("OIL", e2, ps2, NOW + 30 * 60, eps, CFG))
        self.assertEqual(episodes.step("OIL", e2, ps2, NOW + 61 * 60, eps, CFG)["kind"], "step")

    def test_fire_limits(self):
        cfg = dict(CFG, fire_enabled=True)
        self.assertTrue(episodes.fire_allowed([], NOW, cfg)[0])
        self.assertFalse(episodes.fire_allowed([NOW - 600], NOW, cfg)[0])
        self.assertFalse(episodes.fire_allowed([NOW - 3600 * 5, NOW - 3600 * 4, NOW - 3600 * 3], NOW, cfg)[0])
        self.assertFalse(episodes.fire_allowed([], NOW, dict(CFG, fire_enabled=False))[0])


class MiscTests(unittest.TestCase):
    def test_canon_is_deterministic(self):
        a = {"b": 1, "a": [1, 2], "c": "č"}
        b = {"c": "č", "a": [1, 2], "b": 1}
        self.assertEqual(canon(a), canon(b))
        self.assertEqual(sha12(canon(a)), sha12(canon(b)))
        self.assertEqual(len(sha12(canon(a))), 12)

    def test_calendar_eia_wednesday(self):
        cal = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config", "calendar.json"),
                             encoding="utf-8"))
        # sreda 2026-10-07, 10:30 EDT = 14:30 UTC
        t = dt.datetime(2026, 10, 7, 14, 30, tzinfo=dt.timezone.utc).timestamp()
        self.assertTrue(any("EIA" in f for f in calendar_guard.scheduled_flags(t, cal)))
        t2 = dt.datetime(2026, 10, 7, 18, 0, tzinfo=dt.timezone.utc).timestamp()
        self.assertFalse(calendar_guard.scheduled_flags(t2, cal))
        # posle prelaska na zimsko vreme: 10:30 EST = 15:30 UTC
        t3 = dt.datetime(2026, 11, 4, 15, 30, tzinfo=dt.timezone.utc).timestamp()
        self.assertTrue(any("EIA" in f for f in calendar_guard.scheduled_flags(t3, cal)))

    def test_calendar_nfp_first_friday(self):
        cal = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config", "calendar.json"),
                             encoding="utf-8"))
        t = dt.datetime(2026, 10, 2, 12, 30, tzinfo=dt.timezone.utc).timestamp()  # prvi petak oktobra, EDT
        self.assertTrue(any("NFP" in f for f in calendar_guard.scheduled_flags(t, cal)))


if __name__ == "__main__":
    unittest.main()
