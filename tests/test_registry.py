import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import registry as R  # noqa: E402

G = R.load_gates()


def row(vid="D_X", test="E7", n=1000, mean=0.5, t=3.0, t_train=2.0, t_test=2.0, recent=0.3, fdr=True, groups=None, family="MOM", interval="1d"):
    return {"id": vid, "family": family, "interval": interval, "test": test, "verdict": "obecava", "fdr_pass": fdr,
            "stats": {"n": n, "mean": mean, "all": {"days": 400, "t": t}, "train": {"t": t_train}, "test": {"t": t_test},
                      "windows": {"last270d": {"mean": recent, "t": 1.0}}},
            "groups": groups if groups is not None else {"crypto": {"n": 900, "mean": 0.6}, "stock": {"n": 100, "mean": -0.2}}}


def fwd(n=40, mean=0.8, days=25, t_naive=2.0):
    return {"n": n, "mean": mean, "days": days, "t_naive": t_naive}


class RegistryTests(unittest.TestCase):
    def status(self, rows, f=None, placebo=None):
        return R.classify([R._hist_row(r) for r in rows], f, placebo, G)

    def test_strong_history_is_probni_without_forward(self):
        s, why, _ = self.status([row()])
        self.assertEqual(s, "probni")
        self.assertIn("nema ishoda unapred", why[0])

    def test_forward_confirmation_makes_it_ziv(self):
        s, why, _ = self.status([row()], fwd(), placebo=-0.25)
        self.assertEqual((s, why), ("ziv", []))

    def test_forward_not_beating_placebo_stays_probni(self):
        s, why, _ = self.status([row()], fwd(mean=0.05, t_naive=1.6), placebo=0.0)
        self.assertEqual(s, "probni")
        self.assertTrue(any("placebo" in w for w in why))

    def test_forward_clear_loser_is_retired(self):
        s, _, _ = self.status([row()], fwd(n=40, mean=-0.6, t_naive=-2.5), placebo=-0.2)
        self.assertEqual(s, "penzionisan")

    def test_weak_t_is_rejected(self):
        self.assertEqual(self.status([row(t=1.0, mean=0.2)])[0], "odbacen")
        self.assertEqual(self.status([row(t=2.5, mean=-0.1)])[0], "odbacen")

    def test_each_historical_gate_blocks_promotion(self):
        for kw, text in ((dict(recent=-0.1), "270"), (dict(fdr=False), "FDR"), (dict(n=100), "n 100"), (dict(t_test=0.2), "drugi deo"),
                         (dict(t_train=-0.5), "prvi deo"), (dict(t=1.8), "t 1.80")):
            s, why, _ = self.status([row(**kw)])
            self.assertEqual(s, "kandidat", kw)
            self.assertTrue(any(text in w for w in why), (kw, why))

    def test_best_test_is_highest_t_with_enough_samples(self):
        rows = [R._hist_row(row(test="E3", t=5.0, n=50)), R._hist_row(row(test="E7", t=3.0)), R._hist_row(row(test="E14", t=2.5))]
        self.assertEqual(R.best_hist(rows, G)["test"], "E7")

    def test_edge_groups_listed(self):
        b = R._hist_row(row())
        self.assertEqual(b["edge_groups"], ["crypto"])

    def test_build_skips_placebo_and_counts(self):
        res = [row("D_A"), row("D_B", t=0.5, mean=0.1), row("PLACEBO_p2", interval="1h"), row("D_PLACEBO_p5")]
        reg = R.build(res, None, G, now="2026-10-07T00:00:00Z")
        self.assertEqual(reg["counts"], {"probni": 1, "odbacen": 1})
        self.assertEqual([x["id"] for x in reg["rules"]], ["D_A", "D_B"])
        self.assertIn("D_A", R.to_markdown(reg))

    def test_build_reads_forward_and_placebo(self):
        stats = {"variants": {"D_A": {"tests": {"E7": fwd()}}, "D_PLACEBO_p5": {"tests": {"E7": {"mean": -0.25}}}}}
        reg = R.build([row("D_A")], stats, G)
        self.assertEqual(reg["rules"][0]["status"], "ziv")

    def test_no_historical_test_is_candidate(self):
        self.assertEqual(R.classify([], None, None, G)[0], "kandidat")


if __name__ == "__main__":
    unittest.main()
