import datetime as dt
import json
import os
import random
import tempfile
import unittest

from lab import trump, trump_study as ts

HOUR = 3600 * 1000
LEX = trump.load_lexicon()

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:truth="https://truthsocial.com/ns"><channel>
<item><title>x</title><description><![CDATA[<p>New TARIFFS on China starting Monday! Very good deal for Intel.</p>]]></description>
<guid>https://www.trumpstruth.org/statuses/2</guid><pubDate>Thu, 08 Oct 2026 12:29:08 +0000</pubDate>
<truth:originalId>1002</truth:originalId></item>
<item><title>x</title><description><![CDATA[<p>RT @someone: tariffs are great</p>]]></description>
<guid>https://www.trumpstruth.org/statuses/1</guid><pubDate>Thu, 08 Oct 2026 03:54:44 +0000</pubDate>
<truth:originalId>1001</truth:originalId></item>
<item><title>x</title><description><![CDATA[<p></p>]]></description>
<guid>https://www.trumpstruth.org/statuses/0</guid><pubDate>Wed, 07 Oct 2026 20:00:00 +0000</pubDate>
<truth:originalId>1000</truth:originalId></item>
</channel></rss>"""


def ms(s):
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


class TaggingTests(unittest.TestCase):
    def test_topics_companies_and_repost(self):
        t = trump.tag_text("New TARIFFS on China starting Monday! Very good deal for Intel.", LEX)
        self.assertEqual(sorted(t["topics"]), ["china", "deal", "tariff"])
        self.assertEqual(t["companies"], ["intel"])
        self.assertFalse(t["rt"])
        rt = trump.tag_text("RT @someone: tariffs are great", LEX)
        self.assertTrue(rt["rt"])
        self.assertEqual(rt["topics"], [])

    def test_shout_needs_enough_letters_and_upper_ratio(self):
        self.assertTrue(trump.tag_text("THIS IS A VERY LOUD AND LONG MESSAGE TO EVERYONE", LEX)["shout"])
        self.assertFalse(trump.tag_text("WOW", LEX)["shout"])
        self.assertFalse(trump.tag_text("This is a quiet and long message to everybody here", LEX)["shout"])

    def test_empty_text_has_no_tags(self):
        t = trump.tag_text("", LEX)
        self.assertEqual((t["topics"], t["companies"], t["shout"]), ([], [], False))


class FeedTests(unittest.TestCase):
    def test_parse_feed_has_no_text_and_sorted_newest_first(self):
        ev = trump.parse_feed(RSS, LEX)
        self.assertEqual([e["id"] for e in ev], ["1002", "1001", "1000"])
        self.assertTrue(all("text" not in e and "content" not in e for e in ev))
        self.assertEqual(ev[0]["ts_ms"], ms("2026-10-08T12:29:08Z"))
        self.assertTrue(ev[1]["rt"])

    def test_summarize_counts_only_own_posts(self):
        ev = trump.parse_feed(RSS, LEX)
        now = ms("2026-10-08T13:00:00Z")
        s = trump.summarize(ev, now)
        self.assertEqual((s["posts_1h"], s["posts_24h"], s["rt_24h"]), (1, 2, 1))
        self.assertEqual(s["topics_24h"]["tariff"], 1)
        self.assertEqual(s["last_age_min"], 30.9)


class ReactionTests(unittest.TestCase):
    def setUp(self):
        self.ev = [{"id": "1", "ts_ms": ms("2026-10-08T12:29:00Z"), "topics": ["tariff"], "companies": [], "shout": False, "rt": False},
                   {"id": "2", "ts_ms": ms("2026-10-08T12:50:00Z"), "topics": ["tariff"], "companies": [], "shout": False, "rt": False}]

    def test_one_event_per_topic_and_day_entry_and_fills(self):
        store = {}
        # 12:29 -> prvi pun sat najmanje 55 min kasnije = 14:00
        trump.update_reactions(store, self.ev, {"BTC": 100.0}, ms("2026-10-08T12:30:00Z"), ["BTC"])
        self.assertEqual(len(store["events"]), 1)
        rec = next(iter(store["events"].values()))
        self.assertEqual(rec["entry_t"], ms("2026-10-08T14:00:00Z"))
        self.assertIsNone(rec["entry"])
        trump.update_reactions(store, self.ev, {"BTC": 100.0}, ms("2026-10-08T14:05:00Z"), ["BTC"])
        self.assertEqual(rec["entry"], {"BTC": 100.0})
        trump.update_reactions(store, self.ev, {"BTC": 101.0}, ms("2026-10-08T15:05:00Z"), ["BTC"])
        self.assertEqual(rec["out"]["1"], {"BTC": 1.0})
        trump.update_reactions(store, self.ev, {"BTC": 98.0}, ms("2026-10-08T18:05:00Z"), ["BTC"])
        self.assertEqual(rec["out"]["4"], {"BTC": -2.0})
        self.assertNotIn("24", rec["out"])
        trump.update_reactions(store, self.ev, {"BTC": 110.0}, ms("2026-10-09T14:05:00Z"), ["BTC"])
        self.assertEqual(rec["out"]["24"], {"BTC": 10.0})
        self.assertEqual(len(store["events"]), 1)  # druga objava iste teme istog dana ne pravi novi dogadjaj

    def test_missed_entry_is_not_recorded(self):
        store = {}
        trump.update_reactions(store, self.ev, {"BTC": 100.0}, ms("2026-10-08T20:00:00Z"), ["BTC"])
        self.assertEqual(store.get("events"), {})

    def test_reposts_never_make_events(self):
        store = {}
        trump.update_reactions(store, [dict(self.ev[0], rt=True)], {"BTC": 100.0}, ms("2026-10-08T12:30:00Z"), ["BTC"])
        self.assertEqual(store.get("events"), {})

    def test_collect_trump_roundtrip_with_fake_feed(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ev.json")
            now = ms("2026-10-08T12:40:00Z")
            out = trump.collect_trump(now, lex=LEX, fetch=lambda: RSS, store_path=path, instruments=["BTC"], marks={"BTC": 100.0})
            self.assertEqual(out["posts_24h"], 2)
            self.assertEqual(out["n_events"], 4)  # jedna objava: tariff, china, deal + kompanija intel; repost i prazna objava nemaju oznake
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
            self.assertNotIn("Intel", raw)
            self.assertNotIn("TARIFFS", raw)
            self.assertEqual(json.loads(raw)["events"].keys().__len__(), out["n_events"])

    def test_collect_trump_fails_on_empty_feed(self):
        with self.assertRaises(Exception):
            trump.collect_trump(1, lex=LEX, fetch=lambda: '<rss version="2.0"><channel></channel></rss>')


def synthetic(seed, planted, days=500, n_ev=80):
    """Satne svece (otvaranja) za `days` dana sa sumom 0,2% po satu; planted = skok posle ulaza u svaki dogadjaj."""
    rnd = random.Random(seed)
    start = ms("2025-01-20T00:00:00Z")
    n = days * 24
    t = [start + i * HOUR for i in range(n)]
    rets = [rnd.gauss(0, 0.2) for _ in range(n)]
    ev_days = sorted(rnd.sample(range(10, days - 10), n_ev))
    posts, entry_idx = [], []
    for d in ev_days:
        post_ts = start + d * 24 * HOUR + 12 * HOUR + 10 * 60000
        posts.append({"ts": post_ts, "topics": ["tariff"], "companies": [], "shout": False})
        entry_idx.append(d * 24 + 14)  # prvi sat >= 13:10 je 14:00
    if planted:
        for i in entry_idx:
            rets[i] += planted
    o = [100.0]
    for r in rets[:-1]:
        o.append(o[-1] * (1 + r / 100.0))
    return ts.Bars(t, o), posts, start, start + n * HOUR


class StudyTests(unittest.TestCase):
    def run_cell(self, planted, seed):
        b, posts, start, end = synthetic(seed, planted)
        ctrl = ts.Control(b, 1, start, end)
        times = ts.event_times(posts, lambda p: "tariff" in p["topics"], start, end)
        return ts.summarize_cell(*ts.cell(b, ctrl, times, 1, True)[:2])

    def test_planted_effect_is_detected(self):
        s = self.run_cell(1.0, 3)
        self.assertGreater(s["t"], 8)
        self.assertTrue(s["stable"])
        self.assertAlmostEqual(s["mean"], 1.0, delta=0.25)

    def test_pure_noise_is_usually_insignificant(self):
        big = sum(1 for seed in range(12) if abs(self.run_cell(0.0, seed)["t"]) > 3)
        self.assertLessEqual(big, 1)

    def test_empirical_p_uses_placebo_distribution(self):
        null = sorted([0.1, 0.5, 1.0, 1.5, 2.5])
        self.assertAlmostEqual(ts.emp_p(2.0, null), (1 + 1) / 6.0)
        self.assertAlmostEqual(ts.emp_p(-9.0, null), 1 / 6.0)

    def test_too_few_events_gives_no_cell(self):
        self.assertIsNone(ts.summarize_cell([0.1] * 10, [0.1] * 10))

    def test_gap_rejects_closed_market(self):
        b = ts.Bars([ms("2025-03-03T14:30:00Z"), ms("2025-03-03T15:30:00Z"), ms("2025-03-04T14:30:00Z")], [100.0, 101.0, 103.0])
        self.assertAlmostEqual(ts.fwd_ret(b, 0, 1), 1.0)
        self.assertIsNone(ts.fwd_ret(b, 1, 1))  # sledeca sveca je 23 h kasnije


if __name__ == "__main__":
    unittest.main()
