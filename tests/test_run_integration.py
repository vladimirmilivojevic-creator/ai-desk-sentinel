"""Integracioni test: ceo krug straze sa lazim izvorima (bez mreze) za izmisljen sok nafte."""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sentinel import notify, run, sources  # noqa: E402
from sentinel.util import canon, sha12  # noqa: E402

EV_RE = re.compile(r"^EV-\d{8}T\d{4}Z-[A-Z0-9-]{3,24}$")


def fake_candles(coin, interval, minutes_back):
    now = time.time()
    base = {"xyz:BRENTOIL": 100.0, "xyz:CL": 90.0}.get(coin, 1000.0)
    shock = coin in ("xyz:BRENTOIL", "xyz:CL")
    out = []
    for k in range(60, -1, -1):
        t = now - k * 300
        # poslednjih 60 min: pad od 6% za naftu
        if shock and k <= 12:
            p = base * (1 - 0.06 * (12 - k) / 12.0)
        else:
            p = base
        out.append((t, p))
    return out


def fake_ctx(dex):
    names = ["xyz:BRENTOIL", "xyz:CL", "xyz:GOLD", "xyz:SP500", "xyz:XYZ100", "xyz:VIX", "xyz:DXY"] if dex else ["BTC", "ETH"]
    return {n: {"mark": 94.0 if n == "xyz:BRENTOIL" else (84.6 if n == "xyz:CL" else 1000.0), "prev_day": 100.0,
                "funding": 0.0001, "oi": 1e6} for n in names}


def fake_yahoo(symbol, interval="5m", rng="1d"):
    return [(t, p * (1 if symbol in ("BZ=F", "CL=F") else 1)) for t, p in fake_candles(
        "xyz:BRENTOIL" if symbol in ("BZ=F", "CL=F") else "x", "5m", 300)]


def fake_gnews(query):
    now = time.time()
    return [{"title": "War: missile strike on Hormuz tanker sends oil crude surge", "source": "Reuters", "ts": now - 300},
            {"title": "Hormuz blockade war fears as oil tanker attack escalates", "source": "BBC", "ts": now - 400}]


def fake_rss(url, name):
    return []


def fake_poly():
    return [{"id": "9", "q": "Will Iran strike oil tanker in Hormuz?", "p": 0.7, "vol24": 500000.0}]


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.state, self.root = os.path.join(self.tmp, "state"), os.path.join(self.tmp, "root")
        os.makedirs(self.state)
        os.makedirs(self.root)
        self.args = argparse.Namespace(state=self.state, root=self.root, dry=True, write_events=True, probe=False)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def patches(self):
        return [mock.patch.object(sources, "hl_ctx", fake_ctx), mock.patch.object(sources, "hl_candles", fake_candles),
                mock.patch.object(sources, "yahoo_series", fake_yahoo), mock.patch.object(sources, "gnews", fake_gnews),
                mock.patch.object(sources, "rss", fake_rss), mock.patch.object(sources, "polymarket", fake_poly)]

    def go(self):
        ps = self.patches()
        for p in ps:
            p.start()
        try:
            return run.run(self.args)
        finally:
            for p in ps:
                p.stop()

    def test_oil_shock_makes_event_and_second_round_is_quiet(self):
        # prediction istorija: trziste je pre 50 min bilo na 0.3
        os.makedirs(self.state, exist_ok=True)
        with open(os.path.join(self.state, "poly.json"), "w") as f:
            json.dump({"9": [[time.time() - 3000, 0.30]]}, f)
        self.assertEqual(self.go(), 0)
        files = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(self.root, "events")) for f in fs]
        self.assertEqual(len(files), 1, files)
        data = open(files[0], "rb").read()
        ev = json.loads(data)
        self.assertRegex(ev["id"], EV_RE)
        self.assertEqual(ev["theme"], "OIL")
        self.assertIn(ev["tier"], ("N2", "N3"))
        self.assertEqual(data, canon(ev))  # deterministicki bajtovi
        self.assertEqual(len(sha12(data)), 12)
        self.assertFalse(ev["brain_fired"])  # senka: fire_enabled=false
        self.assertTrue(ev["instruments"])
        # status i puls postoje
        st = json.load(open(os.path.join(self.state, "status", "latest.json"), encoding="utf-8"))
        self.assertEqual(st["themes"]["OIL"]["tier"], ev["tier"])
        self.assertTrue(st["events"])
        # drugi krug odmah posle: ista epizoda, bez novog dogadjaja
        self.go()
        files2 = [f for d, _, fs in os.walk(os.path.join(self.root, "events")) for f in fs]
        self.assertEqual(len(files2), 1)

    def test_fire_payload_has_only_ids_and_hash(self):
        captured = {}

        def fake_fire(payload, dry=False):
            captured.update(payload)
            return True, "okinuto"

        cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "sentinel.json")
        cfg = json.load(open(cfg_path, encoding="utf-8"))
        cfg["fire_enabled"] = True
        with mock.patch.object(run, "cfg_load", side_effect=lambda n: cfg if n == "sentinel.json" else json.load(
                open(os.path.join(os.path.dirname(cfg_path), n), encoding="utf-8"))), \
                mock.patch.object(notify, "fire_brain", fake_fire):
            with open(os.path.join(self.state, "poly.json"), "w") as f:
                json.dump({"9": [[time.time() - 3000, 0.30]]}, f)
            self.go()
        self.assertTrue(captured, "fire nije pozvan")
        self.assertEqual(set(captured), {"v", "tier", "event_ids", "sha12"})
        for eid in captured["event_ids"]:
            self.assertRegex(eid, EV_RE)
            self.assertEqual(len(captured["sha12"][eid]), 12)
        flat = json.dumps(captured)
        self.assertNotIn("Hormuz", flat)  # nikad tekst vesti


if __name__ == "__main__":
    unittest.main()
