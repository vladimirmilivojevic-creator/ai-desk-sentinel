import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import portfolio_sim as ps  # noqa: E402
from lab.indicators import Series  # noqa: E402

DAY = 86400000
T0 = 1_640_995_200_000  # 2022-01-01 UTC


def daily(n, seed, drift=0.0, vol=0.02, start=100.0):
    rnd = random.Random(seed)
    c, out = start, []
    for i in range(n):
        o = c
        c = c * (1.0 + drift + rnd.gauss(0.0, vol))
        out.append({"t": T0 + i * DAY, "o": o, "h": max(o, c) * 1.001, "l": min(o, c) * 0.999, "c": c, "v": 1000.0})
    return out


def world(n=900, names=12, trending=False, seed=1):
    """Svet kripto instrumenata. trending=True: svaki ima svoj stalan trend (pobednici ostaju pobednici)."""
    out = {}
    for j in range(names):
        drift = (j - names / 2.0) * 0.0006 if trending else 0.0
        sym = "C%d" % j
        out[sym] = Series(daily(n, seed * 100 + j, drift=drift), None, sym=sym, group="crypto", cls="crypto")
    return out


class PortfolioSimTests(unittest.TestCase):
    def test_trending_world_makes_money(self):
        rows, n = ps.csm_series(world(trending=True), "crypto", 14, 7, 3, True, cost_pct=0.0)
        m = ps.metrics(rows)
        self.assertGreater(n, 500)
        self.assertGreater(m["sharpe"], 1.5)
        self.assertGreater(m["t"], 2.5)

    def test_random_world_with_cost_has_no_edge(self):
        for seed in (1, 2, 3):
            rows, _ = ps.csm_series(world(trending=False, seed=seed), "crypto", 14, 7, 3, True, cost_pct=0.23)
            self.assertLess(ps.metrics(rows)["sharpe"], 1.0, "seed %d" % seed)

    def test_reversal_flips_sign_in_trending_world(self):
        w = world(trending=True)
        mom = ps.metrics(ps.csm_series(w, "crypto", 14, 7, 3, True, cost_pct=0.0)[0])["sharpe"]
        rev = ps.metrics(ps.csm_series(w, "crypto", 14, 7, 3, False, cost_pct=0.0)[0])["sharpe"]
        self.assertGreater(mom, 0)
        self.assertLess(rev, 0)

    def test_higher_cost_lowers_return(self):
        w = world(trending=True)
        lo = ps.metrics(ps.csm_series(w, "crypto", 14, 7, 3, True, cost_pct=0.0)[0])["total_pct"]
        hi = ps.metrics(ps.csm_series(w, "crypto", 14, 7, 3, True, cost_pct=0.5)[0])["total_pct"]
        self.assertGreater(lo, hi)

    def test_delay_shifts_first_day(self):
        w = world(trending=True)
        r0, _ = ps.csm_series(w, "crypto", 14, 7, 3, True, cost_pct=0.0, delay=0)
        r2, _ = ps.csm_series(w, "crypto", 14, 7, 3, True, cost_pct=0.0, delay=2)
        self.assertEqual(r2[0][0] - r0[0][0], 2 * DAY)

    def test_needs_enough_names(self):
        rows, n = ps.csm_series(world(names=5), "crypto", 14, 7, 3, True)
        self.assertEqual((rows, n), ([], 0))

    def test_other_group_is_ignored(self):
        w = world(names=12)
        for s in w.values():
            s.group = "stock"
        rows, n = ps.csm_series(w, "crypto", 14, 7, 3, True)
        self.assertEqual(n, 0)

    def test_metrics_shape_and_window(self):
        rows, _ = ps.csm_series(world(trending=True), "crypto", 14, 7, 3, True, cost_pct=0.0)
        m = ps.metrics(rows)
        self.assertLessEqual(m["max_dd_pct"], 0.0)
        self.assertIn(2022, m["by_year"])
        later = ps.metrics(rows, ps.ts_ms(2023, 6, 1))
        self.assertLess(later["n_days"], m["n_days"])
        self.assertEqual(ps.metrics(rows[:10]), {"n_days": 10})

    def test_oos_selection_returns_all_combinations(self):
        w = world(n=1100, trending=True)
        combos = ps.oos_selection(w, "crypto", cut=ps.ts_ms(2023, 6, 1), cost_pct=0.0)
        self.assertEqual(len(combos), 36)
        self.assertGreaterEqual(combos[0][0], combos[-1][0])


if __name__ == "__main__":
    unittest.main()
