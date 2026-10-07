import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import collect, collectors2 as C2, featstore, netutil  # noqa: E402

NOW = 1_791_390_000_000  # 2026-10-07 UTC


class CftcTests(unittest.TestCase):
    def setUp(self):
        self._g = netutil.get_json

    def tearDown(self):
        netutil.get_json = self._g

    def test_net_position_percentile_and_week_change(self):
        rows = [{"report_date_as_yyyy_mm_dd": "2026-09-%02dT00:00:00.000" % (29 - 7 * i), "open_interest_all": "1000", "lev_money_positions_long": str(100 + i * 10),
                 "lev_money_positions_short": "300"} for i in range(4)]  # najnovija ima najmanje dugih

        def fake(url, **k):
            assert "%24select" not in url and "$select" in url  # kljucevi upita nisu kodirani
            return rows
        netutil.get_json = fake
        r = C2.collect_cftc(NOW, markets={"btc": (C2.TFF, "BITCOIN - CHICAGO MERCANTILE EXCHANGE")})
        self.assertEqual(r["btc"]["net_pct_oi"], -20.0)
        self.assertEqual(r["btc"]["chg_1w"], -1.0)
        self.assertEqual(r["btc"]["pctl"], 25.0)  # jedan od 4 je <= poslednjeg

    def test_error_everywhere_is_a_source_error(self):
        netutil.get_json = lambda *a, **k: (_ for _ in ()).throw(netutil.NetError("HTTP 500", 500))
        with self.assertRaises(netutil.NetError):
            C2.collect_cftc(NOW, markets={"btc": (C2.TFF, "X")})


class KalshiTests(unittest.TestCase):
    def mk(self, k, bid, ask):
        return {"floor_strike": k, "yes_bid_dollars": bid, "yes_ask_dollars": ask, "last_price_dollars": ask}

    def test_modal_level_and_probabilities(self):
        ms = [self.mk(3.50, "0.99", "1.00"), self.mk(3.75, "0.99", "1.00"), self.mk(4.00, "0.17", "0.18"), self.mk(4.25, "0.00", "0.01")]
        r = C2.fed_summary(ms, NOW)
        self.assertEqual(r["modal_level"], 3.75)
        self.assertAlmostEqual(r["p_up"], 0.175, places=3)
        self.assertAlmostEqual(r["p_down"], 0.005, places=3)
        self.assertAlmostEqual(r["expected_rate"], 3.5 + 0.25 * (0.995 + 0.995 + 0.175 + 0.005), places=3)

    def test_too_few_markets(self):
        self.assertIsNone(C2.fed_summary([self.mk(3.5, "0.9", "1.0")], NOW))

    def test_non_monotone_prices_are_repaired(self):
        ms = [self.mk(3.0, "0.99", "1.0"), self.mk(3.25, "0.20", "0.22"), self.mk(3.5, "0.60", "0.62")]
        r = C2.fed_summary(ms, NOW)
        self.assertLessEqual(r["p_up"] or 0, 1.0)


class BinanceDailyTests(unittest.TestCase):
    def fake(self, sym, day):
        if day.endswith("-20"):  # 20. septembar: star dan koji nedostaje (pamti se kao null)
            return "missing", None
        n = int(day[-2:])
        return "ok", {"oi_amt": 100.0 + n, "oi_val": 1.0, "top_acc_ls": 1.0 + n / 100.0, "top_pos_ls": 2.0, "glob_ls": 1.5, "taker": 1.0, "bars": 288}

    def test_fetch_resume_and_features(self):
        import datetime as dt
        today = dt.date(2026, 10, 7)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bn.json")
            r = C2.collect_binance_daily({"BTC": "BTCUSDT", "kPEPE": "1000PEPEUSDT"}, path, NOW, days=20, workers=2, fetch=self.fake, today=today)
            self.assertEqual(r["asof"], "2026-10-06")
            self.assertEqual(r["fetch"]["error"], 0)
            self.assertAlmostEqual(r["coins"]["BTC"]["oi_chg_1"], (106.0 / 105.0 - 1.0) * 100.0, places=3)
            self.assertEqual(r["agg"]["n_coins"], 2)
            calls = []

            def counting(sym, day):
                calls.append((sym, day))
                return self.fake(sym, day)
            r2 = C2.collect_binance_daily({"BTC": "BTCUSDT", "kPEPE": "1000PEPEUSDT"}, path, NOW, days=20, workers=2, fetch=counting, today=today)
            self.assertEqual(calls, [])  # nista se ne vuce ponovo (stari nedostajuci dan je zapamcen kao null)
            self.assertEqual(r2["agg"]["n_coins"], 2)

    def test_time_budget_defers_remaining_jobs_and_saves_progress(self):
        import datetime as dt
        today = dt.date(2026, 10, 7)
        calls = []

        def slow(sym, day):
            calls.append(day)
            time.sleep(0.02)
            return self.fake(sym, day)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bn.json")
            r = C2.collect_binance_daily({"BTC": "BTCUSDT"}, path, NOW, days=40, workers=1, fetch=slow, today=today, budget_s=0.15, chunk=5)
            self.assertGreater(r["fetch"]["deferred"], 0)
            self.assertLess(len(calls), 40)
            saved = json.load(open(path, encoding="utf-8"))
            self.assertGreaterEqual(len(saved["BTCUSDT"]), 5)  # napredak je sacuvan
            r2 = C2.collect_binance_daily({"BTC": "BTCUSDT"}, path, NOW, days=40, workers=1, fetch=self.fake, today=today)
            self.assertEqual(r2["fetch"]["deferred"], 0)  # sledeci krug nastavlja i zavrsava

    def test_everything_missing_is_an_error(self):
        import datetime as dt
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(netutil.NetError):
                C2.collect_binance_daily({"BTC": "BTCUSDT"}, os.path.join(d, "x.json"), NOW, days=5, fetch=lambda s, dd: ("missing", None), today=dt.date(2026, 10, 7))


class OkxOnchainGdeltTests(unittest.TestCase):
    def setUp(self):
        self._g = netutil.get_json

    def tearDown(self):
        netutil.get_json = self._g

    def test_okx_flow(self):
        def fake(url, **k):
            if "taker-volume" in url:
                return {"data": [["t%d" % i, "100", "90"] for i in range(48)]}
            if "open-interest-volume" in url:
                return {"data": [["t%d" % i, str(1000 - i), "50"] for i in range(30)]}
            return {"data": [{"fundingRate": "0.0001"}]}
        netutil.get_json = fake
        r = C2.collect_okx_flow(("BTC",))
        self.assertAlmostEqual(r["BTC"]["taker_ratio_24h"], 0.9, places=3)
        self.assertAlmostEqual(r["BTC"]["oi_chg_24h_pct"], (1000 / 976 - 1) * 100, places=2)
        self.assertEqual(r["BTC"]["funding_8h"], 0.0001)

    def test_okx_total_failure_raises(self):
        netutil.get_json = lambda *a, **k: (_ for _ in ()).throw(netutil.NetError("HTTP 403", 403))
        with self.assertRaises(netutil.NetError):
            C2.collect_okx_flow(("BTC",))

    def test_onchain_drops_incomplete_today_and_sorts(self):
        rows = [{"time": "2026-10-%02dT00:00:00.000000000Z" % (7 - i), "AdrActCnt": str(600000 + i), "TxCnt": "700000"} for i in range(30)]  # od najnovijeg ka starijem
        netutil.get_json = lambda *a, **k: {"data": rows}
        r = C2.collect_onchain(NOW)
        self.assertEqual(r["asof"], "2026-10-06")  # 7. oktobar je tekuci dan, izbacen
        self.assertIsNotNone(r["btc_adr_z"])

    def test_gdelt_best_effort(self):
        def fake(url, **k):
            if "oil" in url:
                return {"timeline": [{"data": [{"value": -2.0}] * 100 + [{"value": -3.0}] * 100}]}
            raise netutil.NetError("HTTP 429", 429)
        netutil.get_json = fake
        r = C2.collect_gdelt(NOW, queries={"oil": "oil prices", "war": "war"}, pause=0)
        self.assertAlmostEqual(r["oil"]["tone_chg"], -0.9615, places=2)
        self.assertIsNone(r["war"])
        netutil.get_json = lambda *a, **k: (_ for _ in ()).throw(netutil.NetError("HTTP 429", 429))
        with self.assertRaises(netutil.NetError):
            C2.collect_gdelt(NOW, queries={"oil": "x"}, pause=0)


class FeatStoreTests(unittest.TestCase):
    def files(self):
        return {
            "macro": {"data": {"yahoo": {"VIX": {"last": 16.0, "chg_1d_pct": 1.0, "chg_5d_pct": 2.0, "chg_20d_pct": -3.0}, "prinos 10g": {"last": 4.2, "chg_1d_pct": 0.1, "chg_5d_pct": 0.2, "chg_20d_pct": 0.3}},
                               "fred": {"WALCL": {"name": "bilans", "last": 6.5e6, "chg_5": 1.0}, "WTREGEN": {"name": "tga", "last": 0.8e6, "chg_5": 1.0},
                                        "RRPONTSYD": {"name": "rrp", "last": 100.0, "chg_5": 1.0}}}},
            "sentiment": {"data": {"fear_greed": {"avg7": 70.0, "avg30": 60.0}, "crypto_global": {"btc_dominance": 59.0, "mcap_chg_24h_pct": -1.0},
                                   "stablecoins": {"total_usd": 3.1e11, "chg_30d_pct": 1.2}, "wiki_attention": {"Bitcoin": {"last": 100, "z": -0.4}}}},
            "derivs": {"data": {"deribit": {"dvol_btc": {"chg_24h": 1.0}}, "okx_lsr": {"BTC": {"last": 1.5, "chg_24h": 0.1}},
                                "coinalyze": {"BTC": {"oi_usd": 1.5e10, "funding_mean": -0.001, "liq_long_24h": 1e8, "liq_short_24h": 3e6, "lsr_last": 2.0}, "ETH": {"error": "HTTP 429"}}}},
            "market": {"data": {"BTC": {"ctx": {"mark": 100.0, "funding_h": 1e-5, "oi_usd": 3e9, "premium": 0.0001, "vol24": 1e9}, "book": {"spread_bps": 0.1, "imb_1pct": 0.2}, "fund_xv": None},
                                "ETH": {"ctx": {"mark": 10.0, "funding_h": -1e-5, "oi_usd": 1e9, "premium": -0.0001, "vol24": 5e8}, "book": {"spread_bps": 0.2, "imb_1pct": -0.1}, "fund_xv": None},
                                "xyz:AMD": {"ctx": {"mark": 600.0, "funding_h": 0.0, "oi_usd": 2e7, "premium": 0.0, "vol24": 1e7}, "book": {"spread_bps": 1.0, "imb_1pct": 0.0}}}},
            "calendar": {"data": {"events": [{"ts": "2026-10-07T18:00:00Z", "impact": "High"}, {"ts": "2026-10-07T20:00:00Z", "impact": "Medium"}],
                                  "earnings": {"xyz:TSLA": {"date": "2026-10-20"}}}},
            "cftc": {"data": {"btc": {"net_pct_oi": -35.0, "pctl": 92.0, "chg_1w": 0.6}}},
            "llama": {"data": {"dex": {"total24h": 9.8e9, "chg_1d": 21.0, "chg_7d": -16.0, "chg_1m": -9.0, "hyperliquid_24h": 1.2e8}, "fees": {"total24h": 7.4e7, "chg_7d": -9.0, "chg_1m": -14.0}}},
            "kalshi": {"data": {"expected_rate": 4.04, "p_up": 0.17, "p_down": 0.005, "days_to_meeting": 21.0}},
            "bn_daily": {"data": {"agg": {"glob_ls_med": 1.7, "oi_chg_7_med": 2.5}, "coins": {"BTC": {"oi_chg_7": 3.4, "glob_ls": 1.1}}}},
            "onchain": {"data": {"btc_adr_z": 0.0, "btc_tx_z": 0.7, "btc_adr_chg_7d_pct": -6.4}},
        }

    def test_flatten_covers_every_source_and_skips_missing(self):
        f, g = featstore.flatten(self.files(), {"vix": 16.0, "fear_greed": 71, "btc_smart_net_share": -0.4, "dvol_btc": None}, NOW)
        for k in ("vix", "fear_greed", "y_vix", "y_vix_c5", "y_prinos_10g", "f_walcl", "f_net_liq_tn", "fg_avg7", "btc_dom", "stable_total_tn", "wiki_bitcoin_z", "dvol_btc_c24",
                  "okx_lsr_btc", "cz_btc_oi_usd", "hl_fund_mean", "hl_oi_total_b", "hl_imb_btc", "cal_hrs_to_high", "cal_n_high_24h", "earn_n_14d", "earn_days_min", "cftc_btc_net",
                  "cftc_btc_pctl", "dex_vol_b", "dex_c7", "fees_m", "fed_exp_rate", "fed_p_up", "bn_glob_ls_med", "bn_btc_oi_chg_7", "oc_btc_tx_z", "t_hour", "t_dow"):
            self.assertIn(k, f, k)
            self.assertIn(k, g)
        self.assertNotIn("dvol_btc", f)  # None ne ulazi
        self.assertFalse(any(k.startswith("cz_eth_") for k in f))  # greska izvora: nema izmisljenih vrednosti
        self.assertAlmostEqual(f["f_net_liq_tn"], (6.5e6 - 0.8e6) / 1e6 - 100.0 / 1e3, places=6)
        self.assertAlmostEqual(f["hl_fund_pos_share"], 0.5)
        self.assertNotIn("xyz_amd", json.dumps(list(f)))  # akcije nisu u kripto agregatima
        self.assertEqual(f["earn_n_14d"], 1)
        self.assertEqual(f["cal_n_high_24h"], 1)
        self.assertTrue(all(isinstance(v, float) or isinstance(v, int) for v in f.values()))
        self.assertGreater(len(f), 60)

    def test_instrument_features(self):
        r = featstore.instrument_features(self.files()["market"]["data"])
        self.assertEqual(set(r), {"BTC", "ETH", "xyz:AMD"})
        self.assertIn("imb_1pct", r["BTC"])
        self.assertEqual(featstore.instrument_features(None), {})


class BriefingExtraTests(unittest.TestCase):
    def test_briefing_carries_extra_and_evidence_and_stays_small(self):
        files = {"kalshi": {"data": {"event": "E", "days_to_meeting": 20.0, "modal_level": 3.75, "p_up": 0.17, "p_down": 0.0, "expected_rate": 4.04}},
                 "cftc": {"data": {"btc": {"pctl": 90.0}, "gold": None}}, "llama": {"data": {"dex": {"chg_7d": -16.0}}}}
        ev = {"tests": 120, "fdr_pass": 0, "findings": [{"strategy": "s", "var": "v", "t": 2.6}] * 20}
        b = collect.build_briefing(files, {}, NOW, n_features=259, evidence=ev)
        self.assertEqual(b["n_features"], 259)
        self.assertEqual(b["extra"]["fed"]["modal_level"], 3.75)
        self.assertEqual(b["extra"]["cftc_pctl_3y"], {"btc": 90.0})
        self.assertEqual(b["evidence"]["tests"], 120)
        self.assertLess(len(json.dumps(b).encode()), collect.BRIEFING_MAX_BYTES)
        self.assertIsNone(collect.build_briefing({}, {}, NOW)["evidence"])


class CompactHistoryTests(unittest.TestCase):
    def test_hourly_recent_daily_old(self):
        hour = 3600000
        now = (NOW // hour) * hour
        rows = [{"t": now - i * hour, "x": i} for i in range(24 * 20)]
        out = collect.compact_history(rows, now)
        recent = [r for r in out if r["t"] >= now - 24 * 7 * hour]
        old = [r for r in out if r["t"] < now - 24 * 7 * hour]
        self.assertEqual(len(recent), 24 * 7 + 1)
        self.assertLessEqual(len(old), 14)  # jedan red dnevno
        self.assertEqual([r["t"] for r in out], sorted(r["t"] for r in out))


if __name__ == "__main__":
    unittest.main()
