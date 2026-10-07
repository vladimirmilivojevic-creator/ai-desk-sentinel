"""Testovi kolektora i briefing-a. Svi odgovori su IZMISLJENI, bez mreze."""
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import backtest, collect, collectors as C, netutil  # noqa: E402

NOW = int(time.time() * 1000)


def book(mid=100.0, spread=0.02, depth_per_level=1000.0, n=10):
    bids = [{"px": str(mid - spread / 2 - i * 0.01), "sz": str(depth_per_level / mid), "n": 1} for i in range(n)]
    asks = [{"px": str(mid + spread / 2 + i * 0.01), "sz": str(depth_per_level / mid), "n": 1} for i in range(n)]
    return {"coin": "X", "levels": [bids, asks]}


class BookTests(unittest.TestCase):
    def test_spread_slippage_and_depth(self):
        m = C.book_metrics(book())
        self.assertAlmostEqual(m["spread_bps"], 2.0, places=1)  # 0,02 na 100 = 2 bps
        self.assertLess(m["slip_buy_bps"]["120"], 3.0)
        self.assertGreater(m["slip_buy_bps"]["120"], 0)
        self.assertLess(m["slip_sell_bps"]["120"], 3.0)
        self.assertGreater(m["depth_usd_1pct"], 5000)

    def test_shallow_book_gives_none_not_a_guess(self):
        m = C.book_metrics(book(depth_per_level=10.0, n=3))
        self.assertIsNone(m["slip_buy_bps"]["500"])
        self.assertIsNone(m["slip_buy_bps"]["2500"])

    def test_empty_book(self):
        self.assertIsNone(C.book_metrics({"levels": [[], []]}))


class ParseTests(unittest.TestCase):
    def setUp(self):
        self._gj, self._gt, self._pj, self._hp = netutil.get_json, netutil.get_text, netutil.post_json, C.hl_post

    def tearDown(self):
        netutil.get_json, netutil.get_text, netutil.post_json, C.hl_post = self._gj, self._gt, self._pj, self._hp

    def test_predicted_fundings_normalised_per_hour(self):
        C.hl_post = lambda body, **k: [["BTC", [["BinPerp", {"fundingRate": "0.0004", "fundingIntervalHours": 4}],
                                                ["HlPerp", {"fundingRate": "0.0000125", "fundingIntervalHours": 1}],
                                                ["BybPerp", {"fundingRate": "0.0008", "fundingIntervalHours": 8}]]],
                                       ["ZZZ", [["HlPerp", {"fundingRate": "0.1", "fundingIntervalHours": 1}]]]]
        r = C.predicted_fundings(["BTC"])
        self.assertAlmostEqual(r["BTC"]["bin_h"], 0.0001)
        self.assertAlmostEqual(r["BTC"]["byb_h"], 0.0001)
        self.assertAlmostEqual(r["BTC"]["bin_minus_hl_h"], 0.0001 - 0.0000125)
        self.assertNotIn("ZZZ", r)

    def test_contexts_and_liquid_universe(self):
        def fake(body, **k):
            names = ["BTC", "DEAD", "ALT"] if not body.get("dex") else ["xyz:NVDA"]
            ctx = {"BTC": {"markPx": "100", "funding": "0.00001", "openInterest": "1000000", "premium": "0.0001", "dayNtlVlm": "5e8"},
                   "DEAD": {"markPx": "1", "funding": "0", "openInterest": "1", "premium": "0", "dayNtlVlm": "1"},
                   "ALT": {"markPx": "2", "funding": "0", "openInterest": "10", "premium": "0", "dayNtlVlm": "100"},
                   "xyz:NVDA": {"markPx": "200", "funding": "0.00002", "openInterest": "500000", "premium": "0", "dayNtlVlm": "3e6"}}
            uni = [{"name": n, "isDelisted": n == "DEAD"} for n in names]
            return {"universe": uni}, [ctx[n] for n in names]
        C.hl_post = fake
        ctx = C.hl_contexts()
        self.assertNotIn("DEAD", ctx)
        self.assertEqual(ctx["BTC"]["oi_usd"], 100_000_000)
        liq = C.liquid_universe(ctx)
        self.assertEqual([r["sym"] for r in liq], ["BTC", "xyz:NVDA"])

    def test_deribit_and_okx(self):
        def fake(url, **k):
            if "volatility_index" in url:
                return {"result": {"data": [[1, 0, 0, 0, 40.0 + i * 0.1] for i in range(30)]}}
            if "book_summary" in url:
                return {"result": [{"instrument_name": "BTC-1-100-P", "open_interest": 30.0}, {"instrument_name": "BTC-1-100-C", "open_interest": 60.0}]}
            return {"data": [["t", "1.5"], ["t", "1.4"]] + [["t", "1.0"]] * 30}
        netutil.get_json = fake
        d = C.collect_deribit(NOW)
        self.assertAlmostEqual(d["dvol_btc"]["last"], 42.9, places=1)
        self.assertAlmostEqual(d["btc_put_call_oi"], 0.5)
        o = C.collect_okx_lsr(("BTC",))
        self.assertEqual(o["BTC"]["last"], 1.5)

    def test_fred_and_yahoo_parse_and_failures_become_none(self):
        netutil.get_text = lambda url, **k: "observation_date,X\n2026-01-01,1.0\n2026-01-02,.\n2026-01-03,2.0\n"
        f = C.collect_fred({"X": "test"})
        self.assertEqual(f["X"]["last"], 2.0)
        self.assertEqual(f["X"]["chg_1"], 1.0)
        netutil.get_text = lambda url, **k: (_ for _ in ()).throw(netutil.NetError("HTTP 429", 429))
        self.assertIsNone(C.collect_fred({"X": "test"})["X"])
        netutil.get_json = lambda url, **k: {"chart": {"result": [{"indicators": {"quote": [{"close": [10.0, None, 11.0, 12.0]}]}}]}}
        y = C.collect_yahoo({"^VIX": "VIX"}, pause=0)
        self.assertEqual(y["VIX"]["last"], 12.0)
        self.assertAlmostEqual(y["VIX"]["chg_1d_pct"], round((12 / 11 - 1) * 100, 3))
        calls = []

        def boom(url, **k):
            calls.append(url)
            raise netutil.NetError("HTTP 429", 429)
        netutil.get_json = boom
        r = C.collect_yahoo({"^A": "A", "^B": "B", "^C": "C", "^D": "D", "^E": "E"}, pause=0)
        self.assertTrue(all(v is None for v in r.values()))
        self.assertEqual(len(calls), 3)  # prekidac: posle 3 uzastopna neuspeha ne zovemo ostale

    def test_calendar_filters_by_impact_window_and_maps_earnings(self):
        import datetime as dt
        soon = dt.datetime.fromtimestamp(NOW / 1000 + 3600, dt.timezone.utc).isoformat()
        far = dt.datetime.fromtimestamp(NOW / 1000 + 10 * 86400, dt.timezone.utc).isoformat()

        def fake(url, **k):
            if "faireconomy" in url:
                return [{"title": "CPI", "country": "USD", "date": soon, "impact": "High", "forecast": "0.3%", "previous": "0.2%"},
                        {"title": "Lunch", "country": "USD", "date": soon, "impact": "Low"},
                        {"title": "Later", "country": "USD", "date": far, "impact": "High"}]
            return {"earningsCalendar": [{"symbol": "NVDA", "date": "2026-10-10", "hour": "amc", "epsEstimate": 1.2}, {"symbol": "ZZZ", "date": "2026-10-10"}]}
        netutil.get_json = fake
        r = C.collect_calendar(NOW, ["xyz:NVDA", "BTC"], finnhub_key="K")
        self.assertEqual([e["title"] for e in r["events"]], ["CPI"])
        self.assertEqual(r["earnings"]["xyz:NVDA"]["source"], "finnhub")
        self.assertNotIn("ZZZ", json.dumps(r))
        self.assertNotIn("\"K\"", json.dumps(r))

    def test_smart_money_aggregates_and_hides_addresses(self):
        rows = [{"ethAddress": "0xaaa", "accountValue": "1000000", "windowPerformances": [["week", {"pnl": "10", "roi": "0.1"}], ["month", {"pnl": "20", "roi": "0.3"}]]},
                {"ethAddress": "0xbbb", "accountValue": "900000", "windowPerformances": [["week", {"pnl": "10", "roi": "0.1"}], ["month", {"pnl": "20", "roi": "0.2"}]]},
                {"ethAddress": "0xccc", "accountValue": "10", "windowPerformances": [["week", {"pnl": "10", "roi": "9"}], ["month", {"pnl": "20", "roi": "9"}]]},
                {"ethAddress": "0xddd", "accountValue": "900000", "windowPerformances": [["week", {"pnl": "-1", "roi": "0.1"}], ["month", {"pnl": "20", "roi": "0.5"}]]}]
        netutil.get_text = lambda url, **k: json.dumps({"leaderboardRows": rows})

        def fake(body, **k):
            if body.get("dex"):
                return {"assetPositions": []}
            pos = {"0xaaa": [("BTC", "2", "100")], "0xbbb": [("BTC", "-1", "100"), ("ETH", "5", "10")]}[body["user"]]
            return {"assetPositions": [{"position": {"coin": c, "szi": s, "markPx": m}} for c, s, m in pos]}
        C.hl_post = fake
        r = C.collect_smart_money(["BTC"], n=10)
        self.assertEqual(r["wallets_selected"], 2)  # mali nalog i nalog sa gubitkom nedelje su izbaceni
        self.assertEqual(r["coins"]["BTC"]["net_usd"], 100.0)
        self.assertEqual(r["coins"]["BTC"]["wallets"], 2)
        self.assertNotIn("0xaaa", json.dumps(r))

    def test_coinalyze_needs_key_and_survives_shape_errors(self):
        with self.assertRaises(netutil.NetError):
            C.collect_coinalyze(None, NOW)

        def fake(url, **k):
            if "future-markets" in url:
                return [{"symbol": "BTCUSDT_PERP.A", "base_asset": "BTC", "quote_asset": "USDT", "is_perpetual": True}]
            if "open-interest" in url:
                return [{"symbol": "BTCUSDT_PERP.A", "value": 1000}]
            if "funding-rate" in url:
                return [{"symbol": "BTCUSDT_PERP.A", "value": 0.0001}]
            raise netutil.NetError("HTTP 500", 500)
        netutil.get_json = fake
        r = C.collect_coinalyze("KEY", NOW, coins=("BTC", "ETH"), pause=0)
        self.assertEqual(r["BTC"]["oi_usd"], 1000)
        self.assertIn("error", r["BTC"])
        self.assertIsNone(r["ETH"])


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = {"universe": [{"sym": "BTC", "hl": "BTC", "group": "crypto", "cls": "crypto"},
                                 {"sym": "xyz:NVDA", "hl": "xyz:NVDA", "group": "stock", "cls": "stock"}]}
        self._lc, self._saved = backtest.load_config, {}
        backtest.load_config = lambda: (self.cfg, [])
        for n in ("hl_contexts", "collect_market", "collect_deribit", "collect_okx_lsr", "collect_coinalyze", "collect_yahoo", "collect_fred",
                  "collect_sentiment", "collect_calendar", "collect_smart_money"):
            self._saved[n] = getattr(C, n)
        self.calls = {}
        ctx = {"BTC": {"mark": 100.0, "funding_h": 0.00001, "oi_usd": 5e8, "premium": 0.0, "vol24": 1e9},
               "xyz:NVDA": {"mark": 200.0, "funding_h": 0.0, "oi_usd": 2e7, "premium": 0.0, "vol24": 5e6}}

        def counted(name, val):
            def f(*a, **k):
                self.calls[name] = self.calls.get(name, 0) + 1
                if isinstance(val, Exception):
                    raise val
                return val
            return f
        C.hl_contexts = counted("ctx", ctx)
        C.collect_market = lambda syms, c: (self.calls.__setitem__("market", self.calls.get("market", 0) + 1) or
                                            {s: {"ctx": c.get(s), "book": {"spread_bps": 1.0, "slip_buy_bps": {"120": 0.5}}, "fund_xv": None} for s in syms})
        C.collect_deribit = counted("deribit", {"dvol_btc": {"last": 45.0}, "btc_put_call_oi": 0.6})
        C.collect_okx_lsr = counted("okx", {"BTC": {"last": 1.4}})
        C.collect_coinalyze = counted("coinalyze", netutil.NetError("nema kljuca"))
        C.collect_yahoo = counted("yahoo", {"VIX": {"last": 18.0}, "VIX3M": {"last": 20.0}})
        C.collect_fred = counted("fred", {"BAMLH0A0HYM2": {"last": 3.1, "chg_5": 0.05}})
        C.collect_sentiment = counted("sent", {"fear_greed": {"last": 60}})
        C.collect_calendar = counted("cal", {"events": [], "earnings": {}})
        C.collect_smart_money = counted("smart", {"coins": {"BTC": {"net_share": 0.2}}})

    def tearDown(self):
        backtest.load_config = self._lc
        for n, f in self._saved.items():
            setattr(C, n, f)
        self.tmp.cleanup()

    def test_full_run_writes_files_briefing_and_health(self):
        r = collect.run(self.tmp.name, now_ms=NOW, log=lambda *_: None, env={})
        self.assertTrue(r["ok"])
        d = os.path.join(self.tmp.name, "data")
        for f in ("market.json", "derivs.json", "macro.json", "sentiment.json", "calendar.json", "smart_money.json", "universe.json",
                  "health.json", "history.json", "briefing.json", "meta.json"):
            self.assertTrue(os.path.exists(os.path.join(d, f)), f)
        b = json.load(open(os.path.join(d, "briefing.json"), encoding="utf-8"))
        self.assertLess(len(json.dumps(b).encode()), collect.BRIEFING_MAX_BYTES)
        self.assertEqual(b["scalars"]["vix"], 18.0)
        self.assertIn(b["regime"]["label"], ("risk_on", "neutral", "risk_off"))
        hist = json.load(open(os.path.join(d, "history.json"), encoding="utf-8"))
        self.assertEqual(hist[-1]["m"]["BTC"], 100.0)  # cene univerzuma za ocenjivanje prognoza
        h = json.load(open(os.path.join(d, "health.json"), encoding="utf-8"))
        self.assertIn("derivs_coinalyze", h)
        self.assertIsNotNone(h["derivs_coinalyze"]["last_error"])  # nema kljuca: zapisano, ne izmisljeno
        self.assertIsNone(h["market"]["last_error"])

    def test_same_hour_is_skipped_but_force_runs_again(self):
        collect.run(self.tmp.name, now_ms=NOW, log=lambda *_: None, env={})
        n = self.calls["market"]
        collect.run(self.tmp.name, now_ms=NOW + 60_000, log=lambda *_: None, env={})
        self.assertEqual(self.calls["market"], n)
        collect.run(self.tmp.name, now_ms=NOW + 3_700_000, log=lambda *_: None, env={})
        self.assertEqual(self.calls["market"], n + 1)
        collect.run(self.tmp.name, now_ms=NOW + 3_700_000, force=True, log=lambda *_: None, env={})
        self.assertEqual(self.calls["market"], n + 2)

    def test_one_failing_source_keeps_old_file_and_others_work(self):
        collect.run(self.tmp.name, now_ms=NOW, log=lambda *_: None, env={})
        C.collect_yahoo = lambda *a, **k: (_ for _ in ()).throw(netutil.NetError("HTTP 429", 429))
        r = collect.run(self.tmp.name, now_ms=NOW + 3_700_000, log=lambda *_: None, env={})
        self.assertTrue(r["ok"])
        self.assertIn("macro_yahoo", r["failing"])
        d = os.path.join(self.tmp.name, "data")
        b = json.load(open(os.path.join(d, "briefing.json"), encoding="utf-8"))
        self.assertEqual(b["scalars"]["vix"], 18.0)  # staro, ne izmisljeno
        self.assertIn("macro_yahoo", b["source_health_failing"])

    def test_zscores_need_history_and_flag_extremes(self):
        hist = [{"t": i, "vix": 15.0 + (i % 3) * 0.1} for i in range(60)]
        z = collect.zscores({"vix": 30.0, "dxy": None, "new": 1.0}, hist)
        self.assertGreater(z["vix"], 10)
        self.assertNotIn("dxy", z)
        self.assertNotIn("new", z)
        self.assertEqual(collect.zscores({"vix": 30.0}, hist[:10]), {})

    def test_regime_labels(self):
        calm = {"macro": {"data": {"yahoo": {"VIX": {"last": 14}, "VIX3M": {"last": 17}}, "fred": {}}}, "sentiment": {"data": {}}}
        self.assertEqual(collect.regime(calm)["label"], "risk_on")
        bad = {"macro": {"data": {"yahoo": {"VIX": {"last": 32}, "VIX3M": {"last": 28}}, "fred": {"BAMLH0A0HYM2": {"chg_5": 0.6}}}}, "sentiment": {"data": {}}}
        self.assertEqual(collect.regime(bad)["label"], "risk_off")

    def test_main_never_raises(self):
        backtest.load_config = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        sys.argv = ["lab.collect", "--state", self.tmp.name]
        self.assertEqual(collect.main(), 0)


if __name__ == "__main__":
    unittest.main()
