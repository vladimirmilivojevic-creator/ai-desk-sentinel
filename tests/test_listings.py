import json
import os
import tempfile
import unittest

from lab import jumps as J
from lab import listings as L

CFG = L.load_cfg()
MIN = L.MIN
T0 = 1791800000000  # proizvoljan trenutak


def notice(i, title, t_ms):
    import datetime as dt
    return {"id": i, "title": title, "listed_at": dt.datetime.fromtimestamp(t_ms / 1000.0, dt.timezone(dt.timedelta(hours=9))).isoformat()}


RSR = "리저브라이트(RSR) KRW, USDT 마켓 디지털 자산 추가"
KAIA = "카이아(KAIA) 신규 거래지원 안내 (KRW, BTC, USDT 마켓)"
TWO = "페이팔유에스디(PYUSD), 제이피와이코인(JPYC) 신규 거래지원 안내 (KRW, BTC, USDT 마켓)"
NOISE = ["블러(BLUR) 거래 유의 종목 지정 안내", "아이콘(ICX) 거래지원 종료 안내 (10/19 15:00)", "렌조(REZ) 신규 거래지원 안내 (USDT 마켓) (거래지원 개시 시점 추가 변경 안내)",
         "헤미(HEMI), 유즈리스(USELESS) 신규 거래지원 안내 (BTC, USDT 마켓) (헤미(HEMI) 거래지원 취소 안내)", "카이아(KAIA) 신규 거래지원 안내 (KRW, BTC, USDT 마켓) (KAIA/BTC 초기 매수 제한 안내)"]


def ctx(**px):
    return {k: {"mark": v, "oi_usd": 1.4e6 if k == "RSR" else 50e6} for k, v in px.items()}


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class ParseTests(unittest.TestCase):
    def test_only_first_listing_announcements_with_their_symbols(self):
        ns = [notice("1", RSR, T0), notice("2", KAIA, T0), notice("3", TWO, T0)] + [notice(str(10 + i), t, T0) for i, t in enumerate(NOISE)]
        out = L.parse_upbit(ns, CFG)
        self.assertEqual([(n["id"], n["syms"]) for n in out], [("1", ["RSR"]), ("2", ["KAIA"]), ("3", ["PYUSD", "JPYC"])])
        self.assertEqual(out[0]["t_ms"], T0)  # ISO vreme sa +09:00 se pretvara u UTC milisekunde

    def test_bad_notices_are_ignored(self):
        self.assertEqual(L.parse_upbit([{"title": RSR}, {"title": None, "listed_at": "x"}, {"id": 5, "title": RSR, "listed_at": "nije datum"}], CFG), [])


class PriceTests(unittest.TestCase):
    def test_hl_mark_then_k_prefix_then_binance_then_none(self):
        self.assertEqual(L.price_of("RSR", ctx(RSR=0.002), CFG), (0.002, "hl", 1.4e6))
        k = L.price_of("PEPE", {"kPEPE": {"mark": 0.012, "oi_usd": 3e6}}, CFG)
        self.assertAlmostEqual(k[0], 0.000012)  # k = 1000 jedinica
        self.assertEqual(L.price_of("NEWX", {}, CFG, spot=lambda s, c: 2.5), (2.5, "binance", None))
        def boom(s, c):
            raise OSError("mreza")
        self.assertIsNone(L.price_of("NEWX", {}, CFG, spot=boom))

    def test_price_before_uses_radar_snapshot_not_the_future(self):
        snap = {"RSR": [[T0 - 30 * MIN, 0.00166, 0], [T0 - 5 * MIN, 0.00167, 0], [T0 + 5 * MIN, 0.0024, 0]]}
        self.assertEqual(L.price_before(snap, "RSR", T0, {"RSR": {}}), 0.00167)
        self.assertIsNone(L.price_before(snap, "RSR", T0 - 2 * 60 * MIN, {"RSR": {}}))


class RunTests(unittest.TestCase):
    def test_first_run_seeds_without_events_then_new_notice_and_new_coinbase_asset_become_events(self):
        with tempfile.TemporaryDirectory() as d:
            up1 = lambda c: [notice("1", KAIA, T0 - 3 * 86400000)]
            r1 = L.run(d, ctx(RSR=0.0017), T0, cfg=CFG, upbit=up1, coinbase=lambda c: {"BTC", "ETH"}, log=lambda m: None)
            self.assertEqual((r1["new"], r1["events"]), (0, 0))  # staro se samo pamti
            up2 = lambda c: [notice("2", RSR, T0 + 4 * MIN), notice("1", KAIA, T0 - 3 * 86400000)]
            snap = {"RSR": [[T0, 0.00166, 0], [T0 + 3 * MIN, 0.00167, 0]]}
            r2 = L.run(d, ctx(RSR=0.00236), T0 + 6 * MIN, snap=snap, cfg=CFG, upbit=up2, coinbase=lambda c: {"BTC", "ETH", "NEWC"}, log=lambda m: None,
                       spot=lambda s, c: 1.0)
            self.assertEqual(r2["new"], 2)
            ev = {e["source"]: e for e in read_json(os.path.join(d, "listings", "events.json"))}
            u = ev["upbit"]
            self.assertEqual((u["sym"], u["venue"], u["delay_min"]), ("RSR", "hl", 2.0))
            self.assertAlmostEqual(u["move_before_detect_pct"], (0.00236 / 0.00167 - 1) * 100, places=1)  # koliko je cena vec otisla do detekcije
            self.assertTrue(u["cost"] == CFG["cost_pct"]["thin"])  # OI $1,4M = tanko trziste
            self.assertEqual((ev["coinbase"]["sym"], ev["coinbase"]["venue"], ev["coinbase"]["cost"]), ("NEWC", "binance", CFG["cost_pct"]["no_perp"]))
            r3 = L.run(d, ctx(RSR=0.00236), T0 + 9 * MIN, cfg=CFG, upbit=up2, coinbase=lambda c: {"BTC", "ETH", "NEWC"}, log=lambda m: None, spot=lambda s, c: 1.0)
            self.assertEqual(r3["new"], 0)  # isto saopstenje se ne broji dvaput

    def test_outcomes_follow_and_fade_net_of_cost_late_is_missed(self):
        e = L.make_event("upbit", "9", "RSR", T0, T0 + 5 * MIN, ctx(RSR=0.002), None, CFG)
        evs = [e]
        L.update_outcomes(evs, ctx(RSR=0.0021), CFG, T0 + 5 * MIN + 15 * MIN)
        o = e["out"]["15"]
        self.assertAlmostEqual(o["gross"], 5.0)
        self.assertAlmostEqual(o["net"], 5.0 - CFG["cost_pct"]["thin"])
        L.update_outcomes(evs, ctx(RSR=0.0019), CFG, T0 + 5 * MIN + 60 * MIN + 50 * MIN)  # 50 min posle roka: kasni (> 40)
        self.assertEqual(e["out"]["60"], {"missed": True})
        self.assertEqual(e["out"]["15"]["gross"], o["gross"])
        self.assertEqual(e["peak_pct"], 5.0)
        s = L.summarize(evs, CFG)
        self.assertEqual(s["upbit"]["events"], 1)
        self.assertAlmostEqual(s["upbit"]["follow_net_15m"]["mean"] + s["upbit"]["fade_net_15m"]["mean"], -2 * CFG["cost_pct"]["thin"], places=2)

    def test_sources_failing_never_raise(self):
        with tempfile.TemporaryDirectory() as d:
            def boom(c):
                raise OSError("mreza")
            r = L.run(d, ctx(), T0, cfg=CFG, upbit=boom, coinbase=boom, log=lambda m: None)
            self.assertEqual(r["new"], 0)
            self.assertEqual(r["sources"], {"upbit": "OSError mreza", "coinbase": "OSError mreza"})

    def test_jump_radar_runs_listings_only_when_asked_and_survives_its_failure(self):
        jc = J.load_cfg()
        orig = L.run
        try:
            with tempfile.TemporaryDirectory() as d:
                L.run = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("pad"))
                r = J.run(d, cfg=jc, ctx={"A": {"mark": 1.0, "oi_usd": 1e7, "vol24": 1}}, now_ms=T0, log=lambda m: None, listings=True)
                self.assertTrue(r["ok"])
                self.assertEqual(r["listings"], {"error": "RuntimeError"})
                self.assertNotIn("listings", J.run(d, cfg=jc, ctx={}, now_ms=T0 + 5 * MIN, log=lambda m: None))  # podrazumevano ne zove mrezu
        finally:
            L.run = orig


if __name__ == "__main__":
    unittest.main()
