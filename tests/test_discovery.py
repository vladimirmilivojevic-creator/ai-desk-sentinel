import datetime as dt
import json
import os
import random
import tempfile
import unittest

from lab import discovery as D

CFG = D.load_cfg()
UCFG = CFG["universes"]["stocks"]
TCFG = dict(CFG, universes={"stocks": UCFG})  # samo akcije: testovi ne smeju da zovu mrezu za kripto i robe


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
                    json.dump(TCFG, f)
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
                    json.dump(TCFG, f)
                self.assertEqual(D.run("weekly", write=True, root=root, hl={"stocks": []}, log=lambda m: None), 1)
                self.assertFalse(os.path.exists(os.path.join(root, "discovery", "rules.json")))
        finally:
            D.load_prices = orig


def alldays(end="2026-10-11", n=800):
    d1 = dt.date.fromisoformat(end)
    return [(d1 - dt.timedelta(days=n - 1 - k)).isoformat() for k in range(n)]


UC = CFG["universes"]["crypto"]
UM = CFG["universes"]["commodities"]


class UniverseV4Tests(unittest.TestCase):
    def test_membership_limits_members_and_universe_mean(self):
        px, bench = mk_universe(seed=3, n_sym=16, days=400)
        d = bench["d"][350]
        syms = sorted(px)
        mem = {s: ({d} if k < 13 else set()) for k, s in enumerate(syms)}
        U = D.Universe("crypto", px, bench, UC, CFG, mem=mem)
        self.assertEqual(len(U.members("MOM12_1", d)), 13)
        self.assertEqual(len(U.active(d)), 13)
        self.assertIsNotNone(U.universe_mean(d, 5))
        mem2 = {s: ({d} if k < 8 else set()) for k, s in enumerate(syms)}
        self.assertIsNone(D.Universe("crypto", px, bench, UC, CFG, mem=mem2).universe_mean(d, 5))  # ispod min_universe

    def test_picks_only_tradable_and_explorer_symbol(self):
        px, bench = mk_universe(seed=4, n_sym=16, days=400, drift=[0.001 * (k - 8) for k in range(16)])
        d = bench["d"][350]
        r = {"universe": "crypto", "family": "MOM12_1", "kind": "rank", "step": 1, "H": 7, "leg": "long"}
        U_all = D.Universe("crypto", px, bench, UC, CFG)
        top = [x[0] for x in U_all.members("MOM12_1", d)][:3]
        low = U_all.members("MOM12_1", d)[-1][0]
        U = D.Universe("crypto", px, bench, UC, CFG, tradable={top[1], low}, ex={top[1]: "k" + top[1]})
        got = [p["sym"] for p in D.pick_for(U, r, d, 3, CFG)]
        self.assertEqual(got, [top[1], low])  # samo tradable, po redu ocene
        self.assertNotIn(top[0], got)
        self.assertEqual(U.explorer(top[1]), "k" + top[1])
        self.assertEqual(D.Universe("stocks", px, bench, UCFG, CFG).explorer("S03"), "xyz:S03")

    def test_event_thresholds_and_cost_per_universe(self):
        days = weekdays(n=120)
        rets, vols = [0.0] * 120, [1e6] * 120
        rets[60], vols[60] = 0.08, 5e6
        rets[90], vols[90] = 0.04, 5e6
        b = mk_bars(days, rets, vols)
        bench = mk_bars(days, [0.0] * 120)
        us = D.Universe("stocks", {"X": b}, bench, UCFG, CFG)
        uc = D.Universe("crypto", {"X": b}, bench, UC, CFG)
        um = D.Universe("commodities", {"X": b}, bench, UM, CFG)
        self.assertIsNotNone(us.ev["X"]["SPIKE_UP"][60])
        self.assertIsNone(uc.ev["X"]["SPIKE_UP"][60])  # 8% nije dovoljno za kripto (prag 10%)
        self.assertIsNotNone(um.ev["X"]["SPIKE_UP"][60])
        self.assertIsNotNone(um.ev["X"]["SPIKE_UP"][90])  # 4% je preko praga robe (3.5%)
        self.assertIsNone(us.ev["X"]["SPIKE_UP"][90])
        self.assertAlmostEqual(us.cost, CFG["cost_pct"])
        self.assertAlmostEqual(uc.cost, CFG["cost_pct"] + 0.10)
        self.assertAlmostEqual(um.cost, CFG["cost_pct"] + 0.15)

    def test_entry_windows(self):
        px, bench = mk_universe(seed=5, n_sym=3, days=50)
        uc = D.Universe("crypto", px, bench, UC, CFG)
        frm, to = D.entry_window(uc, "2026-10-11", CFG)  # nedelja
        self.assertEqual((frm, to), ("2026-10-12T00:00:00Z", "2026-10-13T06:00:00Z"))
        um = D.Universe("commodities", px, bench, UM, CFG)
        frm, to = D.entry_window(um, "2026-10-09", CFG)  # petak: robe ulaze u ponedeljak 00:00
        self.assertEqual(frm, "2026-10-12T00:00:00Z")
        us = D.Universe("stocks", px, bench, UCFG, CFG)
        self.assertEqual(D.entry_window(us, "2026-10-09", CFG)[0], "2026-10-12T14:30:00Z")


class DataQualityTests(unittest.TestCase):
    def test_clean_series_cuts_at_last_break(self):
        days = alldays(n=120)
        b = mk_bars(days, [0.0] * 120)
        for k in ("o", "h", "l", "c", "rc"):
            for i in range(50, 120):
                b[k][i] *= 100.0  # promena denominacije u svecu 50
        out = D.clean_series(b)
        self.assertEqual(len(out["c"]), 70)
        self.assertEqual(out["d"][0], days[50])
        days2 = days[:60] + days[66:]  # rupa od 6 dana
        b2 = mk_bars(days2, [0.0] * len(days2))
        self.assertEqual(len(D.clean_series(b2)["c"]), len(days2) - 60)
        self.assertEqual(len(D.clean_series(mk_bars(days, [0.01] * 120))["c"]), 120)  # cist niz se ne dira

    def test_pit_membership_is_point_in_time_and_keeps_dead_symbols(self):
        days = alldays(n=12)
        def bars(vol, n):
            b = mk_bars(days[:n], [0.0] * n)
            b["v"] = [float(vol)] * n
            return b
        px = {"A": bars(300, 12), "B": bars(200, 12), "C": bars(100, 12), "DEAD": bars(400, 6)}
        mem = D.pit_membership(px, 2, 3)
        self.assertIn(days[4], mem["DEAD"])
        self.assertNotIn(days[8], mem["DEAD"])  # posle gasenja nije clan
        self.assertIn(days[8], mem["A"])
        self.assertIn(days[8], mem["B"])
        self.assertNotIn("C", mem)
        self.assertEqual(sorted(s for s in mem if days[4] in mem[s]), ["A", "DEAD"])
        # nema gledanja unapred: promena kasnijih podataka ne menja clanstvo ranijih dana
        px2 = {k: dict(v, v=list(v["v"])) for k, v in px.items()}
        for i in range(8, 12):
            px2["C"]["v"][i] = 9000.0
        mem2 = D.pit_membership(px2, 2, 3)
        for day in days[:8]:
            self.assertEqual({s for s in mem if day in mem[s]}, {s for s in mem2 if day in mem2[s]})

    def test_fetch_binance_pages_and_failure_modes(self):
        t0 = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        def row(i, c=10.0):
            return [t0 + i * 86400000, "10", "11", "9", str(c), "5", 0, str(c * 1000)]
        pages = [[row(i) for i in range(1000)], [row(i) for i in range(1000, 1003)] + [row(1002)]]
        calls = []
        def fake(path, tries=3):
            calls.append(path)
            return pages[len(calls) - 1]
        orig = D.binance_get
        try:
            D.binance_get = fake
            b = D.fetch_binance("XUSDT", t0)
            self.assertEqual(len(b["c"]), 1003)  # duplikat poslednje svece je odbacen
            self.assertAlmostEqual(b["v"][0], 10000.0)  # obim je promet u USDT
            self.assertEqual(b["d"][0], "2023-01-01")
            self.assertEqual(len(calls), 2)
            D.binance_get = lambda path, tries=3: False
            self.assertEqual(D.fetch_binance("NOPE", t0)["c"], [])
            D.binance_get = lambda path, tries=3: None
            self.assertIsNone(D.fetch_binance("XUSDT", t0))
        finally:
            D.binance_get = orig

    def test_binance_superset_keeps_every_symbol_that_was_ever_near_the_top(self):
        weeks = [(dt.date(2023, 1, 2) + dt.timedelta(days=7 * i)).isoformat() for i in range(8)]
        vol = {"A": [100] * 8, "B": [50] * 8, "C": [10] * 8, "D": [5] * 8, "LATE": [0, 0, 0, 0, 0, 0, 500, 500]}
        orig = D.fetch_binance_weekly
        try:
            D.fetch_binance_weekly = lambda sym, start_ms: dict(zip(weeks, map(float, vol[sym])))
            keep, fails = D.binance_superset(sorted(vol), 0, 1, 2)  # 1 x 2 = dva mesta po nedelji
            self.assertEqual((keep, fails), ({"A", "B", "LATE"}, 0))
            D.fetch_binance_weekly = lambda sym, start_ms: None
            self.assertEqual(D.binance_superset(["A", "B"], 0, 1, 2), (set(), 2))
        finally:
            D.fetch_binance_weekly = orig

    def test_binance_symbols_lists_dead_and_falls_back(self):
        xml1 = ("<ListBucketResult><IsTruncated>true</IsTruncated><NextMarker>data/spot/monthly/klines/BTCUSDT/</NextMarker><Prefix>data/spot/monthly/klines/</Prefix>"
                "<CommonPrefixes><Prefix>data/spot/monthly/klines/BTCUSDT/</Prefix></CommonPrefixes><CommonPrefixes><Prefix>data/spot/monthly/klines/ETHBTC/</Prefix></CommonPrefixes></ListBucketResult>")
        xml2 = ("<ListBucketResult><IsTruncated>false</IsTruncated><CommonPrefixes><Prefix>data/spot/monthly/klines/LUNAUSDT/</Prefix></CommonPrefixes></ListBucketResult>")
        seen = []
        class R:
            def __init__(self, x):
                self.x = x
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def read(self):
                return self.x.encode()
        def fake_open(req, timeout=0):
            seen.append(req.full_url)
            return R(xml1 if "marker=" not in req.full_url else xml2)
        o_open, o_get = D.urllib.request.urlopen, D.binance_get
        try:
            D.urllib.request.urlopen = fake_open
            D.binance_get = lambda path, tries=3: {"symbols": [{"symbol": "NEWUSDT", "quoteAsset": "USDT", "status": "TRADING"},
                                                              {"symbol": "OLDUSDT", "quoteAsset": "USDT", "status": "BREAK"}]}
            syms = D.binance_symbols(log=lambda m: None)
        finally:
            D.urllib.request.urlopen, D.binance_get = o_open, o_get
        self.assertEqual(syms, ["BTCUSDT", "LUNAUSDT", "NEWUSDT"])
        self.assertEqual(len(seen), 2)


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class ThreeUniverseRunTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 10, 12, 0, 40, tzinfo=dt.timezone.utc)
        cal5 = [d for d in weekdays("2023-01-02", 1500) if d <= "2026-10-09"][-800:]
        cal7 = alldays("2026-10-11", 800)
        self.px_s, self.bench_s = mk_universe(seed=9, drift=[0.002 - 0.00025 * k for k in range(16)], cal=cal5)
        px_c, bench_c = mk_universe(seed=11, n_sym=17, noise=0.03, cal=cal7)
        self.px_c = {"%sUSDT" % k: v for k, v in px_c.items()}
        rb = random.Random(77)
        self.px_c["S00BUSDT"] = px_c["S01"]  # akcijski token (S00 je akcija): ne sme u kripto
        self.px_c["BTCUSDT"] = mk_bars(cal7, [rb.gauss(0, 0.03) for _ in cal7], vols=[1e6] * len(cal7))
        px_m, bench_m = mk_universe(seed=13, n_sym=14, cal=cal5)
        self.px_m = {"M%02d=F" % int(k[1:]): v for k, v in px_m.items()}
        self.px_m["G0=F"] = bench_m
        ucr = dict(UC, top_n=14, min_hl_vol24_usd=0)
        umm = dict(UM, symbols=dict({s: ("xyz:M%s" % s[1:3]) if k < 6 else None for k, s in enumerate(sorted(self.px_m))}), benchmark="G0=F")
        self.cfg = dict(CFG, universes={"stocks": UCFG, "crypto": ucr, "commodities": umm})
        self.cands = {
            "stocks": [{"sym": "xyz:" + s, "yahoo": s, "mark": b["rc"][-1], "vol24": 1e7} for s, b in self.px_s.items()],
            "crypto": [{"sym": s[:-4], "base": s[:-4], "scale": 1.0, "mark": b["rc"][-1], "vol24": 1e7} for s, b in self.px_c.items() if s != "BTCUSDT"] +
                      [{"sym": "BTC", "base": "BTC", "scale": 1.0, "mark": self.px_c["BTCUSDT"]["rc"][-1], "vol24": 1e7}],
            "commodities": [{"sym": umm["symbols"][s], "yahoo": s, "mark": self.px_m[s]["rc"][-1], "vol24": 1e7} for s in sorted(self.px_m)]}
        self.orig = (D.load_prices, D.binance_symbols, D.fetch_binance, D.binance_superset)
        data = dict(self.px_s, SPY=self.bench_s, **self.px_m)
        D.load_prices = lambda syms, cache=None, max_age_h=12: {s: data[s] for s in syms if s in data}
        D.binance_symbols = lambda log=print: sorted(self.px_c)
        D.binance_superset = lambda syms, start_ms, top_n, factor, cache=None, max_age_h=12: (set(syms), 0)
        D.fetch_binance = lambda sym, start_ms: self.px_c.get(sym, {"d": [], "o": [], "h": [], "l": [], "c": [], "v": [], "rc": []})

    def tearDown(self):
        D.load_prices, D.binance_symbols, D.fetch_binance, D.binance_superset = self.orig

    def test_weekly_runs_all_three_universes_then_daily(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "config"))
            with open(os.path.join(root, "config", "discovery.json"), "w", encoding="utf-8") as f:
                json.dump(self.cfg, f)
            self.assertEqual(D.run("weekly", write=True, root=root, now=self.now, hl=self.cands, log=lambda m: None), 0)
            res = json.loads(read_text(os.path.join(root, "calibration", "discovery.json")))
            self.assertEqual(set(res["universes"]), {"stocks", "crypto", "commodities"})
            self.assertEqual(len(res["tests"]), 180)
            self.assertTrue(any(r["id"] == "crypto:SPIKE_UP:7d:long" for r in res["tests"]))
            self.assertTrue(any(r["id"] == "stocks:SPIKE_UP:5d:long" for r in res["tests"]))
            self.assertEqual({r["universe"] for r in res["tests"]}, {"stocks", "crypto", "commodities"})
            uni = json.loads(read_text(os.path.join(root, "discovery", "universe.json")))["universes"]
            self.assertTrue(any(x["tradable"] for x in uni["crypto"]))
            self.assertTrue(any(x["tradable"] for x in uni["commodities"]))
            self.assertTrue(any(not x["tradable"] for x in uni["commodities"]))
            md = read_text(os.path.join(root, "calibration", "discovery.md"))
            self.assertIn("roll", md)
            self.assertEqual(D.run("daily", write=True, root=root, now=self.now, hl=self.cands, log=lambda m: None), 0)

    def test_stock_tokens_are_not_crypto(self):
        unis, _ = D.prepare(self.cfg, self.now, None, log=lambda m: None, hl=self.cands)
        self.assertNotIn("S00BUSDT", unis["crypto"].px)
        self.assertIn("S01USDT", unis["crypto"].px)

    def test_weekly_refuses_when_a_universe_is_missing_but_daily_goes_on(self):
        D.binance_symbols = lambda log=print: []
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "config"))
            with open(os.path.join(root, "config", "discovery.json"), "w", encoding="utf-8") as f:
                json.dump(self.cfg, f)
            self.assertEqual(D.run("weekly", write=True, root=root, now=self.now, hl=self.cands, log=lambda m: None), 1)
            self.assertFalse(os.path.exists(os.path.join(root, "discovery", "rules.json")))
            self.assertEqual(D.run("daily", write=True, root=root, now=self.now, hl=self.cands, log=lambda m: None), 0)


if __name__ == "__main__":
    unittest.main()
