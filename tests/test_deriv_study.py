import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import binance_backfill as bb, deriv_study as ds, portfolio_sim as ps  # noqa: E402
from lab.indicators import Series  # noqa: E402

DAY = 86400000
T0 = 1_640_995_200_000  # 2022-01-01 UTC

CSV = ("create_time,symbol,sum_open_interest,sum_open_interest_value,count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,"
       "count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
       "2026-09-01 23:55:00,BTCUSDT,110.0,1100.0,1.5,2.5,1.2,0.8\n"
       "2026-09-01 00:00:00,BTCUSDT,100.0,1000.0,1.0,2.0,1.0,1.2\n"
       "2026-09-01 12:00:00,BTCUSDT,105.0,1050.0,1.2,2.2,1.1,1.0\n")


def candles(n, seed, drift=0.0, vol=0.02):
    rnd, c, out = random.Random(seed), 100.0, []
    for i in range(n):
        o = c
        c = c * (1.0 + drift + rnd.gauss(0.0, vol))
        out.append({"t": T0 + i * DAY, "o": o, "h": max(o, c) * 1.001, "l": min(o, c) * 0.999, "c": c, "v": 1.0})
    return out


class BackfillTests(unittest.TestCase):
    def test_symbol_mapping(self):
        self.assertEqual(bb.bn_symbol("BTC"), "BTCUSDT")
        self.assertEqual(bb.bn_symbol("kPEPE"), "1000PEPEUSDT")
        self.assertIsNone(bb.bn_symbol("xyz:AAPL"))

    def test_parse_metrics_uses_last_bar_and_mean_taker(self):
        f = bb.parse_metrics(CSV)
        self.assertEqual((f["oi_val"], f["oi_val_open"], f["oi_amt"], f["bars"]), (1100.0, 1000.0, 110.0, 3))
        self.assertEqual((f["top_acc_ls"], f["top_pos_ls"], f["glob_ls"]), (1.5, 2.5, 1.2))
        self.assertAlmostEqual(f["taker"], 1.0)
        self.assertIsNone(bb.parse_metrics(CSV.splitlines()[0] + "\n"))

    def test_backfill_caches_and_resumes(self):
        calls = []

        def fake(sym, day):
            calls.append((sym, day))
            if day == "2026-09-02":
                return "missing", None
            return "ok", {"oi_val": 1.0, "oi_amt": 1.0, "taker": 1.0}

        old = bb.CACHE
        bb.CACHE = tempfile.mkdtemp()
        try:
            import datetime as dt
            today = dt.date(2026, 10, 1)
            st1 = bb.backfill(["AAAUSDT"], "2026-09-01", "2026-09-03", workers=2, fetch=fake, log=lambda *a: None, today=today)
            self.assertEqual((st1["ok"], st1["missing"], st1["jobs"]), (2, 1, 3))
            self.assertIsNone(bb.load("AAAUSDT")["2026-09-02"])  # staro i nedostaje: pamti se kao null
            n = len(calls)
            st2 = bb.backfill(["AAAUSDT"], "2026-09-01", "2026-09-03", workers=2, fetch=fake, log=lambda *a: None, today=today)
            self.assertEqual((st2["jobs"], len(calls)), (0, n))  # nista se ne vuce ponovo
            self.assertEqual(sorted(bb.series("AAAUSDT")), ["2026-09-01", "2026-09-03"])
            # skoriji dan koji nedostaje (fajl jos nije objavljen) ne sme da se zapamti kao null
            st3 = bb.backfill(["BBBUSDT"], "2026-09-30", "2026-09-30", workers=1, fetch=lambda s, d: ("missing", None), log=lambda *a: None, today=today)
            self.assertEqual(st3["missing"], 1)
            self.assertNotIn("2026-09-30", bb.load("BBBUSDT"))
        finally:
            bb.CACHE = old

    def test_errors_are_counted_not_cached(self):
        old = bb.CACHE
        bb.CACHE = tempfile.mkdtemp()
        try:
            st = bb.backfill(["CCCUSDT"], "2026-01-01", "2026-01-02", workers=1, fetch=lambda s, d: ("error", None), log=lambda *a: None)
            self.assertEqual((st["error"], bb.load("CCCUSDT")), (2, {}))
        finally:
            bb.CACHE = old


def bn_days(n, fn):
    out = {}
    for i in range(n):
        out[ds.day_of(T0 + i * DAY)] = fn(i)
    return out


class FeatureTests(unittest.TestCase):
    def test_oi_change_and_z(self):
        n = 60
        bn = bn_days(n, lambda i: {"oi_amt": 100.0 + i, "top_pos_ls": 2.0 + (0.5 if i == 50 else 0.0) + 0.01 * (i % 3), "top_acc_ls": 1.0, "glob_ls": 1.0,
                                   "taker": 1.0 + 0.1 * (i % 2)})
        times = [T0 + i * DAY for i in range(n)]
        f = ds.feature_table(times, bn)
        self.assertAlmostEqual(f["oi_chg_3"][10], 110.0 / 107.0 - 1.0, places=9)
        self.assertIsNone(f["oi_chg_3"][2])
        self.assertIsNone(f["top_pos_ls_z"][10])  # premalo istorije
        self.assertGreater(f["top_pos_ls_z"][50], 5.0)  # nagli skok je velik z
        self.assertIsNone(f["glob_ls_z"][50])  # konstanta: sd=0

    def test_missing_days_give_none(self):
        bn = {ds.day_of(T0 + i * DAY): {"oi_amt": 1.0 + i, "top_pos_ls": 1.0, "top_acc_ls": 1.0, "glob_ls": 1.0, "taker": 1.0} for i in range(0, 30, 2)}
        f = ds.feature_table([T0 + i * DAY for i in range(30)], bn)
        self.assertIsNone(f["oi_chg_3"][5])  # dan 5 nema podatke


class StudyTests(unittest.TestCase):
    def world(self, n=700, names=14, planted=True):
        members, bnmap = [], {}
        for j in range(names):
            drift = (j - names / 2.0) * 0.0006
            s = Series(candles(n, 500 + j, drift=drift), None, sym="C%d" % j, group="crypto", cls="crypto")
            members.append(s)
            sig = 1.0 + drift * 1000 if planted else random.Random(j).random()
            # OI i taker su nasumicni po (instrument, dan), da izjednaceni skorovi ne poklope slucajno planirani drift po indeksu
            bnmap[s.sym] = bn_days(n, lambda i, sig=sig, j=j: {"oi_amt": 100.0 + random.Random(j * 10000 + i).random() * 5, "oi_val": 1.0, "top_pos_ls": sig,
                                                                "top_acc_ls": sig, "glob_ls": sig, "taker": 1.0 + random.Random(j * 7 + i * 13).random()})
        return {m.sym: m for m in members}, bnmap

    def test_planted_feature_wins_and_reverses(self):
        series, bnmap = self.world()
        members, tables = ds.build_members(series, bnmap)
        self.assertEqual(len(members), 14)
        score = lambda mi, i, t: tables[mi]["glob_ls"][i]  # noqa: E731
        up = ps.metrics(ps.basket_series(members, score, 7, 3, 1, 0.0, 10)[0])
        down = ps.metrics(ps.basket_series(members, score, 7, 3, -1, 0.0, 10)[0])
        self.assertGreater(up["sharpe"], 1.5)
        self.assertLess(down["sharpe"], -1.5)

    def test_run_study_structure(self):
        series, bnmap = self.world(n=500)
        members, tables = ds.build_members(series, bnmap)
        res = ds.run_study(members, tables, T0 + 100 * DAY, n_placebo=3, log=lambda *a: None)
        self.assertEqual(res["members"], 14)
        self.assertTrue(res["results"])
        ts = [r["t"] for r in res["results"]]
        self.assertEqual(ts, sorted(ts, reverse=True))
        self.assertEqual(set(res["placebo_sharpe"]), set(ds.HOLDS))
        best = res["results"][0]
        self.assertIn(best["feature"], ("top_pos_ls", "top_acc_ls", "glob_ls"))
        self.assertEqual(best["sign"], 1)
        self.assertTrue(best["fdr_pass"])
        self.assertIn("osobina", ds.to_markdown(res))

    def test_ols_recovers_coefficients(self):
        rnd = random.Random(3)
        X = [[rnd.gauss(0, 1), rnd.gauss(0, 1)] for _ in range(600)]
        y = [0.5 + 2.0 * a - 1.0 * b + rnd.gauss(0, 0.1) for a, b in X]
        beta, r2, ta = ds.ols(y, X)
        self.assertAlmostEqual(beta[0], 0.5, delta=0.03)
        self.assertAlmostEqual(beta[1], 2.0, delta=0.03)
        self.assertAlmostEqual(beta[2], -1.0, delta=0.03)
        self.assertGreater(r2, 0.99)
        self.assertGreater(ta, 20)

    def test_ols_no_alpha_when_pure_factor(self):
        rnd = random.Random(4)
        X = [[rnd.gauss(0, 1)] for _ in range(800)]
        y = [1.5 * a + rnd.gauss(0, 0.5) for (a,) in X]
        beta, _, ta = ds.ols(y, X)
        self.assertLess(abs(ta), 3.0)

    def test_confound_check_structure(self):
        series, bnmap = self.world(n=500)
        members, tables = ds.build_members(series, bnmap)
        out = ds.confound_check(members, tables, T0 + 150 * DAY, [("glob_ls", 1, 3), ("oi_chg_3", 1, 3)])
        self.assertEqual(len(out), 2)
        for c in out:
            self.assertEqual(set(c["beta"]), {"nizak_vol", "mom30", "mom90"})
            self.assertGreater(c["days"], 100)
        md = ds.to_markdown({"generated_utc": "x", "members": 14, "t_from": "2022-01-01", "cost_pct": 0.23, "k": 5, "tests": 0,
                             "placebo_sharpe": {}, "results": [], "confound": out})
        self.assertIn("poznat faktor", md)

    def test_replication_uses_recorded_criteria(self):
        series, bnmap = self.world(n=520)
        members, tables = ds.build_members(series, bnmap)
        hyp = {"id": "H-T", "feature": "glob_ls", "sign": 1, "H": 3, "k": 3, "cost_pct": 0.0, "replication_sample": "2022-03-01..2023-03-01",
               "pass": {"net_sharpe_min": 0.5, "net_t_min": 1.5, "alpha_after_controls_positive": False}}
        good = ds.replicate(members, tables, hyp)
        self.assertTrue(good["passed"], good)
        self.assertGreater(good["net_sharpe"], 0.5)
        bad = ds.replicate(members, tables, dict(hyp, sign=-1))
        self.assertFalse(bad["passed"])
        self.assertFalse(bad["checks"]["net_sharpe"])
        short = ds.replicate(members, tables, dict(hyp, replication_sample="2022-01-01..2022-01-10"))
        self.assertFalse(short["passed"])  # premalo dana nikad ne prolazi

    def test_random_score_is_deterministic(self):
        f = ds.random_score(3)
        self.assertEqual(f(1, 2, 3), f(1, 2, 3))
        self.assertNotEqual(f(1, 2, 3), ds.random_score(4)(1, 2, 3))

    def test_members_need_enough_history(self):
        series, bnmap = self.world(n=300)
        bnmap["C0"] = dict(list(bnmap["C0"].items())[:50])
        members, _ = ds.build_members(series, bnmap, min_days=200)
        self.assertEqual(len(members), 13)


if __name__ == "__main__":
    unittest.main()
