import datetime as dt
import os
import tempfile
import unittest

from lab import insider_study as S


def buy(tk, day, owner, value=60000.0, price=10.0, od=True, ceo=False):
    return {"t": dt.date.fromisoformat(day), "tk": tk, "cik": "1", "owner": owner, "od": od, "ceo": ceo, "value": value, "price": price, "acc": owner + day, "f10b5": False}


def bars(start="2026-01-02", n=80, o0=10.0, step=0.0):
    d0 = dt.date.fromisoformat(start)
    days, o, c = [], [], []
    k = 0
    while len(days) < n:
        d = d0 + dt.timedelta(days=k)
        k += 1
        if d.weekday() >= 5:
            continue
        i = len(days)
        days.append(d.isoformat())
        o.append(o0 + step * i)
        c.append(o0 + step * i)
    return {"d": days, "o": o, "c": c, "ro": list(o)}


class ClusterTests(unittest.TestCase):
    def test_two_buyers_in_window_make_one_event_on_second_filing(self):
        ev = S.find_clusters([buy("AAA", "2026-03-02", "a"), buy("AAA", "2026-03-10", "b")])
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["date"], dt.date(2026, 3, 10))
        self.assertEqual(ev[0]["n_buyers"], 2)
        self.assertEqual(ev[0]["total"], 120000)

    def test_same_buyer_twice_is_not_a_cluster(self):
        self.assertEqual(S.find_clusters([buy("AAA", "2026-03-02", "a"), buy("AAA", "2026-03-10", "a")]), [])

    def test_too_small_total_or_outside_window(self):
        self.assertEqual(S.find_clusters([buy("AAA", "2026-03-02", "a", 20000), buy("AAA", "2026-03-03", "b", 20000)]), [])
        self.assertEqual(S.find_clusters([buy("AAA", "2026-01-02", "a"), buy("AAA", "2026-03-10", "b")]), [])  # vise od 30 dana razmaka

    def test_non_officer_buyers_do_not_count(self):
        self.assertEqual(S.find_clusters([buy("AAA", "2026-03-02", "a", od=False), buy("AAA", "2026-03-03", "b", od=False)]), [])

    def test_quiet_period_after_event(self):
        rows = [buy("AAA", "2026-03-02", "a"), buy("AAA", "2026-03-03", "b"), buy("AAA", "2026-03-20", "c"), buy("AAA", "2026-04-20", "d"), buy("AAA", "2026-06-20", "e")]
        ev = S.find_clusters(rows)
        self.assertEqual([e["date"].isoformat() for e in ev][0], "2026-03-03")
        self.assertTrue(all((b["date"] - a["date"]).days >= S.QUIET_D for a, b in zip(ev, ev[1:])))

    def test_avg_price_is_value_weighted_and_sells_counted(self):
        sells = [{"t": dt.date(2026, 3, 5), "tk": "AAA", "f10b5": False}, {"t": dt.date(2026, 3, 5), "tk": "AAA", "f10b5": True}]
        ev = S.find_clusters([buy("AAA", "2026-03-02", "a", 100000, 10.0), buy("AAA", "2026-03-10", "b", 100000, 20.0)], sells)
        self.assertAlmostEqual(ev[0]["avg_price"], 15.0)
        self.assertEqual(ev[0]["sells_30d"], 1)  # prodaja po planu 10b5-1 se ne racuna


class ReturnTests(unittest.TestCase):
    def test_entry_is_first_trading_day_strictly_after_filing(self):
        b = bars(step=0.1)
        i = S._idx_after(b["d"], "2026-01-02")
        self.assertEqual(b["d"][i], "2026-01-05")  # petak je datum prijave, ulaz ponedeljak

    def test_excess_return_minus_spy_and_cost(self):
        stock, spy = bars(step=0.1), bars(step=0.0)
        ev = {"tk": "AAA", "date": dt.date(2026, 1, 2), "avg_price": 10.0}
        r = S.event_returns(ev, {"AAA": stock}, spy, horizons=(5,))
        i = S._idx_after(stock["d"], "2026-01-02")
        raw = (stock["c"][i + 4] / stock["o"][i] - 1) * 100
        self.assertAlmostEqual(r["raw5"], raw, places=6)
        self.assertAlmostEqual(r["r5"], raw - 0.0 - S.COST_PCT, places=6)
        self.assertAlmostEqual(r["chase"], (stock["o"][i] / 10.0 - 1) * 100, places=6)

    def test_missing_prices_or_short_history(self):
        stock = bars(n=8)
        ev = {"tk": "AAA", "date": dt.date(2026, 1, 2), "avg_price": 10.0}
        self.assertIsNone(S.event_returns({"tk": "ZZZ", "date": dt.date(2026, 1, 2), "avg_price": 1.0}, {}, stock))
        r = S.event_returns(ev, {"AAA": stock}, stock, horizons=(5, 60))
        self.assertIsNone(r["r60"])

    def test_summarize_groups_by_week(self):
        rows = [({"date": dt.date(2026, 1, 5) + dt.timedelta(days=7 * k)}, {"r20": 1.0 + k}) for k in range(6)]
        s = S.summarize(rows, 20)
        self.assertEqual(s["n"], 6)
        self.assertEqual(s["weeks"], 6)
        self.assertAlmostEqual(s["mean"], 3.5)

    def test_placebo_is_centered_for_flat_prices(self):
        stock, spy = bars(n=120), bars(n=120)
        ev = [{"tk": "AAA", "date": dt.date(2026, 1, 2)}] * 5
        sims = S.placebo_mean(ev, {"AAA": stock}, spy, 5, n_sims=20)
        self.assertTrue(all(abs(x + S.COST_PCT) < 1e-9 for x in sims))


class LoadTests(unittest.TestCase):
    def test_load_quarter_from_tsv(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "SUBMISSION.tsv"), "w", encoding="utf-8") as f:
                f.write("ACCESSION_NUMBER\tFILING_DATE\tDOCUMENT_TYPE\tISSUERCIK\tISSUERTRADINGSYMBOL\tAFF10B5ONE\n")
                f.write("A1\t05-MAR-2026\t4\t111\tAAA\t0\n")
                f.write("A2\t06-MAR-2026\t3\t111\tAAA\t0\n")
            with open(os.path.join(d, "REPORTINGOWNER.tsv"), "w", encoding="utf-8") as f:
                f.write("ACCESSION_NUMBER\tRPTOWNERCIK\tRPTOWNER_RELATIONSHIP\tRPTOWNER_TITLE\n")
                f.write("A1\t900\tDirector,Officer\tChief Executive Officer\n")
            with open(os.path.join(d, "NONDERIV_TRANS.tsv"), "w", encoding="utf-8") as f:
                f.write("ACCESSION_NUMBER\tSECURITY_TITLE\tTRANS_CODE\tTRANS_SHARES\tTRANS_PRICEPERSHARE\tTRANS_ACQUIRED_DISP_CD\n")
                f.write("A1\tCommon Stock\tP\t1000\t12.5\tA\n")
                f.write("A1\tStock Option\tP\t1000\t12.5\tA\n")  # opcije se ne racunaju
                f.write("A1\tCommon Stock\tP\t1000\t1.0\tA\n")  # ispod $2
                f.write("A1\tCommon Stock\tS\t10\t12.0\tD\n")
                f.write("A2\tCommon Stock\tP\t1000\t12.5\tA\n")  # nije Form 4
            buys, sells = S.load_quarter(d)
        self.assertEqual(len(buys), 1)
        self.assertEqual(buys[0]["tk"], "AAA")
        self.assertTrue(buys[0]["od"] and buys[0]["ceo"])
        self.assertAlmostEqual(buys[0]["value"], 12500.0)
        self.assertEqual(len(sells), 1)


if __name__ == "__main__":
    unittest.main()
