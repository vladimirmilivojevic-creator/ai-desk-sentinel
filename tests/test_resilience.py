"""Otpornost: izvori padaju, stanje je pokvareno, dnevni pregled i dnevni log. Bez mreze."""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sentinel import notify, run, sources  # noqa: E402
from sentinel.util import SourceError  # noqa: E402


def boom(*a, **k):
    raise SourceError("HTTP 500")


class ResilienceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.state, self.root = os.path.join(self.tmp, "state"), os.path.join(self.tmp, "root")
        os.makedirs(self.state)
        os.makedirs(self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def args(self, dry=True):
        return argparse.Namespace(state=self.state, root=self.root, dry=dry, write_events=False, probe=False)

    def patch_all_fail(self):
        return [mock.patch.object(sources, n, boom) for n in
                ("hl_ctx", "hl_candles", "yahoo_series", "gnews", "rss", "polymarket", "gdelt_timeline")]

    def go(self, args, patches):
        for p in patches:
            p.start()
        try:
            return run.run(args)
        finally:
            for p in patches:
                p.stop()

    def status(self):
        return json.load(open(os.path.join(self.state, "status", "latest.json"), encoding="utf-8"))

    def test_all_sources_down_still_writes_heartbeat_and_degrades(self):
        for _ in range(3):
            self.assertEqual(self.go(self.args(), self.patch_all_fail()), 0)
        st = self.status()
        self.assertTrue(all(i["stale"] for i in st["instruments"]))
        self.assertTrue(st["degraded"], "izvori treba da budu degradirani posle 3 pada")
        self.assertTrue(all(t["tier"] is None for t in st["themes"].values()))  # bez cena nema nivoa
        self.assertTrue(os.path.exists(os.path.join(self.state, "heartbeat.json")))
        # nema dogadjaja
        self.assertFalse(os.path.exists(os.path.join(self.root, "events")))

    def test_degraded_alert_sent_once_not_in_dry(self):
        sent = []
        with mock.patch.object(notify, "telegram", lambda t, dry=False: (sent.append(t) or (True, "ok"))):
            for _ in range(4):
                self.go(self.args(dry=False), self.patch_all_fail())
        self.assertEqual(sum("ne rade 3 puta" in t for t in sent), 1, sent)

    def test_corrupt_state_files_are_ignored(self):
        for name in ("health", "prices", "episodes", "poly", "meta", "vol", "events_recent", "firelog", "runlog"):
            with open(os.path.join(self.state, name + ".json"), "w") as f:
                f.write("{ovo nije json")
        self.assertEqual(self.go(self.args(), self.patch_all_fail()), 0)
        self.assertIn("instruments", self.status())

    def test_digest_once_per_day_and_log_rollover(self):
        sent = []
        day1 = dt.datetime(2026, 10, 6, 9, 0, tzinfo=dt.timezone.utc).timestamp()
        day2 = dt.datetime(2026, 10, 7, 9, 0, tzinfo=dt.timezone.utc).timestamp()
        with mock.patch.object(notify, "telegram", lambda t, dry=False: (sent.append(t) or (True, "ok"))):
            for now in (day1, day1 + 300, day2):
                with mock.patch.object(run.time, "time", return_value=now):
                    self.go(self.args(dry=False), self.patch_all_fail())
        digests = [t for t in sent if "dnevni pregled" in t]
        self.assertEqual(len(digests), 2, sent)  # jedan po danu
        # prelazak na novi dan upisuje log prethodnog dana
        log = os.path.join(self.root, "log", "2026-10-06.jsonl")
        self.assertTrue(os.path.exists(log))
        lines = [json.loads(x) for x in open(log, encoding="utf-8") if x.strip()]
        self.assertEqual(len(lines), 2)

    def test_partial_failure_yahoo_down(self):
        import time as _t

        def candles(coin, interval, minutes_back):
            now = _t.time()
            return [(now - k * 300, 100.0) for k in range(60, -1, -1)]

        def ctx(dex):
            names = ["xyz:BRENTOIL", "xyz:CL", "xyz:GOLD", "xyz:SP500", "xyz:XYZ100", "xyz:VIX", "xyz:DXY"] if dex else ["BTC", "ETH"]
            return {n: {"mark": 100.0, "prev_day": 100.0, "funding": 0.0, "oi": 1.0} for n in names}

        ps = [mock.patch.object(sources, "hl_ctx", ctx), mock.patch.object(sources, "hl_candles", candles),
              mock.patch.object(sources, "yahoo_series", boom), mock.patch.object(sources, "gnews", boom),
              mock.patch.object(sources, "rss", boom), mock.patch.object(sources, "polymarket", boom)]
        self.assertEqual(self.go(self.args(), ps), 0)
        st = self.status()
        live = [i for i in st["instruments"] if not i["stale"]]
        self.assertTrue(live)
        self.assertTrue(all(abs(i["m60"]) < 0.01 for i in live if i["m60"] is not None))


if __name__ == "__main__":
    unittest.main()
