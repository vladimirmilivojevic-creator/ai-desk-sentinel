import unittest

from lab import ideas_verdict as V


def row(vid, test, n, mean, t, tt, te):
    return {"id": vid, "test": test, "stats": {"n": n, "mean": mean, "all": {"t": t}, "train": {"t": tt}, "test": {"t": te}}}


class IdeasVerdictTests(unittest.TestCase):
    def status(self):
        return {"ideas": [{"status": "u laboratoriji", "variant": "CAND_A"}, {"status": "u laboratoriji", "variant": "CAND_B"},
                          {"status": "u laboratoriji", "variant": "CAND_C"}, {"status": "u laboratoriji", "variant": "CAND_NEMA"},
                          {"status": "odbijeno", "reason": "x"}]}

    def test_need_only_when_an_imported_idea_has_no_history(self):
        s = self.status()
        self.assertTrue(V.need(s))
        for i in s["ideas"]:
            if i["status"] == "u laboratoriji":
                i["history"] = {"verdict": "x"}
        self.assertFalse(V.need(s))
        self.assertFalse(V.need({"ideas": [{"status": "odbijeno"}]}))

    def test_verdicts_use_excess_over_basket_and_both_halves(self):
        bt = {"generated_utc": "2026-11-16T05:00:00Z", "days": 200, "cost_pct": 0.23, "k_tests": 280, "bonferroni_z": 3.7,
              "results": [row("CAND_A", "H24", 500, 0.9, 4.0, 3.0, 2.0), row("CAND_A", "E24", 500, 0.3, 2.6, 1.2, 1.9),      # dobar: preko korpe pozitivan
                          row("CAND_B", "H24", 500, 0.9, 4.0, 3.0, 2.0), row("CAND_B", "E24", 500, -0.1, -0.8, 0.5, -1.0),   # sirovo dobar, preko korpe nije
                          row("CAND_C", "E24", 40, 0.5, 2.5, 1.0, 1.0),                                                       # premalo signala
                          row("MOM_L1_z1.5", "E24", 900, 0.2, 3.0, 1.0, 1.0)]}
        s = self.status()
        self.assertEqual(V.merge(s, bt), 3)
        by = {i.get("variant"): i for i in s["ideas"]}
        self.assertTrue(by["CAND_A"]["history"]["verdict"].startswith("nagovestaj"))
        self.assertTrue(by["CAND_B"]["history"]["verdict"].startswith("palo"))
        self.assertTrue(by["CAND_C"]["history"]["verdict"].startswith("premalo"))
        self.assertNotIn("history", by["CAND_NEMA"])
        self.assertEqual(by["CAND_A"]["history"]["test"], "E24")
        self.assertEqual(by["CAND_A"]["history"]["k_tests"], 280)
        self.assertIn("280", s["history_note"])
        self.assertTrue(V.need(s))  # CAND_NEMA jos nema presudu

    def test_one_half_negative_fails_even_with_high_total_t(self):
        v = V.verdict_of([row("X", "E24", 500, 0.4, 3.1, 4.0, -0.5)])
        self.assertTrue(v["verdict"].startswith("palo"))
        self.assertIn("nema", V.verdict_of([row("X", "H24", 500, 0.4, 3.1, 4.0, 0.5)])["verdict"])


if __name__ == "__main__":
    unittest.main()
