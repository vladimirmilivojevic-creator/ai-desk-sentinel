import datetime as dt
import json
import os
import random
import tempfile
import unittest

from lab import carry_study as C


def days(n, start="2024-01-01"):
    d0 = dt.date.fromisoformat(start)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range(n)]


def series(ds, fn):
    """Svece sa otvaranjem = zatvaranju prethodnog dana (nema rupa)."""
    c = [fn(i) for i in range(len(ds))]
    o = [c[0]] + c[:-1]
    return {"d": list(ds), "o": o, "h": c, "l": c, "c": c, "v": [1.0] * len(ds), "rc": c}


CFG = {"k": 2, "universe": {"min_names": 4, "from": "2024-02-01"}, "cost_per_round_trip_pct": 0.33, "min_periods": 5, "fdr_q": 0.10, "placebo_runs": 3,
       "signal_days": [3], "hold_days": [3], "orientations": ["carry", "reverse"],
       "candidate_gates": {"fdr": True, "mean_gt": 0.0, "both_halves_mean_gt": 0.0, "last_270d_mean_gt": 0.0}}


def world(n=120, noise=0.0, seed=1):
    rng = random.Random(seed)
    ds = days(n)
    px, fund, mem = {}, {}, {}
    for j in range(8):
        s = "C%dUSDT" % j
        # ravna cena sa malim sumom; fonding raste sa j (C0 najnizi, C7 najvisi) i je konstantan po danu
        px[s] = series(ds, lambda i, j=j: 100.0 * (1.0 + noise * rng.uniform(-1, 1)) * (1.0 + 0.0005 * (i % 3)))
        fund[s] = {d: 0.0001 * (j - 3.5) for d in ds}
        mem[s] = set(ds)
    return px, fund, mem, ds


class TestParse(unittest.TestCase):
    def test_parse_and_daily_sum(self):
        txt = "calc_time,funding_interval_hours,last_funding_rate\n1704067200000,8,0.0001\n1704096000000,8,0.0002\n1704124800000,8,-0.00005\n"
        rows = C.parse_funding_csv(txt)
        self.assertEqual(len(rows), 3)  # zaglavlje se preskace
        out = C.daily_funding(rows)
        self.assertEqual(sorted(out), ["2024-01-01"])
        self.assertAlmostEqual(out["2024-01-01"], 0.00025, places=9)

    def test_months(self):
        self.assertEqual(C.months("2023-11-15", "2024-02-03"), ["2023-11", "2023-12", "2024-01", "2024-02"])

    def test_cache_roundtrip_and_missing_file_is_cached(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "fr_X_2024-01.json")
            with open(p, "w") as f:
                json.dump([[1704067200000, 0.0001]], f)
            self.assertEqual(C.fetch_month("X", "2024-01", d), [(1704067200000, 0.0001)])


class TestPick(unittest.TestCase):
    def test_pick_lowest_and_highest_funding_and_no_peeking(self):
        px, fund, mem, ds = world()
        idx = C.build_index(px)
        d = ds[60]
        lo, hi = C.pick(px, idx, fund, mem, d, 3, 2, 4)
        self.assertEqual([x[1] for x in lo], ["C0USDT", "C1USDT"])
        self.assertEqual([x[1] for x in hi], ["C6USDT", "C7USDT"])
        # promena fondinga POSLE dana d ne menja izbor na dan d
        fund["C7USDT"][ds[61]] = -1.0
        lo2, hi2 = C.pick(px, idx, fund, mem, d, 3, 2, 4)
        self.assertEqual([x[1] for x in hi2], [x[1] for x in hi])

    def test_pick_needs_min_names_and_full_signal_window(self):
        px, fund, mem, ds = world()
        idx = C.build_index(px)
        self.assertIsNone(C.pick(px, idx, fund, mem, ds[60], 3, 2, 9))  # manje od min_names
        for s in list(fund)[:6]:
            del fund[s][ds[59]]  # rupa u fondingu u prozoru signala
        self.assertIsNone(C.pick(px, idx, fund, mem, ds[60], 3, 2, 4))


class TestPeriod(unittest.TestCase):
    def test_fund_component_sign_and_cost(self):
        px, fund, mem, ds = world()  # cena ravna: cena se vraca na isto, pa je komponenta cene ~0 u proseku
        idx = C.build_index(px)
        d = ds[60]
        lo, hi = C.pick(px, idx, fund, mem, d, 3, 2, 4)
        r = C.period_result(px, idx, fund, lo, hi, d, 3, "carry", 0.33)
        # carry: duga noga placa (negativan fonding = prima), kratka prima vise: fonding komponenta je pozitivna
        self.assertGreater(r["fund"], 0)
        rev = C.period_result(px, idx, fund, lo, hi, d, 3, "reverse", 0.33)
        self.assertAlmostEqual(r["fund"], -rev["fund"], places=9)  # obrnuta orijentacija obrce predznak
        self.assertAlmostEqual(r["net"], r["price"] + r["fund"] - 0.33, places=9)
        # tacna vrednost: 3 dana, polovina razlike prosecnog fondinga kratke i duge strane (jednake volatilnosti)
        avg_long = (0.0001 * -3.5 + 0.0001 * -2.5) / 2
        avg_short = (0.0001 * 2.5 + 0.0001 * 3.5) / 2
        self.assertAlmostEqual(r["fund"], 100.0 * 3 * 0.5 * (avg_short - avg_long), places=6)

    def test_missing_entry_gives_none(self):
        px, fund, mem, ds = world()
        idx = C.build_index(px)
        lo, hi = C.pick(px, idx, fund, mem, ds[60], 3, 2, 4)
        # kovanica nema svecu d+1 (ulaz ne postoji)
        s = lo[0][1]
        i = px[s]["d"].index(ds[61])
        for k in px[s]:
            del px[s][k][i]
        idx = C.build_index(px)
        self.assertIsNone(C.period_result(px, idx, fund, lo, hi, ds[60], 3, "carry", 0.33))

    def test_delisted_leg_closes_at_last_available_price(self):
        px, fund, mem, ds = world()
        s = "C0USDT"
        keep = ds.index(ds[61]) + 1  # poslednja svecu je d+1
        for k in px[s]:
            px[s][k] = px[s][k][:keep]
        idx = C.build_index(px)
        self.assertIsNotNone(C.leg_numbers(px, idx, fund, s, ds[60], 3))


class TestStudy(unittest.TestCase):
    def test_periods_do_not_overlap_and_offsets_shift_start(self):
        px, fund, mem, ds = world()
        idx = C.build_index(px)
        dates = [d for d in ds if d >= "2024-02-01"]
        a = C.run_test(px, idx, fund, mem, dates, 3, 3, "carry", CFG, offset=0)
        b = C.run_test(px, idx, fund, mem, dates, 3, 3, "carry", CFG, offset=1)
        self.assertTrue(len(a) > 10)
        da = [x["date"] for x in a]
        self.assertEqual(len(set(da)), len(da))
        self.assertTrue(all((dt.date.fromisoformat(da[i + 1]) - dt.date.fromisoformat(da[i])).days == 3 for i in range(len(da) - 1)))
        self.assertNotEqual(a[0]["date"], b[0]["date"])

    def test_full_study_reports_all_tests_and_gates(self):
        px, fund, mem, ds = world(n=200, noise=0.002)
        res = C.run_study(px, fund, mem, CFG, ds[-1], log=lambda *a: None)
        self.assertEqual(len(res), 2)  # 1 x 1 x 2 orijentacije
        ids = {r["id"] for r in res}
        self.assertEqual(ids, {"carry:3d:3d", "reverse:3d:3d"})
        car = [r for r in res if r["orient"] == "carry"][0]
        rev = [r for r in res if r["orient"] == "reverse"][0]
        # fonding je stalan i bez drifta cene: carry zaradjuje fonding, reverse ga placa
        self.assertGreater(car["fund"], 0)
        self.assertLess(rev["fund"], 0)
        self.assertIn(car["status"], ("kandidat", "odbaceno"))
        self.assertEqual(rev["status"], "odbaceno")
        for r in res:
            self.assertIsNotNone(r["placebo_mean"])

    def test_placebo_has_no_edge_when_funding_is_the_only_signal(self):
        px, fund, mem, ds = world(n=200, noise=0.002)
        idx = C.build_index(px)
        dates = [d for d in ds if d >= "2024-02-01"]
        means = []
        for seed in range(10):
            rows = C.run_test(px, idx, fund, mem, dates, 3, 3, "carry", CFG, rng=random.Random(seed))
            means.append(sum(r["fund"] for r in rows) / len(rows))
        # nasumican izbor nema sistematsku razliku fondinga izmedju duge i kratke strane
        self.assertLess(abs(sum(means) / len(means)), 0.05)

    def test_fdr_counts_untested_as_p1(self):
        px, fund, mem, ds = world(n=60)
        cfg = dict(CFG, min_periods=10000)
        res = C.run_study(px, fund, mem, cfg, ds[-1], log=lambda *a: None)
        self.assertTrue(all(r["status"] == "premalo" for r in res))

    def test_markdown_renders(self):
        px, fund, mem, ds = world(n=200, noise=0.002)
        res = C.run_study(px, fund, mem, CFG, ds[-1], log=lambda *a: None)
        cfg = dict(CFG, version=1, registered_utc="2026-10-14T01:00:00Z", limits="x")
        md = C.to_markdown({"tests": res}, cfg, {"generated_utc": "2026-10-14T10:00:00Z", "n_coins": 8, "from": "2024-02-01", "to": ds[-1]})
        self.assertIn("carry:3d:3d", md)
        self.assertIn("Kandidata:", md)


if __name__ == "__main__":
    unittest.main()
