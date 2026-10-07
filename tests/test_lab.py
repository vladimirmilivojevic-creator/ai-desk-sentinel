"""Testovi laboratorije (lab/). Svi podaci su IZMISLJENI (nasumicna setnja sa fiksnim semenom), bez mreze."""
import json
import os
import random
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import backtest, data, forward, indicators, rules, sim, stats  # noqa: E402

HOUR = 3600000


def walk(n, seed=1, vol=0.004, drift=0.0, start=100.0, t0=1_700_000_000_000):
    rnd = random.Random(seed)
    cs, px = [], start
    for k in range(n):
        o = px
        px = px * (1 + drift + vol * rnd.gauss(0, 1))
        h, l = max(o, px) * 1.001, min(o, px) * 0.999
        cs.append({"t": t0 + k * HOUR, "o": o, "h": h, "l": l, "c": px, "v": 1000.0})
    return cs


def series(n=400, seed=1, sym="BTC", group="crypto", cls="crypto", **kw):
    return indicators.Series(walk(n, seed, **kw), None, sym=sym, group=group, cls=cls)


class IndicatorTests(unittest.TestCase):
    def test_rsi_extremes(self):
        up = [100 + i for i in range(60)]
        self.assertEqual(indicators.rsi(up)[-1], 100.0)
        down = [200 - i for i in range(60)]
        self.assertLess(indicators.rsi(down)[-1], 1.0)

    def test_ema_wilder_and_none_prefix(self):
        e = indicators.ema([1, 1, 1, 1], 2)
        self.assertEqual(e, [1, 1, 1, 1])
        w = indicators.wilder([1.0] * 20, 14)
        self.assertEqual(w[:13], [None] * 13)
        self.assertAlmostEqual(w[-1], 1.0)

    def test_rolling_max_excludes_current(self):
        m = indicators.rolling_max([1, 5, 2, 9, 3], 2)
        self.assertEqual(m, [None, None, 5, 5, 9])

    def test_series_z_and_ret(self):
        S = series(300)
        self.assertIsNone(S.ret(2, 5))
        self.assertIsNotNone(S.z(250, 4))
        self.assertIsNone(S.z(5, 4))


class RuleTests(unittest.TestCase):
    def test_mom_and_fade_are_opposites(self):
        S = series(300, seed=3)
        i = 250
        S.c[i] = S.c[i - 4] * 1.2  # veliki skok
        S.atr_pct[i] = 0.004
        a = rules.mom(S, i, {}, L=4, z=1.5, fade=False)
        b = rules.mom(S, i, {}, L=4, z=1.5, fade=True)
        self.assertEqual((a, b), ("long", "short"))
        self.assertIsNone(rules.mom(S, i, {}, L=4, z=1e9))

    def test_donchian_breakout(self):
        S = series(300, seed=4)
        i = 250
        S.c[i] = max(S.h[i - 72:i]) * 1.05
        self.assertEqual(rules.donchian(S, i, {}, N=72, fade=False), "long")
        self.assertEqual(rules.donchian(S, i, {}, N=72, fade=True), "short")
        S.c[i] = min(S.l[i - 72:i]) * 0.95
        self.assertEqual(rules.donchian(S, i, {}, N=72, fade=False), "short")

    def test_funding_rule(self):
        cs = walk(300, seed=5)
        S = indicators.Series(cs, [{"t": cs[250]["t"], "rate": 0.0002}, {"t": cs[251]["t"], "rate": -0.0002}], sym="BTC", group="crypto")
        self.assertEqual(rules.funding_extreme(S, 250, {}, thr=0.00004), "short")
        self.assertEqual(rules.funding_extreme(S, 251, {}, thr=0.00004), "long")
        self.assertIsNone(rules.funding_extreme(S, 252, {}, thr=0.00004))

    def test_csm_rank_context(self):
        ser = {}
        for k, drift in enumerate((-0.002, -0.001, 0.0, 0.001, 0.002, 0.003)):
            ser["S%d" % k] = indicators.Series(walk(300, seed=10 + k, vol=0.0005, drift=drift), None, sym="S%d" % k, group="crypto")
        ctx = {"csm": rules.csm_context(ser, (24,))}
        i = 280
        weakest, strongest = ser["S0"], ser["S5"]
        self.assertEqual(rules.cross_sectional(weakest, i, ctx, L=24, k=1, momentum=False), "long")
        self.assertEqual(rules.cross_sectional(strongest, i, ctx, L=24, k=1, momentum=False), "short")
        self.assertEqual(rules.cross_sectional(weakest, i, ctx, L=24, k=1, momentum=True), "short")
        self.assertIsNone(rules.cross_sectional(ser["S2"], i, ctx, L=24, k=1))

    def test_btclead_needs_btc_move_and_quiet_alt(self):
        btc = series(300, seed=21, sym="BTC")
        alt = indicators.Series(btc.cs[:], None, sym="ALT", group="crypto", cls="crypto")
        i = 250
        btc.c[i] = btc.c[i - 1] * 1.05
        alt.c[i] = alt.c[i - 1] * 1.0001
        for S in (btc, alt):
            S.atr_pct[i] = 0.004
        ctx = {"btc": btc, "btc_index": {t: k for k, t in enumerate(btc.t)}}
        self.assertEqual(rules.btc_lead(alt, i, ctx, z=2.0), "long")
        self.assertIsNone(rules.btc_lead(btc, i, ctx, z=2.0))
        alt.c[i] = alt.c[i - 1] * 1.05
        self.assertIsNone(rules.btc_lead(alt, i, ctx, z=2.0))

    def test_candidates_are_data_never_code(self):
        good = {"family": "MOM", "params": {"L": 6, "z": 2.0, "fade": False}}
        bad_family = {"family": "os.system", "params": {}}
        bad_params = {"family": "MOM", "params": {"L": [1, 2], "z": {"x": 1}, "evil": "ok"}}
        v = rules.candidate_variants([good, bad_family, bad_params, {"family": "MOM", "params": "x"}])
        ids = [x[0] for x in v]
        self.assertEqual(len(v), 2)
        self.assertTrue(all(i.startswith("CAND_MOM_") for i in ids))
        self.assertTrue(all(isinstance(val, (int, float, bool, str)) for _, _, p in v for val in p.values()))

    def test_variant_ids_unique_and_known_families(self):
        ids = [v[0] for v in rules.default_variants() + rules.daily_variants()]
        self.assertEqual(len(ids), len(set(ids)))
        for _, fam, _ in rules.default_variants() + rules.daily_variants():
            self.assertIn(fam, rules.FAMILIES)


class SimTests(unittest.TestCase):
    def setUp(self):
        self.S = series(120, seed=7, vol=0.0001)

    def test_fixed_return_net_of_cost_and_sign(self):
        S = self.S
        raw = (S.c[60 + 24] / S.c[60] - 1) * 100
        self.assertAlmostEqual(sim.fixed_return(S, 60, "long", 24), raw - sim.COST_PCT)
        self.assertAlmostEqual(sim.fixed_return(S, 60, "short", 24), -raw - sim.COST_PCT)
        self.assertIsNone(sim.fixed_return(S, 110, "long", 24))

    def test_stop_hits_first_when_both_in_same_candle(self):
        S = self.S
        i = 60
        e = S.c[i]
        S.h[i + 1] = e * 1.10
        S.l[i + 1] = e * 0.90
        self.assertAlmostEqual(sim.stop_return(S, i, "long", 2.0, 24), -2.0 - sim.COST_PCT)
        self.assertAlmostEqual(sim.stop_return(S, i, "short", 2.0, 24), -2.0 - sim.COST_PCT)

    def test_target_and_time_exit(self):
        S = self.S
        i = 60
        e = S.c[i]
        S.h[i + 3] = e * 1.05
        self.assertAlmostEqual(sim.stop_return(S, i, "long", 2.0, 24), 4.0 - sim.COST_PCT)
        S2 = series(120, seed=8, vol=1e-6)
        r = sim.stop_return(S2, 60, "long", 2.0, 24)
        self.assertAlmostEqual(r, (S2.c[84] / S2.c[60] - 1) * 100 - sim.COST_PCT, places=6)

    def test_stop_pct_clamped_by_class(self):
        S = self.S
        S.atr_pct[60] = 0.0001
        self.assertEqual(sim.stop_pct_for(S, 60, "crypto"), 1.2)
        S.atr_pct[60] = 0.5
        self.assertEqual(sim.stop_pct_for(S, 60, "crypto"), 3.5)
        S.atr_pct[60] = None
        self.assertIsNone(sim.stop_pct_for(S, 60, "crypto"))


class StatsTests(unittest.TestCase):
    def test_thin_no_overlap_per_symbol(self):
        sigs = [("A", 0, 0, "long"), ("A", 3, 1, "long"), ("A", 5, 2, "long"), ("B", 1, 0, "long"), ("B", 2, 1, "long")]
        out = stats.thin(sigs, 4)
        self.assertEqual([(s[0], s[1]) for s in out], [("A", 0), ("A", 5), ("B", 1)])

    def test_daily_t_clusters_by_day(self):
        day = stats.DAY_MS
        rows = [(d * day + k, 1.0 if d % 2 else -0.5, "x") for d in range(20) for k in range(50)]
        d = stats.daily_t([(t, r) for t, r, _ in rows])
        self.assertEqual(d["days"], 20)  # 1000 trejdova, ali samo 20 nezavisnih dana
        self.assertIsNotNone(d["t"])
        self.assertEqual(stats.daily_t([(0, 1.0)])["t"], None)

    def test_bonferroni_grows_with_tests(self):
        self.assertAlmostEqual(stats.bonferroni_z(1), 1.96, places=2)
        self.assertGreater(stats.bonferroni_z(100), 3.0)
        self.assertGreater(stats.bonferroni_z(1000), stats.bonferroni_z(100))

    def test_verdicts(self):
        def mk(n, mean, t, ta, tb):
            return {"n": n, "mean": mean, "all": {"t": t}, "train": {"t": ta}, "test": {"t": tb}}
        self.assertEqual(stats.verdict(mk(10, 1, 5, 5, 5), 100), "premalo")
        self.assertEqual(stats.verdict(mk(100, -1, 5, 5, 5), 100), "odbaceno")
        self.assertEqual(stats.verdict(mk(100, 1, 4.0, 3, 3), 100), "potvrdjeno")
        self.assertEqual(stats.verdict(mk(100, 1, 2.5, 2.1, 2.2), 100), "obecava")
        self.assertEqual(stats.verdict(mk(100, 1, 2.2, 1.0, 1.0), 100), "slabo")
        self.assertEqual(stats.verdict(mk(100, 1, 2.5, 3.0, -1.0), 100), "odbaceno")
        self.assertEqual(stats.verdict(mk(100, 1, 1.0, 1.0, 1.0), 100), "odbaceno")

    def test_pure_noise_is_rarely_confirmed(self):
        """Pravilo bez ikakve prednosti ne sme da prodje Bonferroni (kontrola lazno pozitivnih)."""
        confirmed = 0
        for seed in range(40):
            S = series(1500, seed=100 + seed, vol=0.004)
            ctx = {}
            sigs = []
            fn = rules.FAMILIES["MOM"]
            for i in range(210, S.n - 1):
                side = fn(S, i, ctx, L=4, z=1.5, fade=False)
                if side:
                    sigs.append(("S", i, S.t[i], side))
            rows = []
            for sym, i, t, side in stats.thin(sigs, 24):
                r = sim.fixed_return(S, i, side, 24)
                if r is not None:
                    rows.append((t, r, sym))
            s = stats.summarize(rows, S.t[210], S.t[-25])
            if stats.verdict(s, 105) == "potvrdjeno":
                confirmed += 1
        self.assertLessEqual(confirmed, 1)


class ForwardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.now = int(time.time() * 1000)
        self.calls = 0
        self._fc, self._ff = data.fetch_candles, data.fetch_funding
        base = ((self.now // HOUR) * HOUR) - HOUR

        def fake_candles(coin, days=200, interval="1h", now_ms=None):
            self.calls += 1
            n = int(days * (24 if interval == "1h" else 1))
            step = HOUR if interval == "1h" else 24 * HOUR
            seed = sum(ord(c) for c in coin)
            cs = walk(n, seed=seed, t0=base - (n - 1) * step)
            for k, c in enumerate(cs):
                c["t"] = base - (n - 1 - k) * step
            return cs

        data.fetch_candles = fake_candles
        data.fetch_funding = lambda coin, days=200, now_ms=None: []
        self.cfg = {"days": 30, "universe": [
            {"sym": s, "hl": s, "group": "crypto", "cls": "crypto"} for s in ("BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LTC")],
            "live_variants": [{"id": "CSM_rev_L24", "hold_hours": 24}, {"id": "D_MOM_L7_z0.5", "hold_hours": 168}]}
        self._lc = backtest.load_config
        backtest.load_config = lambda: (self.cfg, [])

    def tearDown(self):
        data.fetch_candles, data.fetch_funding = self._fc, self._ff
        backtest.load_config = self._lc
        self.tmp.cleanup()

    def test_run_writes_files_sets_t0_and_skips_same_bar(self):
        r = forward.run(self.tmp.name, now_ms=self.now, log=lambda *_: None)
        self.assertTrue(r["ok"], r)
        lab = os.path.join(self.tmp.name, "lab")
        for f in ("stats.json", "triggers.json", "meta.json", "daily.json", "panel.json"):
            self.assertTrue(os.path.exists(os.path.join(lab, f)), f)
        meta = json.load(open(os.path.join(lab, "meta.json"), encoding="utf-8"))
        self.assertEqual(meta["t0_ms"], (self.now // HOUR) * HOUR)
        with open(os.path.join(lab, "panel.json"), encoding="utf-8") as f:
            pj = json.load(f)
        self.assertEqual([x["id"] for x in pj["live"]], ["CSM_rev_L24", "D_MOM_L7_z0.5"])
        self.assertIn("backtest_counts", pj)
        self.assertLess(len(json.dumps(pj)), 20000)
        n_calls = self.calls
        r2 = forward.run(self.tmp.name, now_ms=self.now, log=lambda *_: None)
        self.assertIn("skipped", r2)
        self.assertEqual(self.calls, n_calls)  # isti sat: nema ponovnog preuzimanja

    def test_forward_counts_only_signals_after_t0(self):
        os.makedirs(os.path.join(self.tmp.name, "lab"))
        t0 = ((self.now // HOUR) * HOUR) - 6 * 24 * HOUR
        json.dump({"t0_ms": t0, "t0_utc": forward.iso(t0)}, open(os.path.join(self.tmp.name, "lab", "meta.json"), "w"))
        forward.run(self.tmp.name, now_ms=self.now, force=True, log=lambda *_: None)
        st = json.load(open(os.path.join(self.tmp.name, "lab", "stats.json"), encoding="utf-8"))
        self.assertGreater(st["totals"]["signals"], 0)
        self.assertTrue(st["variants"]["CSM_rev_L24"]["live"])
        self.assertFalse(st["variants"]["MOM_L4_z1.5"]["live"])
        # ishodi postoje samo tamo gde je proslo dovoljno vremena
        h72 = st["variants"]["MOM_L1_z1.5"]["tests"].get("H72", {"n": 0})
        h4 = st["variants"]["MOM_L1_z1.5"]["tests"].get("H4", {"n": 0})
        self.assertGreaterEqual(h4["n"], h72["n"])
        tr = json.load(open(os.path.join(self.tmp.name, "lab", "triggers.json"), encoding="utf-8"))
        self.assertTrue(all(x["live"] for x in tr["triggers"]))
        self.assertTrue(all(x["variant"] in ("CSM_rev_L24", "D_MOM_L7_z0.5") for x in tr["triggers"]))
        for x in tr["triggers"]:
            self.assertGreater(x["stop_pct"], 0)
            self.assertGreater(x["tp_pct"], x["stop_pct"])

    def test_governor_demotes_known_losers_and_forward_losers(self):
        cfg = {"live_variants": [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}],
               "governor": {"min_n": 30, "t_naive_max": -2.0, "bt_t_known_loser": -3.0}}
        av = {"A": {"interval": "1h", "backtest": {"E24": {"t": -5.0}}, "tests": {}},
              "B": {"interval": "1h", "backtest": {"E24": {"t": 0.5}}, "tests": {"E24": {"n": 40, "t_naive": -2.5, "mean": -0.4}}},
              "C": {"interval": "1h", "backtest": {"E24": {"t": 0.5}}, "tests": {"E24": {"n": 10, "t_naive": -9.0, "mean": -0.4}}},
              "D": {"interval": "1d", "backtest": {"E7": {"t": 2.9}}, "tests": {"E7": {"n": 50, "t_naive": 1.0, "mean": 0.3}}}}
        out = forward.governor(cfg, av)
        self.assertEqual(sorted(out), ["A", "B"])
        self.assertEqual(out["A"]["reason"], "istorija jasno gubi")
        self.assertEqual(out["B"]["reason"], "unapred jasno gubi")

    def test_failure_never_raises_from_main(self):
        data.fetch_candles = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("mreza"))
        sys.argv = ["lab.forward", "--state", self.tmp.name]
        self.assertEqual(forward.main(), 0)

    def test_summarize_rows_honest_t(self):
        day = stats.DAY_MS
        rows = [(d * day, 0.5, "x") for d in range(4)]
        s = forward.summarize_rows(rows)
        self.assertIsNone(s["t"])  # manje od 10 dana: nema t po danima
        self.assertEqual(s["n"], 4)
        self.assertEqual(forward.summarize_rows([]), {"n": 0})


if __name__ == "__main__":
    unittest.main()
