import datetime as dt
import json
import math
import os
import tempfile
import unittest

from lab import core as K
from lab import sleeves as SL


def fake_prices(n=330, start="2026-01-01"):
    d0 = dt.date.fromisoformat(start)
    ds = [(d0 + dt.timedelta(days=i)).isoformat() for i in range(n)]
    out = {}
    for j, s in enumerate(["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "AVAX", "LINK", "LTC", "TRX", "XLM"]):
        p, rows = 100.0, []
        for i, d in enumerate(ds):
            p *= 1.0 + 0.002 * (1 if j % 2 == 0 else -1) + 0.01 * math.sin(i * (0.7 + j * 0.13))
            rows.append({"t": int(dt.datetime.fromisoformat(d).replace(tzinfo=dt.timezone.utc).timestamp() * 1000), "c": p})
        out[s] = rows
    return out, ds


class SleevesTests(unittest.TestCase):
    def test_config_is_valid_and_ids_unique(self):
        c = SL.load_cfg()
        ids = [s["id"] for s in c["sleeves"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in c["sleeves"]:
            self.assertIn(s["universe"], c["universes"])
            self.assertIn(s["mode"], ("trend", "csm", "fundrank"))
            self.assertLessEqual(s["target_vol"], 0.5)

    def test_run_writes_all_sleeves_and_skips_second_time(self):
        prices, ds = fake_prices()
        last = ds[-1]
        now_ms = int(dt.datetime.fromisoformat(last).replace(tzinfo=dt.timezone.utc).timestamp() * 1000) + 86400000 + 3600000
        scfg = SL.load_cfg()
        orig = SL.load_cfg
        SL.load_cfg = lambda: dict(scfg, t0_candle=ds[-20])
        try:
            with tempfile.TemporaryDirectory() as d:
                def fetch(coin, days, now):
                    if coin not in prices:
                        raise RuntimeError("nema")
                    return prices[coin]
                r = SL.run(d, now_ms, fetch, log=lambda *a: None)
                self.assertEqual(r["ok"], last)
                with open(os.path.join(d, "sleeves", "sleeves.json"), encoding="utf-8") as f:
                    out = json.load(f)
                self.assertEqual(len(out["sleeves"]), len(scfg["sleeves"]))
                s1 = [x for x in out["sleeves"] if x["id"] == "S03_trend_top6"][0]
                self.assertNotIn("error", s1)
                self.assertEqual(s1["days"], 19)
                self.assertIn("skipped", SL.run(d, now_ms, fetch, log=lambda *a: None))
        finally:
            SL.load_cfg = orig

    def test_publish_weights_adds_full_weights_only_for_flagged_sleeve(self):
        prices, ds = fake_prices()
        rows = {s: [(time_d, r["c"]) for time_d, r in zip(ds, v)] for s, v in prices.items()}
        now_ms = int(dt.datetime.fromisoformat(ds[-1]).replace(tzinfo=dt.timezone.utc).timestamp() * 1000) + 90000000
        scfg = {"t0_candle": ds[-20], "universes": {"major12": list(prices)},
                "sleeves": [{"id": "A", "text": "a", "universe": "major12", "mode": "trend", "lookbacks": [14, 28], "long_only": False, "target_vol": 0.2, "publish_weights": True},
                            {"id": "B", "text": "b", "universe": "major12", "mode": "trend", "lookbacks": [14, 28], "long_only": True, "target_vol": 0.2}]}
        out = {x["id"]: x for x in SL.compute_all(scfg, K.load_cfg(), rows, None, now_ms)}
        self.assertNotIn("error", out["A"])
        self.assertIsInstance(out["A"]["weights"], dict)
        self.assertTrue(out["A"]["weights"])
        self.assertTrue(any(v < 0 for v in out["A"]["weights"].values()))
        self.assertIn("weights_date", out["A"])
        self.assertNotIn("weights", out["B"])
        self.assertTrue([x for x in SL.load_cfg()["sleeves"] if x["id"] == "S13_fundfade_wide30_7d"][0].get("publish_weights"))

    def test_main_never_raises(self):
        with tempfile.TemporaryDirectory() as d:
            old = SL.core.fetch_rows
            SL.core.fetch_rows = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("mreza"))
            try:
                self.assertEqual(SL.main(["--state", d, "--force"]), 0)
            finally:
                SL.core.fetch_rows = old


if __name__ == "__main__":
    unittest.main()
