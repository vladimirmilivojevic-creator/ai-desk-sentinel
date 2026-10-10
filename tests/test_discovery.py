import datetime as dt
import json
import os
import random
import tempfile
import unittest

from lab import discovery as D

CFG = D.load_cfg()
UCFG = CFG["universes"]["stocks"]


def weekdays(start="2023-01-02", n=900):
    d0 = dt.date.fromisoformat(start)
    out, k = [], 0
    while len(out) < n:
        d = d0 + dt.timedelta(days=k)
        k += 1
        if d.weekday() < 5:
            out.append(d.isoformat())
    return out


def mk_bars(days, rets, vols=None, p0=100.0, gap=0.0):
    """Svece iz niza dnevnih prinosa: otvaranje = prethodno zatvaranje (plus gap), high/low +-0.5%."""
    d, o, h, l, c, v, rc = [], [], [], [], [], [], []
    prev = p0
    for i, day in enumerate(days):
        op = prev * (1 + gap)
        cl = prev * (1 + rets[i])
        d.append(day)
        o.append(op)
        h.append(max(op, cl) * 1.005)
        l.append(min(op, cl) * 0.995)
        c.append(cl)
        v.append(1e6 if vols is None else vols[i])
        rc.append(cl)
        prev = cl
    return {"d": d, "o": o, "h": h, "l": l, "c": c, "v": v, "rc": rc}


def mk_universe(seed=1, n_sym=16, days=900, drift=None, noise=0.01, start="2023-01-02", spikes=None, post=0.0, cal=None):
    """spikes: (simbol, indeks, prinos, mnozilac obima); post = dodatni dnevni prinos u 10 dana posle skoka (nastavak)."""
    rnd = random.Random(seed)
    cal = cal or weekdays(start, days)
    px = {}
    for k in range(n_sym):
        mu = 0.0 if drift is None else drift[k]
        rets = [mu + rnd.gauss(0, noise) for _ in cal]
        vols = [1e6 * (1 + 0.1 * rnd.random()) for _ in cal]
        for (sk, i, r, vm) in (spikes or []):
            if sk == k:
                rets[i], vols[i] = r, 1e6 * vm
                for q in range(1, 11):
                    if i + q < len(cal):
                        rets[i + q] += post
        px["S%02d" % k] = mk_bars(cal, rets, vols)
    bench = mk_bars(cal, [rnd.gauss(0, 0.005) for _ in cal])
    return px, bench


def uni(px, bench):
    return D.Universe("stocks", px, bench, UCFG, CFG)


class FeatureTests(unittest.TestCase):
    def test_family_scores_use_only_past_and_have_known_values(self):
        days = weekdays(n=300)
        rets = [0.0] + [0.01] * 299
        b = mk_bars(days, rets)
        f = D.features(b, CFG)
        i = 280
        self.assertAlmostEqual(f["MOM12_1"][i], b["c"][i - 21] / b["c"][i - 252] - 1.0, places=9)
        self.assertAlmostEqual(f["HIGH52"][i], 1.0, places=9)  # stalan rast: uvek na maksimumu
        self.assertAlmostEqual(f["REV5"][i], -(b["c"][i] / b["c"][i - 5] - 1.0), places=9)
        self.assertAlmostEqual(f["BRK20"][i], b["c"][i] / max(b["c"][i - 20:i]) - 1.0, places=9)
        self.assertIsNone(f["MOM12_1"][100])  # nema dovoljno istorije

    def test_volup_and_attn_use_volume(self):
        days = weekdays(n=120)
        vols = [1e6] * 120
        vols[100] = 5e6
        b = mk_bars(days, [0.0] * 119 + [0.0], vols)
        b2 = mk_bars(days, [0.0] * 100 + [0.04] + [0.0] * 19, vols)
        f = D.features(b2, CFG)
        self.assertAlmostEqual(f["VOLUP"][100], 0.04 * 5.0, places=6)
        self.assertGreater(f["ATTN"][100], 1.0)
        self.assertIsNone(D.features(b, CFG)["ATTN"][10])

    def test_event_flags_spike_and_cooldown(self):
        days = weekdays(n=120)
        vols = [1e6] * 120
        rets = [0.0] * 120
        for i in (60, 63, 80):
            rets[i], vols[i] = 0.08, 5e6
        ev = D.event_flags(mk_bars(days, rets, vols), CFG)
        self.assertIsNotNone(ev["SPIKE_UP"][60])
        self.assertIsNone(ev["SPIKE_UP"][63])  # unutar mirovanja od 10 svecâ
        self.assertIsNotNone(ev["SPIKE_UP"][80])
        self.assertTrue(all(x is None for x in ev["SPIKE_DN"]))
        rets[90], vols[90] = -0.08, 4e6
        self.assertIsNotNone(D.event_flags(mk_bars(days, rets, vols), CFG)["SPIKE_DN"][90])

    def test_high_breakout_needs_volume(self):
        days = weekdays(n=320)
        rets = [0.0005] * 320
        vols = [1e6] * 320
        vols[300] = 3e6
        ev = D.event_flags(mk_bars(days, rets, vols), CFG)
        self.assertIsNotNone(ev["HIGH_BRK"][300])
        self.assertIsNone(ev["HIGH_BRK"][299])


class CalendarTests(unittest.TestCase):
    def test_rebalance_is_last_bar_of_week_and_current_week_waits_for_friday(self):
        cal = ["2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13"]
        out = D.rebalance_dates(cal, 1, 5)
        self.assertEqual(out, ["2026-10-09"])  # tekuca nedelja (do utorka) jos nije gotova
        out2 = D.rebalance_dates(cal + ["2026-10-14", "2026-10-15", "2026-10-16"], 1, 5)
        self.assertEqual(out2, ["2026-10-09", "2026-10-16"])

    def test_every_second_week_uses_week_index_modulus(self):
        cal = weekdays("2026-01-05", 120)
        one = D.rebalance_dates(cal, 1, 5)
        two = D.rebalance_dates(cal, 2, 5)
        self.assertTrue(set(two) <= set(one))
        self.assertAlmostEqual(len(two) / len(one), 0.5, delta=0.1)

    def test_outcome_enters_next_open_and_exits_after_h_bars(self):
        px, bench = mk_universe(n_sym=2, days=60)
        U = uni(px, bench)
        s = "S00"
        d = px[s]["d"][10]
        r = U.outcome(s, d, 5)
        self.assertAlmostEqual(r, (px[s]["c"][15] / px[s]["o"][11] - 1) * 100, places=9)
        self.assertIsNone(U.outcome(s, px[s]["d"][-2], 5))  # ishod jos nije potpun

    def test_trim_incomplete_drops_today_bar(self):
        now = dt.datetime(2026, 10, 12, 12, 0, tzinfo=dt.timezone.utc)
        b = mk_bars(["2026-10-09", "2026-10-12"], [0.0, 0.01])
        self.assertEqual(D.trim_incomplete(b, now, 5)["d"], ["2026-10-09"])
        late = dt.datetime(2026, 10, 12, 22, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(D.trim_incomplete(b, late, 5)["d"], ["2026-10-09", "2026-10-12"])
        self.assertEqual(D.trim_incomplete(b, late, 7)["d"], ["2026-10-09"])  # kripto: danasnji dan nikad nije gotov


class StudyTests(unittest.TestCase):
    def test_persistent_winners_give_positive_long_leg_and_cost_is_subtracted(self):
        drift = [0.0015 - 0.0002 * k for k in range(16)]
        px, bench = mk_universe(seed=3, drift=drift)
        U = uni(px, bench)
        per = D.run_periods(U, CFG, "MOM12_1", 1)
        st_ = D.test_stats(per, 1, CFG, U.cal[-1])
        self.assertGreater(st_["mean"], 0.3)
        self.assertGreater(st_["t"], 3.0)
        flat_px, flat_b = mk_universe(seed=4, drift=[0.0] * 16, noise=0.0)
        Uf = uni(flat_px, flat_b)
        perf = D.run_periods(Uf, CFG, "HIGH52", 1)
        self.assertTrue(perf)
        self.assertTrue(all(abs(p[1] + CFG["cost_pct"]) < 1e-9 for p in perf))  # nema prednosti: ostaje samo trosak

    def test_pure_noise_rarely_passes_gates(self):
        """FDR 10% znaci da u cistom sumu otprilike 1 od 10 studija moze da dobije lazni kandidat (pre ostalih kapija): ovde najvise 1 od 4."""
        studies_with_candidate = 0
        for seed in range(4):
            px, bench = mk_universe(seed=seed + 10, days=700)
            U = uni(px, bench)
            tests = D.run_study({"stocks": U}, CFG, U.cal[-1])
            studies_with_candidate += 1 if any(r["status"] == "kandidat" for r in tests) else 0
            self.assertEqual(len(tests), (len(D.FAMILIES) * len(CFG["weeks"]) + len(D.EVENTS) * len(CFG["event_horizons"])) * 2)
        self.assertLessEqual(studies_with_candidate, 1)

    def test_event_study_detects_continuation_after_spikes(self):
        spikes = []
        for k in range(16):
            for i in range(300, 880, 55):
                spikes.append((k, i + 3 * k, 0.09, 5.0))
        px, bench = mk_universe(seed=5, spikes=spikes, noise=0.004, post=0.004)
        U = uni(px, bench)
        self.assertTrue(any(U.ev[s]["SPIKE_UP"][i] for s in U.px for i in range(len(U.cal))))
        per = D.event_periods(U, CFG, "SPIKE_UP", 5)
        self.assertGreater(len(per), 10)
        stats_long = D.test_stats(per, 1, CFG, U.cal[-1])
        stats_short = D.test_stats(per, 3, CFG, U.cal[-1])
        self.assertGreater(stats_long["mean"], 0.5)  # nastavak posle skoka
        self.assertLess(stats_short["mean"], 0.0)
        self.assertIsNotNone(stats_long["mean_ex_best"])

    def test_classify_gates(self):
        base = {"n": 80, "t": 3.5, "p": 0.001, "mean": 1.2, "abs_mean": 1.0, "t_train": 2.0, "t_test": 2.0, "recent_mean": 0.5, "mean_ex_best": 0.8}
        self.assertEqual(D.classify(base, True, CFG), "kandidat")
        self.assertEqual(D.classify(dict(base, recent_mean=-0.1), True, CFG), "nagovestaj")  # zadnjih 270 d lose
        self.assertEqual(D.classify(dict(base, mean_ex_best=-0.2), True, CFG), "nagovestaj")  # drzi jedan izuzetak
        self.assertEqual(D.classify(base, False, CFG), "nagovestaj")  # bez FDR-a, ali p < 0.05
        self.assertEqual(D.classify(dict(base, p=0.2, t=1.0), False, CFG), "odbaceno")
        self.assertEqual(D.classify(dict(base, n=20), True, CFG), "premalo")
        self.assertEqual(D.classify(dict(base, mean=-1.0), True, CFG), "odbaceno")  # negativan prosek nikad nije nagovestaj

    def test_thin_weeks_averages_within_week_and_skips_overlapping_weeks(self):
        rows = [("2026-01-05", 1.0, 2.0, None), ("2026-01-06", 3.0, 4.0, None), ("2026-01-12", 9.0, 9.0, None), ("2026-01-19", 5.0, 6.0, 1.0),
                ("2026-01-26", 7.0, 8.0, 2.0)]
        out = D.thin_weeks(rows, 10, 5)  # korak 2 nedelje
        self.assertTrue(out and all(D.week_index(r[0]) % 2 == 0 for r in out))
        kept = {D.week_index(r[0]) for r in out}
        self.assertEqual(kept, {w for w in {D.week_index(r[0]) for r in rows} if w % 2 == 0})
        first = [r for r in out if D.week_index(r[0]) == D.week_index("2026-01-05")]
        if first:  # nedelja sa dva reda: prosek, None se preskace
            self.assertAlmostEqual(first[0][1], 2.0)
            self.assertIsNone(first[0][3])

    def test_profile_reports_percentile_and_recent_events(self):
        spikes = [(0, 500, 0.1, 6.0)]
        px, bench = mk_universe(seed=6, spikes=spikes)
        U = uni(px, bench)
        day = U.cal[505]
        p = D.profile(U, "S00", day)
        self.assertEqual(p["date"], day)
        self.assertTrue(any(e["event"] == "SPIKE_UP" for e in p["events"]))
        self.assertTrue(0.0 <= p["families"]["ATTN"]["pct"] <= 1.0)
        self.assertIsNone(D.profile(U, "NEMA", day))


class SimTests(unittest.TestCase):
    def bars(self, rows):
        # rows: (o, h, l, c)
        return {"d": ["d%d" % i for i in range(len(rows))], "o": [r[0] for r in rows], "h": [r[1] for r in rows], "l": [r[2] for r in rows],
                "c": [r[3] for r in rows], "v": [1.0] * len(rows), "rc": [r[3] for r in rows]}

    def test_long_stop_target_and_time_exit(self):
        b = self.bars([(100, 101, 99, 100), (100, 101, 99, 100), (100, 103, 94, 96), (96, 97, 95, 96)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 3, "long", 5, 15), -5.0, places=6)  # stop 95
        b = self.bars([(100, 101, 99, 100), (100, 101, 99, 100), (101, 120, 100, 119), (119, 120, 118, 119)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 3, "long", 5, 15), 15.0, places=6)  # cilj 115
        b = self.bars([(100, 101, 99, 100), (100, 101, 99, 100), (100, 101, 99, 101), (101, 102, 100, 102)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 3, "long", 5, 15), 2.0, places=6)  # vremenski izlaz po zatvaranju

    def test_stop_wins_when_both_hit_same_bar_and_gap_exits_at_open(self):
        b = self.bars([(100, 101, 99, 100), (100, 120, 90, 100), (100, 101, 99, 100)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 2, "long", 5, 15), -5.0, places=6)
        b = self.bars([(100, 101, 99, 100), (100, 101, 99, 100), (90, 91, 88, 90)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 2, "long", 5, 15), -10.0, places=6)  # otvaranje ispod stopa

    def test_short_mirrors(self):
        b = self.bars([(100, 101, 99, 100), (100, 101, 99, 100), (100, 106, 99, 105)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 2, "short", 5, 15), -5.0, places=6)
        b = self.bars([(100, 101, 99, 100), (100, 101, 99, 100), (99, 100, 80, 82)])
        self.assertAlmostEqual(D.sim_trade(b, 1, 2, "short", 5, 15), 15.0, places=6)
        self.assertIsNone(D.sim_trade(b, 1, 5, "short", 5, 15))


class ForwardTests(unittest.TestCase):
    def setUp(self):
        drift = [0.002 - 0.00025 * k for k in range(16)]
        self.px, self.bench = mk_universe(seed=7, drift=drift, days=700)
        self.U = uni(self.px, self.bench)
        self.rule = {"universe": "stocks", "family": "MOM12_1", "kind": "rank", "step": 1, "H": 5, "leg": "long"}

    def rules(self, status="kandidat", start=None):
        r = dict(self.rule, status=status, first_seen_utc="x", forward_start=start or self.U.cal[-60], study={}, history=[])
        return {"stocks:MOM12_1:1w:long": r}

    def test_log_is_idempotent_frozen_and_only_for_tracked(self):
        rules = self.rules()
        new = D.log_signals(rules, {"stocks": self.U}, CFG, [], "2026-10-10T00:00:00Z")
        self.assertGreater(len(new), 5)
        self.assertEqual(len(new[0]["picks"]), CFG["pick_k"])
        again = D.log_signals(rules, {"stocks": self.U}, CFG, new, "2026-10-11T00:00:00Z")
        self.assertEqual(again, [])
        rules["stocks:MOM12_1:1w:long"]["status"] = "odbaceno"
        self.assertEqual(D.log_signals(rules, {"stocks": self.U}, CFG, [], "x"), [])

    def test_evaluate_log_realizes_outcomes_and_marks_pending(self):
        rules = self.rules()
        log = D.log_signals(rules, {"stocks": self.U}, CFG, [], "t")
        fs = D.evaluate_log(log, {"stocks": self.U}, CFG)["stocks:MOM12_1:1w:long"]
        self.assertGreater(fs["n"], 5)
        self.assertGreater(fs["mean"], 0.0)  # trajni pobednici
        self.assertIsNotNone(fs["sim_mean"])
        self.assertIsNotNone(fs["mean_ex_best"])
        short = D.make_rule(dict(self.rule, leg="short"))
        sr = {"stocks:MOM12_1:1w:short": dict(short, status="nagovestaj", first_seen_utc="x", forward_start=self.U.cal[-60], study={}, history=[])}
        slog = D.log_signals(sr, {"stocks": self.U}, CFG, [], "t")
        sfs = D.evaluate_log(slog, {"stocks": self.U}, CFG)["stocks:MOM12_1:1w:short"]
        self.assertGreater(sfs["mean"], 0.0)  # kratka noga = poslednji u rangu = trajni gubitnici: kratka pozicija zaradjuje

    def test_promotion_requires_all_forward_gates_and_demotion(self):
        good = {"n": 10, "mean": 0.8, "t": 1.4, "stress_mean": 0.5, "mean_ex_best": 0.3, "sim_mean": 0.4}
        self.assertTrue(D.forward_gate(good, CFG))
        for k, v in (("n", 7), ("mean", -0.1), ("t", 0.5), ("stress_mean", -0.9), ("mean_ex_best", -0.1), ("sim_mean", -0.2), ("sim_mean", None)):
            self.assertFalse(D.forward_gate(dict(good, **{k: v}), CFG), k)
        rules = self.rules()
        D.apply_forward(rules, {"stocks:MOM12_1:1w:long": good}, CFG, "2026-11-01T00:00:00Z")
        self.assertEqual(rules["stocks:MOM12_1:1w:long"]["status"], "potvrdjen")
        bad = dict(good, t=-2.0, mean=-1.0)
        D.apply_forward(rules, {"stocks:MOM12_1:1w:long": bad}, CFG, "2026-12-01T00:00:00Z")
        self.assertEqual(rules["stocks:MOM12_1:1w:long"]["status"], "nagovestaj")

    def test_only_candidate_can_be_promoted(self):
        rules = self.rules(status="nagovestaj")
        D.apply_forward(rules, {"stocks:MOM12_1:1w:long": {"n": 20, "mean": 1.0, "t": 3.0, "stress_mean": 0.7, "mean_ex_best": 0.9, "sim_mean": 0.9}}, CFG, "t")
        self.assertEqual(rules["stocks:MOM12_1:1w:long"]["status"], "nagovestaj")

    def test_apply_study_creates_tracks_and_demotes(self):
        t = dict(self.rule, id="stocks:MOM12_1:1w:long", status="nagovestaj", n=50, mean=1.0, t=2.5, p=0.01, fdr=False)
        rules = D.apply_study({}, [t], "2026-10-10T01:00:00Z", {"stocks": self.U})
        r = rules[t["id"]]
        self.assertEqual(r["status"], "nagovestaj")
        self.assertTrue(r["forward_start"] >= self.U.cal[-10])  # prvi signal sa nepotpunim ishodom
        rules = D.apply_study(rules, [dict(t, status="kandidat")], "2026-10-17T01:00:00Z", {"stocks": self.U})
        self.assertEqual(rules[t["id"]]["status"], "kandidat")
        rules[t["id"]]["status"] = "potvrdjen"
        rules = D.apply_study(rules, [dict(t, status="kandidat")], "2026-10-24T01:00:00Z", {"stocks": self.U})
        self.assertEqual(rules[t["id"]]["status"], "potvrdjen")  # studija ne skida potvrdjen dok i dalje prolazi
        rules = D.apply_study(rules, [dict(t, status="odbaceno")], "2026-10-31T01:00:00Z", {"stocks": self.U})
        self.assertEqual(rules[t["id"]]["status"], "odbaceno")
        self.assertEqual([h[1] for h in rules[t["id"]]["history"]][-1], "odbaceno")
        ignored = D.apply_study({}, [dict(t, id="stocks:X:1w:long", status="odbaceno")], "t", {"stocks": self.U})
        self.assertEqual(ignored, {})

    def test_radar_has_stop_target_window_and_hold(self):
        rules = self.rules(status="potvrdjen")
        radar = D.build_radar(rules, {"stocks": self.U}, CFG, "2026-10-10T00:40:00Z")
        self.assertEqual(len(radar["rules"]), 1)
        r = radar["rules"][0]
        self.assertEqual(r["hold_hours"], 168)
        self.assertEqual(len(r["picks"]), CFG["radar"]["pick_k"])
        p = r["picks"][0]
        self.assertTrue(p["symbol"].startswith("xyz:"))
        self.assertTrue(3.0 <= p["stop_pct"] <= 12.0)
        self.assertAlmostEqual(p["tp_pct"], 3.0 * p["stop_pct"], places=1)
        self.assertLess(r["valid_from_utc"], r["valid_until_utc"])

    def test_entry_window_skips_weekend(self):
        frm, to = D.entry_window(self.U, "2026-10-09", CFG)  # petak
        self.assertTrue(frm.startswith("2026-10-12T"))
        self.assertEqual(to[:10], "2026-10-13")

    def test_event_radar_only_for_signal_on_last_bar(self):
        spikes = [(0, 699, 0.1, 6.0)]
        px, bench = mk_universe(seed=8, days=700, spikes=spikes)
        U = uni(px, bench)
        rule = {"universe": "stocks", "family": "SPIKE_UP", "kind": "event", "step": 5, "H": 5, "leg": "long", "status": "nagovestaj",
                "first_seen_utc": "x", "forward_start": U.cal[-5], "study": {}, "history": []}
        radar = D.build_radar({"stocks:SPIKE_UP:5d:long": rule}, {"stocks": U}, CFG, "t")
        self.assertEqual(len(radar["rules"]), 1)
        self.assertEqual(radar["rules"][0]["picks"][0]["ticker"], "S00")
        px2, bench2 = mk_universe(seed=8, days=700, spikes=[(0, 680, 0.1, 6.0)])
        radar2 = D.build_radar({"stocks:SPIKE_UP:5d:long": rule}, {"stocks": uni(px2, bench2)}, CFG, "t")
        self.assertEqual(radar2["rules"], [])  # stari dogadjaj nije svez


class RunTests(unittest.TestCase):
    @staticmethod
    def text_of(root, rel):
        with open(os.path.join(root, *rel.split("/")), encoding="utf-8") as f:
            return f.read()

    def rules_of(self, root):
        return json.loads(self.text_of(root, "discovery/rules.json"))["rules"]

    def test_end_to_end_weekly_then_daily_is_idempotent(self):
        drift = [0.002 - 0.00025 * k for k in range(16)]
        now = dt.datetime(2026, 10, 12, 0, 40, tzinfo=dt.timezone.utc)
        cal = [d for d in weekdays("2023-01-02", 1500) if d <= "2026-10-09"][-800:]
        px, bench = mk_universe(seed=9, drift=drift, cal=cal)
        data = dict(px)
        data["SPY"] = bench
        cands = {"stocks": [{"sym": "xyz:" + s, "yahoo": s, "mark": b["rc"][-1], "vol24": 1e7} for s, b in px.items()]}
        orig = D.load_prices
        D.load_prices = lambda syms, cache=None, max_age_h=12: {s: data[s] for s in syms if s in data}
        try:
            with tempfile.TemporaryDirectory() as root:
                os.makedirs(os.path.join(root, "config"))
                with open(os.path.join(root, "config", "discovery.json"), "w", encoding="utf-8") as f:
                    json.dump(CFG, f)
                self.assertEqual(D.run("weekly", write=True, root=root, now=now, hl=cands, log=lambda m: None), 0)
                for fn in ("discovery/rules.json", "discovery/radar.json", "discovery/universe.json", "calibration/discovery.json", "calibration/discovery.md"):
                    self.assertTrue(os.path.exists(os.path.join(root, fn)), fn)
                rules1 = self.rules_of(root)
                self.assertTrue(rules1)  # trajni pobednici daju bar nagovestaj
                self.assertEqual(D.run("daily", write=True, root=root, now=now, hl=cands, log=lambda m: None), 0)
                rules2 = self.rules_of(root)
                self.assertEqual({k: v["status"] for k, v in rules1.items()}, {k: v["status"] for k, v in rules2.items()})
                lines1 = self.text_of(root, "discovery/forward.jsonl")
                D.run("daily", write=True, root=root, now=now, hl=cands, log=lambda m: None)
                self.assertEqual(lines1, self.text_of(root, "discovery/forward.jsonl"))
        finally:
            D.load_prices = orig

    def test_no_universe_leaves_files_untouched(self):
        orig = D.load_prices
        D.load_prices = lambda syms, cache=None, max_age_h=12: {}
        try:
            with tempfile.TemporaryDirectory() as root:
                os.makedirs(os.path.join(root, "config"))
                with open(os.path.join(root, "config", "discovery.json"), "w", encoding="utf-8") as f:
                    json.dump(CFG, f)
                self.assertEqual(D.run("weekly", write=True, root=root, hl={"stocks": []}, log=lambda m: None), 1)
                self.assertFalse(os.path.exists(os.path.join(root, "discovery", "rules.json")))
        finally:
            D.load_prices = orig


if __name__ == "__main__":
    unittest.main()
