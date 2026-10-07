import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import regime_study as R  # noqa: E402


def noise(n, seed, sd=1.0):
    rnd = random.Random(seed)
    return [rnd.gauss(0, sd) for _ in range(n)]


def ar1(n, seed, phi=0.985):
    """Spora, postojana promenljiva stanja (kao VIX ili F&G): tercil ostaje isti kroz ceo blok od 14 dana."""
    rnd, x, out = random.Random(seed), 0.0, []
    for _ in range(n):
        x = phi * x + rnd.gauss(0, 1.0)
        out.append(x)
    return out


class HelperTests(unittest.TestCase):
    def test_rank_labels_never_look_ahead(self):
        x = noise(600, 1)
        a = R.rank_labels(x, min_hist=100)
        y = x[:400] + [1e6] * 200  # budunost se menja, proslost ne
        b = R.rank_labels(y, min_hist=100)
        self.assertEqual(a[:400], b[:400])
        self.assertIsNone(a[50])
        self.assertIn(a[300], ("low", "mid", "high"))

    def test_terciles_are_roughly_balanced(self):
        lab = [l for l in R.rank_labels(noise(3000, 2), min_hist=100) if l]
        for k in ("low", "mid", "high"):
            self.assertGreater(lab.count(k) / len(lab), 0.25)

    def test_blocks_use_previous_day_state(self):
        returns = [0.0] * 100
        labels = ["x"] * 100
        labels[0] = "low"
        returns[1:15] = [2.0] * 14
        bl = R.blocks(returns, labels, block=14)
        self.assertEqual(bl[0], ("low", 2.0))  # blok koji pocinje danom 1 koristi oznaku dana 0

    def test_ffill_with_lag_and_transforms(self):
        days = R.dates_range("2026-01-01", "2026-01-10")
        s = {"2026-01-02": 10.0, "2026-01-06": 20.0}
        out = R.ffill(s, days, lag=2)
        self.assertIsNone(out["2026-01-03"])
        self.assertEqual(out["2026-01-04"], 10.0)
        self.assertEqual(out["2026-01-07"], 10.0)
        self.assertEqual(out["2026-01-08"], 20.0)
        self.assertAlmostEqual(R.pct_change([100.0, 110.0, 121.0], 1)[2], 10.0)
        self.assertEqual(R.diff([1.0, 3.0, 6.0], 2)[2], 5.0)
        t = R.trend([1.0] * 10 + [2.0], 5)
        self.assertGreater(t[-1], 0)


class ConditionTests(unittest.TestCase):
    def test_planted_regime_effect_is_detected(self):
        n = 1500
        n = 3000
        x = ar1(n, 3)
        lab = R.rank_labels(x)
        rnd = random.Random(4)
        ret = [rnd.gauss(0, 1.0) + (0.8 if i > 0 and lab[i - 1] == "high" else 0.0) for i in range(n)]
        c = R.condition(ret, x)
        self.assertGreater(c["diff"], 0.4)
        self.assertGreater(c["t"], 3.0)

    def test_independent_noise_rarely_significant(self):
        ts = []
        for seed in range(30):
            c = R.condition(noise(1500, 100 + seed), ar1(1500, 200 + seed))
            if c:  # premalo blokova u tercilu = test se ne racuna (ispravno)
                ts.append(abs(c["t"]))
        self.assertGreaterEqual(len(ts), 15)
        self.assertLess(sum(1 for t in ts if t > 2) / len(ts), 0.25)

    def test_none_returns_and_short_history(self):
        self.assertIsNone(R.condition([None] * 300, noise(300, 5)))
        self.assertIsNone(R.condition(noise(100, 6), noise(100, 7)))

    def test_run_study_structure_fdr_and_evidence(self):
        n = 3000
        x_real = ar1(n, 11)
        lab = R.rank_labels(x_real)
        rnd = random.Random(12)
        ret_real = [rnd.gauss(0, 1.0) + (0.8 if i > 0 and lab[i - 1] == "high" else 0.0) for i in range(n)]
        states = {"real": x_real, "junk1": ar1(n, 13), "junk2": ar1(n, 14)}
        returns = {"csm_x": ret_real, "placebo1": noise(n, 15), "placebo2": noise(n, 16)}
        res = R.run_study(returns, states)
        self.assertEqual(res["tests_real"], 3)
        top = res["results"][0]
        self.assertEqual((top["strategy"], top["var"]), ("csm_x", "real"))
        self.assertTrue(top["fdr_pass"])
        self.assertEqual(res["null"]["n_tests"], 6)
        ev = R.evidence(res)
        self.assertEqual(ev["findings"][0]["var"], "real")
        self.assertTrue(ev["findings"][0]["high_better"])
        self.assertIn("csm_x", R.to_markdown(res))


class StatesTests(unittest.TestCase):
    def test_build_states_with_fake_loaders_skips_missing_sources(self):
        days = R.dates_range("2026-01-01", "2026-04-30")
        fake = lambda: {d: 20.0 + i * 0.01 for i, d in enumerate(R.dates_range("2025-06-01", "2026-04-30"))}  # noqa: E731
        loaders = {"y_vix": fake, "y_vix3m": fake, "fng": fake, "bn_agg": lambda: {}}
        for k in list(R.YAHOO):
            loaders.setdefault("y_" + k, lambda: (_ for _ in ()).throw(RuntimeError("nema")))
        for k in list(R.FRED):
            loaders["f_" + k] = lambda: (_ for _ in ()).throw(RuntimeError("nema"))
        for k in ("dvol", "stable", "cftc_btc", "cftc_gold", "cftc_es"):
            loaders[k] = lambda: (_ for _ in ()).throw(RuntimeError("nema"))

        class S:  # prazan skup svecica
            group = "crypto"
            t, c = [], []
            sym = "X"
        states = R.build_states({}, days, loaders)
        self.assertIn("vix", states)
        self.assertIn("vix_term", states)
        self.assertIn("fng", states)
        self.assertNotIn("move", states)  # izvor nije dostupan: izostavljen, ne izmisljen
        self.assertEqual(len(states["vix"]), len(days))


if __name__ == "__main__":
    unittest.main()
