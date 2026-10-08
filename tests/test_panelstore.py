import json
import os
import random
import tempfile
import unittest

from lab import panel_scan, panelstore

HOUR = 3600 * 1000
T0 = 1_790_000_000_000 // HOUR * HOUR


def synth(days=12, planted=0.0, seed=1, syms=("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")):
    """Cene sa sumom; instrument sa visim x ima visi prinos u narednih 4 h za `planted` procenata. Vraca (g_rows, i_rows)."""
    rnd = random.Random(seed)
    n = days * 24 + 30
    xs = [{s: rnd.gauss(0, 1) for s in syms} for _ in range(n)]
    price = {s: 100.0 for s in syms}
    g, i = [], []
    for k in range(n):
        t = T0 + k * HOUR
        g.append({"t": t, "f": {"vix": 15.0 + rnd.random(), "mkt": float(k % 5)}, "m": {s: round(price[s], 6) for s in syms}})
        i.append({"t": t, "i": {s: {"x": xs[k][s]} for s in syms}})
        for s in syms:
            drift = planted * xs[k][s] / 4.0 if planted else 0.0  # 4 sata do kraja: ukupno planted * x
            price[s] *= 1 + (rnd.gauss(0, 0.3) + drift) / 100.0
    return g, i


class StoreTests(unittest.TestCase):
    def test_append_is_idempotent_and_trims(self):
        with tempfile.TemporaryDirectory() as d:
            panelstore.append_hour(d, T0, {"a": 1}, {"S": {"x": 1}}, {"S": 10.0})
            panelstore.append_hour(d, T0, {"a": 2}, {"S": {"x": 2}}, {"S": 11.0})
            g, i = panelstore.load(d)
            self.assertEqual(len(g), 1)
            self.assertEqual(g[0]["f"]["a"], 2)
            self.assertEqual(i[0]["i"]["S"]["x"], 2)
            late = T0 + (panelstore.KEEP_DAYS + 2) * 24 * HOUR
            panelstore.append_hour(d, late, {"a": 3}, {}, {"S": 12.0})
            g, _ = panelstore.load(d)
            self.assertEqual([r["t"] for r in g], [late])  # stariji od KEEP_DAYS je odsecen

    def test_seed_from_history_and_features(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "data")), os.makedirs(os.path.join(d, "lab"))
            json.dump([{"t": T0, "vix": 15.0, "m": {"BTC": 100.0}}, {"t": T0 + 1000, "vix": 1.0, "m": {"BTC": 1.0}}, {"t": T0 + HOUR, "vix": 16.0}], open(os.path.join(d, "data", "history.json"), "w"))
            with open(os.path.join(d, "lab", "features.jsonl"), "w") as f:
                f.write(json.dumps({"t": T0, "f": {"BTC": [100.0, 1e-5, 5e8, 0.0, 1e9]}}) + "\n")
            panelstore.append_hour(d, T0 + 2 * HOUR, {"vix": 17.0}, {"BTC": {"spread_bps": 1.0}}, {"BTC": 102.0})
            g, i = panelstore.load(d)
            self.assertEqual([r["t"] for r in g], [T0, T0 + 2 * HOUR])  # red bez cena i red koji nije pun sat se ne uzimaju
            self.assertEqual(g[0]["f"], {"vix": 15.0})
            self.assertEqual(i[0]["i"]["BTC"]["oi_usd"], 5e8)

    def test_dataset_labels_and_market_demeaning(self):
        g = [{"t": T0 + k * HOUR, "f": {}, "m": {"A": 100.0 * (1 + 0.01 * k), "B": 100.0}} for k in range(30)]
        rows = panelstore.dataset(g, [])
        r = next(x for x in rows if x["t"] == T0 + 2 * HOUR and x["sym"] == "A")
        self.assertAlmostEqual(r["y4"], (106.0 / 102.0 - 1) * 100, places=4)
        rb = next(x for x in rows if x["t"] == T0 + 2 * HOUR and x["sym"] == "B")
        self.assertAlmostEqual(r["yx4"] + rb["yx4"], 0.0, places=6)  # oduzet je prosek instrumenata
        self.assertIn("r1", r["x"])
        last = [x for x in rows if x["t"] == T0 + 29 * HOUR]
        self.assertEqual(last, [])  # nema ishoda jos


class ScanTests(unittest.TestCase):
    def test_too_few_days(self):
        g, i = synth(days=3)
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "data"))
            for name, rows in ((panelstore.G_FILE, g), (panelstore.I_FILE, i)):
                panelstore._write(os.path.join(d, "data", name), rows)
            res = panel_scan.run(d)
        self.assertTrue(res["status"].startswith("premalo"))

    def test_planted_feature_is_found_and_noise_is_not(self):
        g, i = synth(days=20, planted=1.5)
        rows = panelstore.dataset(g, i)
        ic = panel_scan.instrument_ic(rows)
        self.assertGreater(ic[("x", 4)]["t"], 6)
        g2, i2 = synth(days=20, planted=0.0, seed=5)
        ic2 = panel_scan.instrument_ic(panelstore.dataset(g2, i2))
        self.assertLess(abs(ic2[("x", 4)]["t"]), 3.5)

    def test_spearman_and_ties(self):
        self.assertAlmostEqual(panel_scan.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(panel_scan.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertIsNone(panel_scan.spearman([1, 1, 1], [1, 2, 3]))

    def test_run_writes_markdown_sections(self):
        g, i = synth(days=12)
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "data"))
            for name, rows in ((panelstore.G_FILE, g), (panelstore.I_FILE, i)):
                panelstore._write(os.path.join(d, "data", name), rows)
            res = panel_scan.run(d)
        self.assertEqual(res["status"], "ok")
        md = panel_scan.to_markdown(res)
        self.assertIn("Osobine po instrumentu", md)


if __name__ == "__main__":
    unittest.main()
