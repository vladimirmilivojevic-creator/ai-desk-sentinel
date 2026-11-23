import json
import os
import tempfile
import unittest

from lab import jumps as J


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

CFG = J.load_cfg()
MIN = J.MIN
T0 = 1700000000000  # proizvoljan pocetak


def ctx_of(**coins):
    """coins: ime=(oznaka, oi_usd, vol24)."""
    return {k: {"mark": v[0], "oi_usd": v[1] if len(v) > 1 else 50e6, "vol24": v[2] if len(v) > 2 else 5e6} for k, v in coins.items()}


def feed(series, start=T0, step=5):
    """series: {coin: [oznake po koraku od 5 min]}; vraca (snap, poslednji trenutak, poslednji ctx)."""
    snap, ctx, t = {}, {}, start
    n = max(len(v) for v in series.values())
    for i in range(n):
        t = start + i * step * MIN
        ctx = ctx_of(**{c: (v[i],) for c, v in series.items() if i < len(v)})
        J.update_snap(snap, ctx, t, CFG["snapshot_keep_min"])
    return snap, t, ctx


class JumpTests(unittest.TestCase):
    def test_burst_up_and_down_are_detected_and_calm_coin_is_not(self):
        base = [100.0] * 12  # 55 min mirnog kretanja
        snap, now, ctx = feed({"UP": base + [116.0], "DN": base + [80.0], "CALM": base + [105.0], "FLAT": base + [100.0]})
        ev = J.detect(snap, ctx, [], CFG, now)
        got = {e["coin"]: e for e in ev}
        self.assertEqual(set(got), {"UP", "DN"})
        self.assertEqual((got["UP"]["trigger"], got["UP"]["dir"]), ("burst", "up"))
        self.assertAlmostEqual(got["UP"]["ret_pct"], 16.0, places=1)
        self.assertEqual(got["DN"]["dir"], "down")
        self.assertEqual(set(got["UP"]["due"]), {"60", "240", "1440"})
        self.assertTrue(got["UP"]["due"]["60"] == now + 60 * MIN)

    def test_ramp_catches_slow_climb_that_no_single_hour_shows(self):
        px = [100.0 * (1.07 ** (i / 12.0)) for i in range(49)]  # +7% na sat, 4 sata = +31%
        snap, now, ctx = feed({"SLOW": px})
        ev = J.detect(snap, ctx, [], CFG, now)
        self.assertEqual([(e["trigger"], e["dir"]) for e in ev], [("ramp", "up")])
        self.assertGreater(ev[0]["ret_pct"], 25.0)

    def test_cooldown_gap_and_thin_flag(self):
        base = [100.0] * 12
        snap, now, ctx = feed({"A": base + [120.0]})
        first = J.detect(snap, ctx, [], CFG, now)
        self.assertEqual(len(first), 1)
        self.assertEqual(J.detect(snap, ctx, first, CFG, now), [])  # isti instrument u cooldown-u
        ctx_thin = ctx_of(A=(120.0, 1e6))
        snap2, now2, _ = feed({"A": base + [120.0]})
        self.assertTrue(J.detect(snap2, ctx_thin, [], CFG, now2)[0]["thin"])  # OI ispod praga = tanko trziste
        # rupa u podacima: nema tacke blizu now-60min, pa nema poredjenja
        snap3 = {"G": [[T0, 100.0, 0.0], [T0 + 100 * MIN, 130.0, 0.0]]}
        self.assertEqual(J.detect(snap3, ctx_of(G=(130.0,)), [], CFG, T0 + 100 * MIN), [])

    def test_snapshot_prunes_old_points_and_ignores_bad_marks(self):
        snap = {}
        for i in range(80):
            J.update_snap(snap, {"X": {"mark": 1.0, "vol24": 1}, "BAD": {"mark": "n/a"}, "ZERO": {"mark": 0}}, T0 + i * 5 * MIN, CFG["snapshot_keep_min"])
        self.assertEqual(set(snap), {"X"})
        self.assertLessEqual(len(snap["X"]), CFG["snapshot_keep_min"] // 5 + 1)
        J.update_snap(snap, {"X": {"mark": 2.0}}, T0 + 79 * 5 * MIN, CFG["snapshot_keep_min"])  # isti trenutak se ne duplira
        self.assertEqual(snap["X"][-1][1], 1.0)

    def test_outcomes_follow_direction_net_of_cost_late_is_missed_and_peak_tracked(self):
        up = {"coin": "U", "t_ms": T0, "dir": "up", "mark": 100.0, "thin": False, "due": {"60": T0 + 60 * MIN, "240": T0 + 240 * MIN, "1440": T0 + 1440 * MIN},
              "out": {"60": None, "240": None, "1440": None}, "peak_pct": 0.0, "trough_pct": 0.0}
        dn = dict(up, coin="D", dir="down", thin=True, out={"60": None, "240": None, "1440": None}, due=dict(up["due"]), peak_pct=0.0, trough_pct=0.0)
        evs = [up, dn]
        J.update_outcomes(evs, ctx_of(U=(104.0,), D=(90.0,)), CFG, T0 + 30 * MIN)
        self.assertEqual((up["peak_pct"], dn["peak_pct"]), (4.0, 10.0))  # u smeru dogadjaja
        J.update_outcomes(evs, ctx_of(U=(110.0,), D=(90.0,)), CFG, T0 + 60 * MIN)
        self.assertAlmostEqual(up["out"]["60"]["gross"], 10.0)
        self.assertAlmostEqual(up["out"]["60"]["net"], 10.0 - CFG["cost_pct"]["normal"])
        self.assertAlmostEqual(dn["out"]["60"]["net"], 10.0 - CFG["cost_pct"]["thin"])  # tanko trziste = veci trosak
        J.update_outcomes(evs, ctx_of(U=(95.0,), D=(95.0,)), CFG, T0 + 240 * MIN + 55 * MIN)  # 55 min posle roka: kasni (> 40)
        self.assertEqual(up["out"]["240"], {"missed": True})
        self.assertEqual(up["out"]["60"]["gross"], 10.0)  # zabelezeni ishod se ne menja
        self.assertEqual(up["peak_pct"], 10.0)  # vrh ostaje
        self.assertLessEqual(up["trough_pct"], 0.0)

    def test_summary_groups_and_fade_is_the_mirror_of_follow(self):
        def ev(coin, d, gross, thin=False, trig="burst"):
            c = CFG["cost_pct"]["thin" if thin else "normal"]
            return {"coin": coin, "dir": d, "trigger": trig, "thin": thin, "peak_pct": 5.0, "trough_pct": -2.0,
                    "out": {"60": {"gross": gross, "net": gross - c, "px": 1}, "240": None, "1440": {"missed": True}}}
        s = J.summarize([ev("A", "up", 4.0), ev("B", "up", -2.0), ev("C", "down", 1.0, thin=True)], CFG)
        self.assertEqual(s["all"]["events"], 3)
        self.assertEqual(s["burst/up"]["events"], 2)
        self.assertEqual(s["burst/up/likvidno"]["follow_net_60m"]["n"], 2)
        self.assertEqual(s["burst/down/tanko"]["events"], 1)
        self.assertEqual(s["all"]["follow_net_240m"], {"n": 0})
        a = s["burst/up"]
        self.assertAlmostEqual(a["follow_net_60m"]["mean"] + a["fade_net_60m"]["mean"], -2 * CFG["cost_pct"]["normal"], places=2)

    def test_run_end_to_end_writes_files_detects_once_and_never_raises_on_empty_state(self):
        with tempfile.TemporaryDirectory() as d:
            t = T0
            for i in range(13):
                px = 100.0 if i < 12 else 125.0
                res = J.run(d, cfg=CFG, ctx=ctx_of(W=(px, 15e6), CALM=(100.0, 80e6)), now_ms=t + i * 5 * MIN, log=lambda m: None)
            self.assertEqual(res["new"], 1)
            ev = read_json(os.path.join(d, "jumps", "events.json"))
            self.assertEqual([e["coin"] for e in ev], ["W"])
            self.assertEqual(ev[0]["oi_usd"], 15000000)
            sm = read_json(os.path.join(d, "jumps", "summary.json"))
            self.assertEqual(sm["events"], 1)
            self.assertEqual(sm["last"][0]["coin"], "W")
            res2 = J.run(d, cfg=CFG, ctx=ctx_of(W=(126.0, 15e6)), now_ms=t + 13 * 5 * MIN, log=lambda m: None)
            self.assertEqual(res2["new"], 0)  # cooldown
        with tempfile.TemporaryDirectory() as d2:
            self.assertEqual(J.run(d2, cfg=CFG, ctx={}, now_ms=T0, log=lambda m: None)["events"], 0)

    def test_fire_queue_only_for_liquid_burst_up_once_and_with_daily_cap(self):
        from lab import jump_fire as JF
        with tempfile.TemporaryDirectory() as d:
            t = T0
            for i in range(13):  # W skace +25% (OI 15M), DN pada -25%, THIN skace ali je OI ispod 1M
                up, dn = (100.0, 100.0) if i < 12 else (125.0, 75.0)
                res = J.run(d, cfg=CFG, ctx=ctx_of(W=(up, 15e6), DN=(dn, 15e6), THIN=(up, 5e5), CALM=(100.0, 80e6)), now_ms=t + i * 5 * MIN, log=lambda m: None)
            self.assertEqual(res["new"], 3)
            self.assertEqual(res["fire_queued"], 1)
            pend = read_json(os.path.join(d, "jumps", "pending_fire.json"))
            self.assertEqual(pend["payload"]["kind"], "jump")
            self.assertEqual(len(pend["payload"]["ids"]), 1)
            self.assertTrue(pend["payload"]["ids"][0].startswith("W@"))
            sent = []
            now = t + 12 * 5 * MIN + 2 * MIN
            r = JF.run(d, now_ms=now, fire=lambda p: (sent.append(p) or True, "okinuto"))
            self.assertTrue(r["fired"])
            self.assertEqual(sent, [{"kind": "jump", "ids": pend["payload"]["ids"]}])
            self.assertFalse(JF.run(d, now_ms=now + 20 * MIN, fire=lambda p: (True, "x"))["fired"])  # star red se ne salje
            res2 = J.run(d, cfg=CFG, ctx=ctx_of(W=(126.0, 15e6)), now_ms=t + 13 * 5 * MIN, log=lambda m: None)
            self.assertEqual(res2["fire_queued"], 0)
            self.assertFalse(os.path.exists(os.path.join(d, "jumps", "pending_fire.json")))  # sledeci krug brise red: nema dvostrukog okidanja
            self.assertEqual(read_json(os.path.join(d, "jumps", "fire_log.json"))["count"], 1)
        ev = {"id": "X@2026-11-16T10:00:00Z", "coin": "X", "dir": "up", "trigger": "burst", "oi_usd": 5e6}
        with tempfile.TemporaryDirectory() as d3:
            cap = dict(CFG, fire=dict(CFG["fire"], max_per_day=1))
            self.assertEqual(J.queue_fire(d3, [ev], cap, T0, log=lambda m: None), 1)
            self.assertEqual(J.queue_fire(d3, [dict(ev, id="Y@2026-11-16T11:00:00Z")], cap, T0 + 60 * MIN, log=lambda m: None), 0)  # dnevni plafon
            self.assertEqual(J.queue_fire(d3, [ev], dict(CFG, fire={"enabled": False}), T0 + 86400000 * 2, log=lambda m: None), 0)
            self.assertEqual(J.fire_candidates([dict(ev, trigger="ramp"), dict(ev, dir="down")], CFG), [])
            self.assertEqual(J.fire_candidates([dict(ev, coin="xyz:NVDA")], CFG), [])  # akcije ne bude rutinu
            self.assertEqual(len(J.fire_candidates([dict(ev, coin="HYPE")], CFG)), 1)
            self.assertEqual(JF.run(d3, now_ms=T0)["why"], "nema reda")

    def test_summary_splits_stocks_and_crypto(self):
        ev = [{"coin": "xyz:NVDA", "trigger": "burst", "dir": "up", "thin": False, "peak_pct": 1.0, "trough_pct": -1.0, "out": {"60": {"gross": 1.0}, "240": None, "1440": None}},
              {"coin": "HYPE", "trigger": "burst", "dir": "up", "thin": False, "peak_pct": 1.0, "trough_pct": -1.0, "out": {"60": {"gross": -2.0}, "240": None, "1440": None}}]
        s = J.summarize(ev, CFG)
        self.assertEqual(s["burst/up/akcije"]["events"], 1)
        self.assertEqual(s["burst/up/kripto"]["events"], 1)

    def test_fire_without_secrets_does_nothing(self):
        from sentinel import notify
        old = {k: os.environ.pop(k, None) for k in ("JUMP_FIRE_URL", "JUMP_FIRE_TOKEN")}
        try:
            ok, info = notify.fire_brain({"kind": "jump", "ids": ["a"]}, url_env="JUMP_FIRE_URL", token_env="JUMP_FIRE_TOKEN")
            self.assertFalse(ok)
            self.assertIn("JUMP_FIRE_URL", info)
        finally:
            for k, v in old.items():
                if v is not None:
                    os.environ[k] = v


if __name__ == "__main__":
    unittest.main()
