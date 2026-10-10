import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab import panelpack as P  # noqa: E402


def merge(parts):
    """Isto sto radi panel (JS): liste se nadovezuju, recnici spajaju, ostalo se prepisuje."""
    out = {}
    for p in parts:
        for k, v in p.items():
            if isinstance(v, list) and isinstance(out.get(k), list):
                out[k] = out[k] + v
            elif isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = dict(out[k], **v)
            else:
                out[k] = v
    return out


class PackTests(unittest.TestCase):
    def test_every_part_is_under_the_limit_and_nothing_is_lost(self):
        sections = [("small", {"a": 1}), ("big_list", [{"i": i, "pad": "x" * 200} for i in range(100)]), ("big_dict", {"k%d" % i: {"v": "y" * 150} for i in range(80)}), ("tail", "kraj")]
        parts = P.pack(sections, limit=2000)
        self.assertGreater(len(parts), 5)
        for p in parts:
            self.assertLessEqual(P.size(p), 2000)
        m = merge(parts)
        self.assertEqual(m["small"], {"a": 1})
        self.assertEqual(len(m["big_list"]), 100)
        self.assertEqual([x["i"] for x in m["big_list"]], list(range(100)))  # redosled sacuvan
        self.assertEqual(len(m["big_dict"]), 80)
        self.assertEqual(m["tail"], "kraj")

    def test_indivisible_oversize_value_raises(self):
        with self.assertRaises(ValueError):
            P.pack([("txt", "z" * 3000)], limit=2000)
        with self.assertRaises(ValueError):
            P.pack([("lst", [{"pad": "q" * 3000}])], limit=2000)

    def test_write_parts_replaces_stale_files_and_checks_slots(self):
        with tempfile.TemporaryDirectory() as d:
            P.write_parts(d, "lab", [{"a": 1}, {"b": 2}, {"c": 3}])
            self.assertEqual(sorted(os.listdir(d)), ["lab.0.json", "lab.1.json", "lab.2.json"])
            P.write_parts(d, "lab", [{"a": 1}])
            self.assertEqual(os.listdir(d), ["lab.0.json"])  # stari delovi uklonjeni
            with self.assertRaises(ValueError):
                P.write_parts(d, "trig", [{}] * 9)


class BuildTests(unittest.TestCase):
    def state(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "lab"))
        os.makedirs(os.path.join(d, "data"))
        panel = {"updated_utc": "2026-10-08T14:00:00Z", "t0_utc": "2026-10-07T01:00:00Z", "hours_running": 37.0, "universe_n": 31, "totals": {"signals": 3825, "outcomes_h24": 451, "variants": 68},
                 "cost_pct": 0.23, "features_rows": 37, "backtest_counts": {"slabo": 12}, "demoted": {}, "placebo": {"hourly_bt": {"mean": -0.26}},
                 "live": [{"id": "R%d" % i, "hold_hours": 24, "why": "w" * 300, "bt": {"n": 10, "mean": 0.1, "t": 1.0, "verdict": "odbaceno"}, "fwd": {"n": 3, "mean": 0.2}, "signals": 4, "test": "E24"} for i in range(9)],
                 "top_backtest": [{"id": "T%d" % i, "test": "E7", "n": 100, "mean": 0.5, "t": 2.0, "t_train": 1.0, "t_test": 1.0, "verdict": "slabo"} for i in range(12)],
                 "history": [[1791334800000 + i * 3600000, 100 + i, i, 3, -0.1, 0.1] for i in range(168)],
                 "registry": {"generated_utc": "x", "gates_version": 1, "counts": {"odbacen": 56},
                              "rules": [{"id": "D_RULE_%d" % i, "interval": "1d", "status": "odbacen", "test": "E7", "n": 500, "mean": 0.1, "t": 1.0, "recent_mean": 0.0, "t_train": 1.0, "t_test": 1.0,
                                         "edge_groups": ["crypto"], "unmet": ["t 1.0 < 2.0", "ne prolazi FDR 10%", "treci"], "live": False} for i in range(30)]}}
        json.dump(panel, open(os.path.join(d, "lab", "panel.json"), "w"))
        json.dump({"updated_utc": "u", "bar_utc": "b", "marks": {"S%d" % i: 100.0 + i for i in range(31)}, "live_variants": {"A": 24},
                   "triggers": [{"variant": "V", "sym": "S%d" % i, "side": "long", "stop_pct": 1.0, "tp_pct": 2.0, "hold_hours": 24, "interval": "1h", "bt_verdict": "odbaceno", "live": i % 2 == 0, "px": 1.0} for i in range(60)]},
                  open(os.path.join(d, "lab", "triggers.json"), "w"))
        json.dump({"updated_utc": "u", "regime": {"label": "risk_on"}, "scalars": {"vix": 15.7}, "calendar_next_72h": [{"ts": "t", "title": "T" * 40}] * 12, "extra": {"fed": {"p_up": 0.1}},
                   "macro": {"M%d" % i: {"last": 1.0, "chg_1d_pct": 0.1, "chg_5d_pct": 0.2, "chg_20d_pct": 0.3} for i in range(19)}, "evidence": {"tests": 117, "findings": []}},
                  open(os.path.join(d, "data", "briefing.json"), "w"))
        json.dump({"updated_utc": "u", "n": 259, "features": {"f%d" % i: {"v": 1.5, "z": 0.2} for i in range(259)}, "meta": {"f%d" % i: ["Makro", "Opis osobine broj %d" % i] for i in range(259)}},
                  open(os.path.join(d, "data", "features.json"), "w"))
        return d

    def test_build_makes_small_parts_that_reassemble(self):
        d = self.state()
        res = P.build(d, root=tempfile.mkdtemp())  # prazan koren: bez Lovca
        self.assertEqual(set(res), {"lab", "brief", "trig", "feat"})
        for f in os.listdir(os.path.join(d, "pf")):
            self.assertLessEqual(os.path.getsize(os.path.join(d, "pf", f)), 6000, f)  # granica alata read_link
        for name in res:
            self.assertLessEqual(res[name], P.SLOTS[name])
        lab = merge([json.load(open(os.path.join(d, "pf", "lab.%d.json" % i))) for i in range(res["lab"])])
        self.assertEqual(lab["head"]["totals"]["signals"], 3825)
        self.assertEqual(len(lab["live"]), 9)
        self.assertEqual(len(lab["registry_rules"]), 30)
        self.assertLessEqual(len(lab["history"]), 72)
        trig = merge([json.load(open(os.path.join(d, "pf", "trig.%d.json" % i))) for i in range(res["trig"])])
        self.assertTrue(all(x["live"] for x in trig["triggers"]))
        self.assertEqual(len(trig["marks"]), 31)
        feat = merge([json.load(open(os.path.join(d, "pf", "feat.%d.json" % i))) for i in range(res["feat"])])
        self.assertEqual(len(feat["rows"]), 259)
        self.assertEqual(feat["rows"][0][0:2], ["f0", "Makro"])

    def test_missing_inputs_are_skipped_and_main_never_raises(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as root:
            self.assertEqual(P.build(d, root=root), {})
            sys.argv = ["panelpack", "--state", d]
            self.assertEqual(P.main(), 0)

    def test_discovery_document_is_packed_small_and_complete(self):
        d, root = self.state(), tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "discovery"))
        os.makedirs(os.path.join(root, "calibration"))
        rules = {"stocks:SPIKE_UP:10d:long": {"status": "nagovestaj", "forward_start": "2026-09-28", "study": {"n": 90, "mean": 5.7, "median": -0.9, "mean_ex_best": 3.0, "t": 2.9, "p": 0.004, "recent_mean": -0.4},
                                              "forward": {"n": 0, "mean": None, "t": None, "sim_mean": None, "mean_ex_best": None, "pending": 1}}}
        json.dump({"updated_utc": "2026-10-10T00:40:00Z", "rules": rules}, open(os.path.join(root, "discovery", "rules.json"), "w"))
        json.dump({"generated_utc": "g", "rules": [{"rule": "stocks:SPIKE_UP:10d:long", "status": "nagovestaj", "side": "long", "signal_date": "2026-10-09", "valid_from_utc": "a", "valid_until_utc": "b",
                                                    "hold_hours": 336, "picks": [{"ticker": "GME", "px": 25.0, "stop_pct": 5.0, "tp_pct": 15.0, "score": 4.0, "symbol": "xyz:GME"}]}]},
                  open(os.path.join(root, "discovery", "radar.json"), "w"))
        tests = [{"id": "t%d" % i, "n": 50, "mean": 0.1 * i, "median": 0.0, "mean_ex_best": 0.0, "t": float(i), "status": "odbaceno"} for i in range(60)]
        json.dump({"generated_utc": "g", "tests": tests, "universes": {"stocks": {"n": 47, "from": "2020", "to": "2026"}}, "cfg_summary": {"fdr_q": 0.1}, "cases": [{"sym": "GME", "entry": "2026-10-03", "profile": {"date": "d", "families": {}, "events": []}}]},
                  open(os.path.join(root, "calibration", "discovery.json"), "w"))
        res = P.build(d, root=root)
        self.assertIn("disc", res)
        self.assertLessEqual(res["disc"], P.SLOTS["disc"])
        for f in os.listdir(os.path.join(d, "pf")):
            self.assertLessEqual(os.path.getsize(os.path.join(d, "pf", f)), 6000, f)
        m = merge([json.load(open(os.path.join(d, "pf", "disc.%d.json" % i))) for i in range(res["disc"])])
        self.assertEqual(m["head"]["n_tests"], 60)
        self.assertEqual(m["head"]["rule_counts"], {"nagovestaj": 1})
        self.assertEqual(len(m["top"]), 10)
        self.assertEqual(m["top"][0]["id"], "t59")
        self.assertEqual(m["radar"][0]["picks"][0]["ticker"], "GME")
        self.assertEqual(m["rules"][0]["fwd"]["pending"], 1)
        self.assertEqual(m["cases"][0]["sym"], "GME")


if __name__ == "__main__":
    unittest.main()
