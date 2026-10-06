"""Odlozeno okidanje mozga i izbor izvora za VIX. Bez mreze."""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sentinel import fire, notify, run, sources  # noqa: E402
from sentinel.util import iso, write_json  # noqa: E402

CFG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")


def candles(coin, interval, minutes_back):
    now = time.time()
    shock = coin in ("xyz:BRENTOIL", "xyz:CL")
    out = []
    for k in range(60, -1, -1):
        base = 100.0 if coin == "xyz:BRENTOIL" else (90.0 if coin == "xyz:CL" else 1000.0)
        p = base * (1 - 0.06 * (12 - k) / 12.0) if shock and k <= 12 else base
        out.append((now - k * 300, p))
    return out


def ctx(dex):
    names = ["xyz:BRENTOIL", "xyz:CL", "xyz:GOLD", "xyz:SP500", "xyz:XYZ100", "xyz:VIX", "xyz:DXY"] if dex else ["BTC", "ETH"]
    return {n: {"mark": 20.0 if n == "xyz:VIX" else (94.0 if n == "xyz:BRENTOIL" else 1000.0), "prev_day": 100.0,
                "funding": 0.0, "oi": 1.0} for n in names}


def yahoo(symbol, interval="5m", rng="1d"):
    now = time.time()
    px = 16.0 if symbol == "^VIX" else (100.0 if symbol in ("BZ=F", "CL=F") else 1000.0)
    if symbol in ("BZ=F", "CL=F"):
        return [(now - k * 300, px * (1 - 0.06 * (12 - k) / 12.0) if k <= 12 else px) for k in range(60, -1, -1)]
    return [(now - k * 300, px) for k in range(60, -1, -1)]


def gnews(q):
    now = time.time()
    return [{"title": "War: missile strike on Hormuz tanker sends oil crude surge", "source": "Reuters", "ts": now - 300},
            {"title": "Hormuz blockade war fears as oil tanker attack escalates", "source": "BBC", "ts": now - 400}]


def poly():
    return [{"id": "9", "q": "Will Iran strike oil tanker in Hormuz?", "p": 0.7, "vol24": 500000.0}]


class FireTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.state, self.root = os.path.join(self.tmp, "state"), os.path.join(self.tmp, "root")
        os.makedirs(self.state)
        os.makedirs(self.root)
        with open(os.path.join(self.state, "poly.json"), "w") as f:
            json.dump({"9": [[time.time() - 3000, 0.30]]}, f)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def go(self, fire_enabled=True, defer=True):
        cfg = json.load(open(os.path.join(CFG_DIR, "sentinel.json"), encoding="utf-8"))
        cfg["fire_enabled"] = fire_enabled

        def cfg_load(n):
            return cfg if n == "sentinel.json" else json.load(open(os.path.join(CFG_DIR, n), encoding="utf-8"))

        args = argparse.Namespace(state=self.state, root=self.root, dry=False, write_events=False, probe=False,
                                  defer_fire=defer)
        calls = []
        patches = [mock.patch.object(run, "cfg_load", side_effect=cfg_load),
                   mock.patch.object(sources, "hl_ctx", ctx), mock.patch.object(sources, "hl_candles", candles),
                   mock.patch.object(sources, "yahoo_series", yahoo), mock.patch.object(sources, "gnews", gnews),
                   mock.patch.object(sources, "rss", lambda u, n: []), mock.patch.object(sources, "polymarket", poly),
                   mock.patch.object(notify, "telegram", lambda t, dry=False: (True, "ok")),
                   mock.patch.object(notify, "fire_brain", lambda p, dry=False: (calls.append(p) or (True, "ok")))]
        for p in patches:
            p.start()
        try:
            run.run(args)
        finally:
            for p in patches:
                p.stop()
        return calls

    def test_run_defers_the_fire_and_does_not_call_the_brain(self):
        calls = self.go()
        self.assertEqual(calls, [], "run.py ne sme da okida mozak kad je defer_fire")
        pend = json.load(open(os.path.join(self.state, "pending_fire.json"), encoding="utf-8"))
        self.assertEqual(set(pend["payload"]), {"v", "tier", "event_ids", "sha12"})
        self.assertEqual(pend["attempts"], 0)

    def test_no_pending_fire_when_fire_disabled(self):
        self.go(fire_enabled=False)
        self.assertFalse(os.path.exists(os.path.join(self.state, "pending_fire.json")))

    def test_fire_module_posts_and_clears_queue(self):
        self.go()
        sent = []
        with mock.patch.object(notify, "fire_brain", lambda p, dry=False: (sent.append(p) or (True, "okinuto"))):
            self.assertEqual(fire.main(["--state", self.state]), 0)
        self.assertEqual(len(sent), 1)
        self.assertFalse(os.path.exists(os.path.join(self.state, "pending_fire.json")))
        self.assertTrue(os.path.exists(os.path.join(self.state, "last_fire.json")))

    def test_fire_failure_retries_then_drops(self):
        self.go()
        path = os.path.join(self.state, "pending_fire.json")
        with mock.patch.object(notify, "fire_brain", lambda p, dry=False: (False, "HTTP 500")), \
                mock.patch.object(notify, "telegram", lambda t, dry=False: (True, "ok")):
            fire.main(["--state", self.state])
            self.assertEqual(json.load(open(path))["attempts"], 1)
            fire.main(["--state", self.state])
            self.assertEqual(json.load(open(path))["attempts"], 2)
            fire.main(["--state", self.state])
        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists(os.path.join(self.state, "fire_dropped.json")))

    def test_stale_queue_is_dropped_without_firing(self):
        path = os.path.join(self.state, "pending_fire.json")
        write_json(path, {"payload": {"v": 1, "tier": "N3", "event_ids": ["EV-20261006T0000Z-OIL"], "sha12": {}},
                          "created": iso(time.time() - 3600), "attempts": 0})
        sent = []
        with mock.patch.object(notify, "fire_brain", lambda p, dry=False: (sent.append(p) or (True, "ok"))):
            fire.main(["--state", self.state])
        self.assertEqual(sent, [])
        self.assertFalse(os.path.exists(path))

    def test_vix_uses_yahoo_not_hyperliquid_scale(self):
        self.go(fire_enabled=False)
        st = json.load(open(os.path.join(self.state, "status", "latest.json"), encoding="utf-8"))
        vix = next(i for i in st["instruments"] if i["key"] == "VIX")
        self.assertEqual(vix["provider"], "yahoo")
        self.assertAlmostEqual(vix["px"], 16.0, places=1)  # pravi VIX, ne xyz:VIX = 20


if __name__ == "__main__":
    unittest.main()
