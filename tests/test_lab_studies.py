import unittest

from lab import adaptive_side as ad, hourly_stops as hs, sim

DAY = 86400000
HOUR = 3600 * 1000


class FakeS:
    cls = "crypto"
    atr_pct = [0.02]


class AdaptiveTests(unittest.TestCase):
    def events(self, gs, per_day=3, t0=1_790_000_000_000 // DAY * DAY):
        ev = []
        for d, g in enumerate(gs):
            for k in range(per_day):
                ev.append((t0 + d * DAY + k * HOUR, g, "V"))
        return ev

    def test_choose_sides_uses_only_old_outcomes(self):
        ev = self.events([1.0] * 5 + [-1.0] * 5)
        sides = ad.choose_sides(ev, window_days=3, min_past=3)
        self.assertIsNone(sides[0])                 # nema proslosti
        self.assertEqual(sides[3 * 3], 1)           # 4. dan: poznati ishodi su pozitivni (1 dan kasnjenja)
        self.assertEqual(sides[-1], -1)             # posle pogresnih dana okrece (prozor od 3 dana)

    def test_lag_prevents_peeking_at_same_day(self):
        ev = self.events([1.0, 1.0, -5.0], per_day=1)
        sides = ad.choose_sides(ev, window_days=5, min_past=1, lag_h=24)
        self.assertEqual(sides[2], 1)               # prosli ishod do tog trenutka je +1, ne vidi se -5 tog dana

    def test_persistent_regime_beats_null(self):
        import random
        rnd, gs, sign = random.Random(4), [], 1.0
        while len(gs) < 150:                          # dugi rezimi nepravilne duzine (periodican niz bi imao savrsena pomeranja)
            gs += [0.8 * sign] * rnd.randint(8, 22)
            sign = -sign
        ev = self.events(gs)
        sides = ad.choose_sides(ev, window_days=3, min_past=3)
        obs = ad.mean_net(ev, sides)
        null = ad.shift_null(ev, sides, n_sims=100)
        self.assertGreater(obs, sorted(null)[int(0.95 * len(null))])

    def test_iid_returns_no_edge(self):
        import random
        rnd = random.Random(2)
        ev = self.events([rnd.gauss(0, 1) for _ in range(120)])
        sides = ad.choose_sides(ev, window_days=5, min_past=3)
        obs = ad.mean_net(ev, sides)
        null = ad.shift_null(ev, sides, n_sims=200)
        p = (1 + sum(1 for x in null if x >= obs)) / (1 + len(null))
        self.assertGreater(p, 0.05)


class StopTests(unittest.TestCase):
    def test_bounds_scale_with_multiple(self):
        S = FakeS()
        lo, hi = sim.CLASS_BOUNDS["crypto"]
        S.atr_pct = [0.0001]
        self.assertAlmostEqual(hs.stop_pct(S, 0, 2.5), lo)                    # uzivo: donja granica klase
        self.assertAlmostEqual(hs.stop_pct(S, 0, 5.0), lo * 2.0)              # duplo siri, granice duplo vece
        S.atr_pct = [0.5]
        self.assertAlmostEqual(hs.stop_pct(S, 0, 2.5), hi)
        S.atr_pct = [None]
        self.assertIsNone(hs.stop_pct(S, 0, 2.5))

    def test_classify(self):
        self.assertEqual(hs.classify(None, 0, "long", 2.0, -2.0 - sim.COST_PCT), "stop")
        self.assertEqual(hs.classify(None, 0, "long", 2.0, 4.0 - sim.COST_PCT), "cilj")
        self.assertEqual(hs.classify(None, 0, "long", 2.0, 0.5), "vreme")
        self.assertIsNone(hs.classify(None, 0, "long", 2.0, None))


if __name__ == "__main__":
    unittest.main()
