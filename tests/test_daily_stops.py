import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import daily_stops as D, sim  # noqa: E402
from lab.indicators import Series  # noqa: E402

DAY = 86400000
T0 = 1_640_995_200_000


def flat(n=60):
    """Mirna serija: zatvaranje 100, raspon 99-101 (ATR oko 2%)."""
    return [{"t": T0 + i * DAY, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 1.0} for i in range(n)]


def with_bar(cs, k, **kw):
    cs = [dict(c) for c in cs]
    cs[k].update(kw)
    return cs


class TradeTests(unittest.TestCase):
    def test_live_stop_is_atr_based_and_clamped(self):
        S = Series(flat(), None)
        self.assertAlmostEqual(D.stop_for(S, 30, "uzivo"), 5.0, places=6)
        self.assertAlmostEqual(D.stop_for(S, 30, "uzi"), 3.0, places=6)
        self.assertAlmostEqual(D.stop_for(S, 30, "siri"), 8.0, places=6)

    def test_stop_hit_long(self):
        S = Series(with_bar(flat(), 31, l=94.0), None)
        r, kind = D.trade(S, 30, "long", "uzivo")
        self.assertEqual(kind, "stop")
        self.assertAlmostEqual(r, -5.0 - sim.COST_PCT, places=6)

    def test_stop_hit_short_is_above_entry(self):
        S = Series(with_bar(flat(), 31, h=106.0), None)
        r, kind = D.trade(S, 30, "short", "uzivo")
        self.assertEqual(kind, "stop")
        self.assertAlmostEqual(r, -5.0 - sim.COST_PCT, places=6)

    def test_target_hit_long(self):
        S = Series(with_bar(flat(), 31, h=116.0), None)
        r, kind = D.trade(S, 30, "long", "uzivo")
        self.assertEqual(kind, "cilj")
        self.assertAlmostEqual(r, 15.0 - sim.COST_PCT, places=6)

    def test_time_exit_and_fixed(self):
        S = Series(with_bar(flat(), 37, c=104.0), None)
        r, kind = D.trade(S, 30, "long", "uzivo")
        self.assertEqual(kind, "vreme")
        self.assertAlmostEqual(r, 4.0 - sim.COST_PCT, places=6)
        r2, k2 = D.trade(S, 30, "long", "fiksno")
        self.assertAlmostEqual(r2, 4.0 - sim.COST_PCT, places=6)
        self.assertEqual(k2, "vreme")

    def test_no_data_at_the_end(self):
        S = Series(flat(40), None)
        self.assertIsNone(D.trade(S, 38, "long", "uzivo"))
        self.assertIsNone(D.excursion(S, 38, "long"))

    def test_excursion_mae_mfe(self):
        cs = with_bar(with_bar(flat(), 32, l=92.0), 34, h=110.0)
        S = Series(cs, None)
        mae, mfe = D.excursion(S, 30, "long")
        self.assertAlmostEqual(mae, 8.0)
        self.assertAlmostEqual(mfe, 10.0)
        mae_s, mfe_s = D.excursion(S, 30, "short")
        self.assertAlmostEqual(mae_s, 10.0)
        self.assertAlmostEqual(mfe_s, 8.0)

    def test_study_rule_on_synthetic_world(self):
        from lab import backtest
        series = {}
        for j in range(10):
            rnd, c, cs = random.Random(40 + j), 100.0, []
            for i in range(500):
                o = c
                c = c * (1.0 + 0.001 * (j - 5) + rnd.gauss(0, 0.02))
                cs.append({"t": T0 + i * DAY, "o": o, "h": max(o, c) * 1.005, "l": min(o, c) * 0.995, "c": c, "v": 1.0})
            series["C%d" % j] = Series(cs, None, sym="C%d" % j, group="crypto", cls="crypto")
        ctx = backtest.make_ctx(series, (D.H,))
        r = D.study_rule(series, ctx, "D_MOM_L7_z0.5", "MOM", {"L": 7, "z": 0.5, "fade": False}, "crypto")
        self.assertIsNotNone(r)
        self.assertEqual(set(r["modes"]), set(D.MODES))
        self.assertGreater(r["n_signals"], 20)
        self.assertGreaterEqual(r["modes"]["uzivo"]["stop_pct_share"], 0)
        self.assertGreaterEqual(r["mae_p90"], r["mae_p50"])
        self.assertIn("D_MOM_L7_z0.5", D.to_markdown([r], "crypto"))


if __name__ == "__main__":
    unittest.main()
