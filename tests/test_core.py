import datetime as dt
import json
import math
import os
import tempfile
import unittest

from lab import core as K

CFG = dict(K.load_cfg(), universe=["UP", "DN", "FLAT", "NOISE"], t0_candle="2024-10-01")


def days(n, start="2024-01-01"):
    d0 = dt.date.fromisoformat(start)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range(n)]


def world(n=320):
    """UP raste ~0,5% dnevno sa sumom, DN pada, FLAT ravan sa sumom, NOISE osciluje."""
    ds = days(n)
    rows = {}
    for s in ("UP", "DN", "FLAT", "NOISE"):
        px, p = [], 100.0
        for i in range(n):
            wiggle = 0.01 * math.sin(i * 1.7 + len(s)) + 0.005 * math.cos(i * 0.9)
            drift = {"UP": 0.005, "DN": -0.005, "FLAT": 0.0, "NOISE": 0.0}[s]
            p *= 1.0 + drift + wiggle
            px.append(p)
        rows[s] = list(zip(ds, px))
    return rows


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.rows = world()
        self.dates, self.px = K.build_matrix(self.rows)

    def test_uptrend_is_held_downtrend_is_not_long_only(self):
        e = K.ensemble(self.px, self.dates, CFG)
        self.assertGreater(e["w"]["UP"], 0)
        self.assertEqual(e["w"]["DN"], 0.0)
        self.assertTrue(all(v >= 0 for v in e["w"].values()))

    def test_gross_never_exceeds_cap_and_signals_reported(self):
        e = K.ensemble(self.px, self.dates, CFG)
        self.assertLessEqual(e["gross"], CFG["max_gross"] + 1e-9)
        self.assertEqual(set(e["sig"]["UP"]), {"L14", "L28", "L56", "L112"})
        self.assertEqual(e["sig"]["DN"]["L14"], 0)

    def test_long_short_shorts_the_downtrend(self):
        e = K.ensemble(self.px, self.dates, CFG, long_only=False)
        self.assertLess(e["w"]["DN"], 0)

    def test_weights_change_only_on_rebalance_days(self):
        # kriva tezina po danima: ponovo pokrenemo sa skracenim istorijama i uporedimo drzane tezine
        prev, changes = None, []
        for n in range(200, 260):
            ds, px = K.build_matrix({s: r[:n] for s, r in self.rows.items()})
            w = K.strategy(px, ds, CFG, 28)["w"]
            if prev is not None and w != prev:
                changes.append(dt.date.fromisoformat(ds[-1]).weekday())
            prev = w
        self.assertTrue(changes)
        self.assertEqual(set(changes), {6})  # menja se samo kad je zadnja svece nedeljna

    def test_no_lookahead_past_is_unchanged_by_future_prices(self):
        k = 250
        a = K.ensemble(self.px, self.dates, CFG)
        rows2 = {s: r[:k] + [(d, p * 3.0) for d, p in r[k:]] for s, r in self.rows.items()}
        ds2, px2 = K.build_matrix(rows2)
        b = K.ensemble(px2, ds2, CFG)
        for i in range(k):
            self.assertAlmostEqual(a["net"][i], b["net"][i], places=12)

    def test_cost_reduces_return_by_turnover(self):
        free = K.ensemble(self.px, self.dates, CFG, cost=0.0)
        paid = K.ensemble(self.px, self.dates, CFG, cost=0.01)
        self.assertLess(sum(paid["net"]), sum(free["net"]))
        self.assertTrue(all(p <= f + 1e-12 for p, f in zip(paid["net"], free["net"])))

    def test_missing_prices_do_not_crash_and_are_not_held(self):
        rows = {s: list(r) for s, r in self.rows.items()}
        rows["NOISE"] = rows["NOISE"][:150]  # kovanica "nestaje"
        rows["FLAT"] = [x for i, x in enumerate(rows["FLAT"]) if i % 9]  # rupe u svecama
        ds, px = K.build_matrix(rows)
        e = K.ensemble(px, ds, CFG)
        self.assertEqual(e["w"]["NOISE"], 0.0)
        self.assertEqual(len(e["net"]), len(ds))

    def test_vol_target_scales_down_when_vol_is_high(self):
        calm, wild = {}, {}
        ds = days(320)
        for s in ("A", "B", "C", "D"):
            p1 = p2 = 100.0
            c, w = [], []
            for i in range(320):
                base = 0.004 + 0.001 * math.sin(i * 0.3)
                p1 *= 1.0 + base
                p2 *= 1.0 + base + 0.05 * math.sin(i * 2.1 + len(s))
                c.append(p1)
                w.append(p2)
            calm[s], wild[s] = list(zip(ds, c)), list(zip(ds, w))
        cfg = dict(CFG, universe=list(calm), t0_candle=ds[250])
        d1, p1 = K.build_matrix(calm)
        d2, p2 = K.build_matrix(wild)
        g1 = K.ensemble(p1, d1, cfg)["gross"]
        g2 = K.ensemble(p2, d2, cfg)["gross"]
        self.assertLessEqual(g2, g1 + 1e-9)


class TestFundingPitCsm(unittest.TestCase):
    def setUp(self):
        self.rows = world()
        self.dates, self.px = K.build_matrix(self.rows)
        self.n = len(self.dates)

    def test_long_pays_and_short_receives_funding(self):
        fund = {s: [0.001] * self.n for s in self.px}
        base = K.ensemble(self.px, self.dates, CFG)
        paid = K.ensemble(self.px, self.dates, CFG, fund=fund)
        self.assertLess(sum(paid["net"]), sum(base["net"]))  # duga noga placa
        base_ls = K.ensemble(self.px, self.dates, CFG, long_only=False)
        paid_ls = K.ensemble(self.px, self.dates, CFG, long_only=False, fund=fund)
        # u dugo/kratko korpi razlika je mala jer se placanje i primanje delimicno potiru, ali nije nula
        self.assertNotEqual(round(sum(paid_ls["net"]), 9), round(sum(base_ls["net"]), 9))

    def test_daily_funding_sums_hourly_points_per_utc_day(self):
        pts = [(1704067200000, 0.0001), (1704070800000, 0.0002), (1704153600000, 0.0003)]  # 2024-01-01 00:00, 01:00, 2024-01-02 00:00
        got = dict(K.daily_funding(pts))
        self.assertAlmostEqual(got["2024-01-01"], 0.0003, places=9)
        self.assertAlmostEqual(got["2024-01-02"], 0.0003, places=9)
        al = K.align_funding(["2024-01-01", "2024-01-02", "2024-01-03"], {"X": K.daily_funding(pts)})
        self.assertEqual(al["X"][2], None)

    def test_pit_eligibility_picks_top_by_dollar_volume_requires_history_and_drops_delisted(self):
        n = 200
        ds = days(n)
        closes = {"BIG": [10.0] * n, "MID": [10.0] * n, "SMALL": [10.0] * n, "NEW": [None] * 150 + [10.0] * 50, "DEAD": [10.0] * 120 + [None] * 80}
        vols = {"BIG": [1000.0] * n, "MID": [100.0] * n, "SMALL": [1.0] * n, "NEW": [5000.0] * n, "DEAD": [900.0] * 120 + [None] * 80}
        el = K.pit_eligibility(ds, closes, vols, top_n=2, win=30, min_hist=60)
        self.assertTrue(el["BIG"][100] and el["DEAD"][100] and not el["SMALL"][100])  # DEAD je tada bio drugi po prometu
        self.assertFalse(el["DEAD"][150])  # ugasena: vise nije u univerzumu
        self.assertFalse(el["NEW"][160])  # premalo istorije, bez obzira na promet
        self.assertTrue(el["NEW"][199] is False or el["NEW"][199])  # posle min_hist moze da udje
        self.assertTrue(el["BIG"][199])

    def test_csm_mode_goes_long_leader_and_short_laggard(self):
        cfg = dict(CFG, csm_k=1, min_names=2)
        e = K.ensemble(self.px, self.dates, cfg, mode="csm", lookbacks=[28])
        self.assertGreater(e["w"]["UP"], 0)
        self.assertLess(e["w"]["DN"], 0)
        self.assertEqual(e["w"]["FLAT"], 0.0)
        self.assertLessEqual(e["gross"], cfg["max_gross"] + 1e-9)

    def test_eligibility_mask_keeps_ineligible_coin_out_of_trend_weights(self):
        el = {s: [s != "UP"] * self.n for s in self.px}  # UP nikad nije u univerzumu
        e = K.ensemble(self.px, self.dates, CFG, elig=el)
        self.assertEqual(e["w"]["UP"], 0.0)


class TestMetrics(unittest.TestCase):
    def test_metrics_and_yearly(self):
        ds = days(400)
        rets = [0.001 if i % 2 else -0.0005 for i in range(400)]
        m = K.metrics(ds, rets)
        self.assertEqual(m["n_days"], 400)
        self.assertGreater(m["sharpe"], 0)
        self.assertLessEqual(m["maxdd_pct"], 0)
        y = K.yearly(ds, rets)
        self.assertEqual(set(y), {"2024", "2025"})
        self.assertEqual(K.metrics(ds[:10], rets[:10]), {"n_days": 10})


class TestCompute(unittest.TestCase):
    def test_compute_has_shadow_curve_from_t0_and_schedule(self):
        out = K.compute(CFG, world(), now_ms=1730000000000)
        self.assertNotIn("error", out)
        self.assertEqual(out["t0_candle"], "2024-10-01")
        self.assertEqual(out["shadow"]["curve"][0][0], "2024-10-02")  # prvi prinos je prvog dana posle T0
        self.assertGreater(out["weights"]["UP"], 0)
        self.assertEqual(dt.date.fromisoformat(out["next_rebalance_candle"]).weekday(), CFG["rebalance_candle_weekday"])
        self.assertGreater(out["next_rebalance_candle"], out["last_candle"])
        json.dumps(out)  # mora da se serijalizuje

    def test_compute_reports_error_on_short_history_or_missing_t0(self):
        short = {s: r[:80] for s, r in world().items()}
        self.assertIn("error", K.compute(CFG, short, now_ms=1))
        self.assertIn("error", K.compute(dict(CFG, t0_candle="2030-01-01"), world(), now_ms=1))


class TestRun(unittest.TestCase):
    def fake(self, ds_rows):
        def f(coin, days_, now):
            if coin not in ds_rows:
                raise RuntimeError("nema")
            return [{"t": int(dt.datetime.fromisoformat(d).replace(tzinfo=dt.timezone.utc).timestamp() * 1000), "c": p} for d, p in ds_rows[coin]]
        return f

    def test_run_writes_state_once_per_day_and_never_raises_on_missing_coin(self):
        rows = world()
        last = rows["UP"][-1][0]
        now_ms = int(dt.datetime.fromisoformat(last).replace(tzinfo=dt.timezone.utc).timestamp() * 1000) + 86400000 + 3600000  # 01:00 sutradan
        cfg = dict(CFG, min_names=3)
        with tempfile.TemporaryDirectory() as d:
            lines = []
            del rows["NOISE"]  # jedna kovanica ne uspeva
            r1 = K.run(d, cfg, now_ms, self.fake(rows), log=lines.append)
            self.assertEqual(r1["ok"], last)
            self.assertTrue(any("NOISE" in x for x in lines))
            with open(os.path.join(d, "core", "core.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["last_candle"], last)
            r2 = K.run(d, cfg, now_ms, self.fake(rows), log=lines.append)
            self.assertIn("skipped", r2)

    def test_run_skips_in_first_minutes_after_midnight(self):
        with tempfile.TemporaryDirectory() as d:
            now_ms = int(dt.datetime(2024, 11, 5, 0, 2, tzinfo=dt.timezone.utc).timestamp() * 1000)
            self.assertIn("skipped", K.run(d, CFG, now_ms, self.fake({}), log=lambda *a: None))

    def test_main_swallows_errors(self):
        with tempfile.TemporaryDirectory() as d:
            old = K.fetch_rows
            K.fetch_rows = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("mreza"))
            try:
                self.assertEqual(K.main(["--state", d, "--force"]), 0)
            finally:
                K.fetch_rows = old


if __name__ == "__main__":
    unittest.main()
