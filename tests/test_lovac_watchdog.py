import datetime as dt
import unittest

from lab import lovac_watchdog as W

NOW = dt.datetime(2026, 10, 12, 9, 0, tzinfo=dt.timezone.utc)


def ago(**kw):
    return (NOW - dt.timedelta(**kw)).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(status="completed", conclusion="success", **kw):
    return {"status": status, "conclusion": conclusion, "created_at": ago(**kw)}


class WatchdogTests(unittest.TestCase):
    def test_fresh_files_need_nothing(self):
        self.assertIsNone(W.decide(NOW, ago(hours=8), ago(days=1), [run(hours=8)]))

    def test_stale_radar_starts_daily(self):
        self.assertEqual(W.decide(NOW, ago(hours=26), ago(days=1), [run(hours=26)]), "daily")
        self.assertIsNone(W.decide(NOW, ago(hours=24), ago(days=1), [run(hours=24)]))  # 00:40 krug jos moze da kasni

    def test_stale_study_starts_weekly_before_daily(self):
        self.assertEqual(W.decide(NOW, ago(hours=30), ago(days=9), [run(hours=30)]), "weekly")
        self.assertIsNone(W.decide(NOW, ago(hours=2), ago(days=7), [run(hours=2)]))

    def test_missing_files_start_weekly(self):
        self.assertEqual(W.decide(NOW, None, None, []), "weekly")

    def test_never_starts_while_a_run_is_active_or_just_started(self):
        for st in ("queued", "in_progress", "waiting"):
            self.assertIsNone(W.decide(NOW, ago(hours=40), ago(days=20), [run(status=st, conclusion=None, minutes=3)]), st)
        self.assertIsNone(W.decide(NOW, ago(hours=40), ago(days=20), [run(hours=1)]))  # manje od 90 min od poslednjeg
        self.assertEqual(W.decide(NOW, ago(hours=40), ago(days=20), [run(hours=2)]), "weekly")

    def test_stops_after_three_failures_in_a_row(self):
        f = lambda h: run(conclusion="failure", hours=h)
        self.assertEqual(W.decide(NOW, ago(hours=40), ago(days=1), [f(3), f(5), run(hours=30)]), "daily")  # dva pada: jos jedan pokusaj
        self.assertIsNone(W.decide(NOW, ago(hours=40), ago(days=1), [f(3), f(5), f(7)]))  # tri pada: ceka coveka
        self.assertEqual(W.decide(NOW, ago(hours=40), ago(days=1), [f(3), f(5), run(hours=7), f(9)]), "daily")  # uspeh prekida niz

    def test_bad_timestamps_are_treated_as_missing(self):
        self.assertEqual(W.decide(NOW, "nije datum", ago(days=1), [run(hours=5)]), "daily")
        self.assertIsNone(W.parse(None))
        self.assertEqual(W.parse("2026-10-12T09:00:00Z"), NOW)


if __name__ == "__main__":
    unittest.main()
