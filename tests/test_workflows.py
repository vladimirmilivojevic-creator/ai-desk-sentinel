"""Zastita od nevazecih workflow fajlova. 2026-10-12 je ime koraka sa dvotackom ('senka: samo ...') obaralo celu strazu 15 minuta,
jer GitHub tada ne pokrece nijedan krug (ni zakazani ni rucni). Testovi su bez mreze; PyYAML se koristi samo ako je instaliran."""
import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")))
KEY = re.compile(r"^(\s*)(-\s+)?([A-Za-z_][A-Za-z0-9_-]*):\s+(.*?)\s*$")


class WorkflowTests(unittest.TestCase):
    def test_there_are_workflows(self):
        self.assertTrue(FILES)

    def test_no_tabs_and_no_unquoted_colon_space_in_single_line_values(self):
        for path in FILES:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
            block = None  # indeks uvlacenja bloka (run: |) cije linije se ne proveravaju
            for n, line in enumerate(lines, 1):
                self.assertNotIn("\t", line, "%s:%d tab u uvlacenju" % (os.path.basename(path), n))
                if block is not None:
                    if line.strip() and len(line) - len(line.lstrip()) <= block:
                        block = None
                    else:
                        continue
                m = KEY.match(line)
                if not m or line.lstrip().startswith("#"):
                    continue
                indent, dash, key, val = m.group(1), m.group(2) or "", m.group(3), m.group(4)
                if val[:1] in ("|", ">"):
                    block = len(indent) + len(dash)
                    continue
                if not val or val[0] in "\"'[{&*!%@`":
                    continue
                val = re.sub(r"\s+#.*$", "", val)  # komentar na kraju reda
                self.assertNotIn(": ", val, "%s:%d vrednost '%s' ima ': ' bez navodnika (YAML greska)" % (os.path.basename(path), n, key))

    def test_parses_with_yaml_when_available(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML nije instaliran")
        for path in FILES:
            with open(path, encoding="utf-8") as f:
                doc = yaml.safe_load(f)
            self.assertIn("jobs", doc, os.path.basename(path))
            self.assertTrue(doc.get("on") or doc.get(True), "%s: nema 'on'" % os.path.basename(path))  # PyYAML cita 'on' kao True


if __name__ == "__main__":
    unittest.main()
