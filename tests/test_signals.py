import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sentinel import signals  # noqa: E402

NOW = 1_800_000_000


def psig(key="BRENT", d="down", px=100.0, trig=True, **kw):
    p = {"key": key, "theme": "OIL", "dir": d, "px": px, "trig": trig, "stale": False, "m60": -3.0, "m240": -3.5,
         "rel": 1.2, "confirmed": True, "tradable": True}
    p.update(kw)
    return p


class SignalTests(unittest.TestCase):
    def test_record_cooldown_and_filters(self):
        st = {}
        themes = {"OIL": {"tier": "N1", "families": {"P": 1.0}}}
        self.assertEqual(len(signals.record([psig()], themes, {}, NOW, st)), 1)
        self.assertEqual(len(signals.record([psig()], themes, {}, NOW + 600, st)), 0)  # hladjenje 120 min
        self.assertEqual(len(signals.record([psig()], themes, {}, NOW + 7300, st)), 1)
        self.assertEqual(signals.record([psig(trig=False), psig(stale=True), psig(signal_only=True), psig(tradable=False)],
                                        themes, {}, NOW + 99999, st), [])

    def test_event_id_is_reused_for_the_signal(self):
        st = {}
        s = signals.record([psig()], {"OIL": {"tier": "N3", "families": {}}}, {"OIL": "EV-20261006T1500Z-OIL"}, NOW, st)
        self.assertEqual(s[0]["id"], "EV-20261006T1500Z-OIL")

    def test_outcomes_follow_and_fade(self):
        st = {}
        signals.record([psig(d="down", px=100.0)], {"OIL": {"tier": "N1", "families": {}}}, {}, NOW, st)

        def candles(coin, interval, mins):
            # cena pada jos 2% posle 4 h, vraca se na 101 posle 24 h, 99 posle 72 h
            return [(NOW + 4 * 3600, 98.0), (NOW + 24 * 3600, 101.0), (NOW + 72 * 3600, 99.0)]

        done = signals.update_outcomes(st, NOW + 73 * 3600, candles, {"BRENT": "xyz:BRENTOIL"})
        self.assertEqual(len(done), 1)
        out = done[0]["out"]
        # smer dole: pad cene je "follow" dobitak
        self.assertAlmostEqual(out["4"], 2.0, places=2)
        self.assertAlmostEqual(out["24"], -1.0, places=2)
        self.assertAlmostEqual(out["72"], 1.0, places=2)
        self.assertEqual(st["open"], [])

    def test_partial_outcomes_stay_open_and_stats_need_min_n(self):
        st = {}
        signals.record([psig(d="up", px=100.0)], {"OIL": {"tier": "N1", "families": {}}}, {}, NOW, st)
        signals.update_outcomes(st, NOW + 5 * 3600, lambda c, i, m: [(NOW + 4 * 3600, 103.0)], {"BRENT": "x"})
        self.assertEqual(len(st["open"]), 1)
        self.assertEqual(st["open"][0]["out"], {"4": 3.0})
        s = signals.stats(st)
        self.assertEqual(s["OIL"]["h4"]["n"], 1)
        self.assertFalse(s["OIL"]["h4"]["enough"])

    def test_stats_split_by_news(self):
        st = {}
        th_news = {"OIL": {"tier": "N2", "families": {"P": 2.0, "H": 1.0}}}
        th_none = {"OIL": {"tier": "N1", "families": {"P": 1.0}}}
        signals.record([psig(d="up", px=100.0)], th_news, {}, NOW, st)
        signals.record([psig(key="WTI", d="up", px=100.0)], th_none, {}, NOW, st)
        up = lambda c, i, m: [(NOW + 4 * 3600, 102.0), (NOW + 24 * 3600, 102.0), (NOW + 72 * 3600, 102.0)]
        signals.update_outcomes(st, NOW + 80 * 3600, up, {"BRENT": "a", "WTI": "b"})
        s = signals.stats(st)
        self.assertEqual(s["OIL|sa vescu"]["h4"]["n"], 1)
        self.assertEqual(s["OIL|bez vesti"]["h4"]["n"], 1)
        self.assertEqual(s["SVE"]["h4"]["n"], 2)

    def test_candle_too_far_from_target_gives_no_outcome(self):
        st = {}
        signals.record([psig()], {"OIL": {"tier": None, "families": {}}}, {}, NOW, st)
        signals.update_outcomes(st, NOW + 5 * 3600, lambda c, i, m: [(NOW + 10 * 3600, 90.0)], {"BRENT": "x"})
        self.assertEqual(st["open"][0]["out"], {})


if __name__ == "__main__":
    unittest.main()
