"""Testovi za sentinel/probe_sources.py (bez mreze)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sentinel import probe_sources as ps  # noqa: E402


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self._fetch = ps.fetch

    def tearDown(self):
        ps.fetch = self._fetch

    def test_endpoint_ids_unique_and_checks_callable(self):
        eps = ps.endpoints()
        ids = [e["id"] for e in eps]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(callable(e["check"]) for e in eps))
        self.assertGreaterEqual(len(eps), 20)

    def test_probe_ok_fail_and_skip(self):
        eps = {e["id"]: e for e in ps.endpoints()}
        ps.fetch = lambda ep, timeout=15: (200, json.dumps([{"a": 1}] * 80), None)
        self.assertTrue(ps.probe_one(eps["hl_predicted_fundings"])["ok"])
        ps.fetch = lambda ep, timeout=15: (200, "[]", None)
        r = ps.probe_one(eps["hl_predicted_fundings"])
        self.assertFalse(r["ok"])
        self.assertIn("oblik", r["note"])
        ps.fetch = lambda ep, timeout=15: (451, None, "HTTP 451")
        r = ps.probe_one(eps["binance_fapi_oi_hist"])
        self.assertEqual((r["ok"], r["status"]), (False, 451))
        ps.fetch = lambda ep, timeout=15: (None, None, "no_key")
        r = ps.probe_one(eps["coinalyze_exchanges"])
        self.assertIsNone(r["ok"])

    def test_malformed_body_is_a_failure_not_a_crash(self):
        eps = {e["id"]: e for e in ps.endpoints()}
        ps.fetch = lambda ep, timeout=15: (200, "not json", None)
        r = ps.probe_one(eps["fear_greed"])
        self.assertFalse(r["ok"])

    def test_key_is_added_to_request_but_never_to_result(self):
        os.environ["FINNHUB_API_KEY"] = "SECRET-TEST-KEY"
        try:
            ep = next(e for e in ps.endpoints() if e["id"] == "finnhub_earnings")
            captured = {}

            class FakeResp:
                status = 200

                def read(self, n=-1):
                    return json.dumps({"earningsCalendar": []}).encode()

                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    return False

            def fake_urlopen(req, timeout=15):
                captured["url"] = req.full_url
                return FakeResp()

            old = ps.urllib.request.urlopen
            ps.urllib.request.urlopen = fake_urlopen
            try:
                r = ps.probe_one(ep)
            finally:
                ps.urllib.request.urlopen = old
            self.assertIn("SECRET-TEST-KEY", captured["url"])
            self.assertNotIn("SECRET-TEST-KEY", json.dumps(r))
            self.assertTrue(r["ok"])
        finally:
            del os.environ["FINNHUB_API_KEY"]

    def test_run_summary_counts(self):
        ps.fetch = lambda ep, timeout=15: (None, None, "no_key") if ep.get("key_env") else (200, None, "HTTP 403")
        res = ps.run(timeout=1)
        self.assertEqual(res["skipped"], 2)
        self.assertEqual(res["ok"], 0)
        self.assertEqual(res["ok"] + res["failed"] + res["skipped"], len(res["results"]))


if __name__ == "__main__":
    unittest.main()
