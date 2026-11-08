import json
import os
import tempfile
import unittest

from lab import ic_track as IC

H = 3600000
T0 = 1790000000000 - (1790000000000 % (24 * H))  # pocetak UTC dana


def world(days=14, names=12, signal=True):
    """funding raste sa indeksom; prinos +24 h je obrnuto srazmeran fondingu (signal) ili nasumican."""
    inst, glob = {}, {}
    for h in range(days * 24):
        t = T0 + h * H
        inst[t] = {"S%d" % i: {"funding_h": 1e-5 * i, "premium": 0.0, "oi_usd": 1e6 * (i + 1), "vol24": 1e6} for i in range(names)}
        day = h // 24
        glob[t] = {"m": {"S%d" % i: 100.0 * (1.0 + ((-0.001 * i) if signal else 0.0) * (day + 1) + 0.001 * ((i * 7 + day * 3) % 5) * (0 if signal else 1)) for i in range(names)}}
    return inst, glob


class ICTests(unittest.TestCase):
    def test_spearman_basic(self):
        self.assertAlmostEqual(IC.spearman(list(range(10)), list(range(10))), 1.0)
        self.assertAlmostEqual(IC.spearman(list(range(10)), list(range(10, 0, -1))), -1.0)
        self.assertIsNone(IC.spearman([1, 2], [1, 2]))

    def test_daily_ics_find_the_planted_negative_funding_signal(self):
        inst, glob = world()
        daily = IC.daily_ics(inst, glob)
        self.assertTrue(daily)
        vals = [d["funding_h|24"] for d in daily.values() if "funding_h|24" in d]
        self.assertTrue(vals and all(v < -0.9 for v in vals))

    def test_summarize_needs_min_days_and_flags_fdr(self):
        daily = {"2026-10-%02d" % i: {"funding_h|24": -0.2 + 0.01 * (i % 3), "premium|24": 0.01 * ((-1) ** i)} for i in range(1, 25)}
        rows = IC.summarize(daily)
        self.assertEqual(rows[0]["feat"], "funding_h")
        self.assertTrue(rows[0]["fdr"])
        self.assertFalse([r for r in rows if r["feat"] == "premium"][0]["fdr"])
        self.assertEqual(IC.summarize({"2026-10-01": {"a|24": 0.1}}), [])

    def test_overlapping_72h_windows_are_penalised(self):
        daily = {"2026-10-%02d" % i: {"funding_h|24": -0.1 + 0.02 * (i % 4), "funding_h|72": -0.1 + 0.02 * (i % 4)} for i in range(1, 25)}
        rows = {r["h"]: r for r in IC.summarize(daily)}
        self.assertLess(abs(rows[72]["t"]), abs(rows[24]["t"]))

    def test_run_accumulates_and_never_raises(self):
        inst, glob = world(days=10)
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "data"))
            with open(os.path.join(d, "data", "panel_inst.jsonl"), "w") as f:
                for t, v in inst.items():
                    f.write(json.dumps({"t": t, "i": v}) + "\n")
            with open(os.path.join(d, "data", "panel_global.jsonl"), "w") as f:
                for t, v in glob.items():
                    f.write(json.dumps({"t": t, "m": v["m"], "f": {}}) + "\n")
            r1 = IC.run(d)
            self.assertIn("ok", r1)
            with open(os.path.join(d, "ic", "ic.json")) as f:
                a = json.load(f)
            IC.run(d)
            with open(os.path.join(d, "ic", "ic.json")) as f:
                b = json.load(f)
            self.assertEqual(a["n_days"], b["n_days"])
            self.assertEqual(IC.main(["--state", os.path.join(d, "nema")]), 0)


if __name__ == "__main__":
    unittest.main()
