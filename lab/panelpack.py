"""Pakuje podatke za panel u male delove (pf/<ime>.<i>.json) jer alat read_link koji panel koristi ODSECA svaki odgovor na ~6000 znakova (JSON se lomi).
Svaki deo ima najvise LIMIT znakova; liste i recnici se seku po elementima, a panel delove sklapa (liste se nadovezuju, recnici spajaju).
Izlaz: <state>/pf/lab.*.json, brief.*.json, trig.*.json, feat.*.json. Samo stdlib. Upotreba: python -m lab.panelpack --state _state"""
import glob
import json
import os
import sys

LIMIT = 5400
SLOTS = {"lab": 6, "brief": 4, "trig": 3, "feat": 8, "disc": 5, "core": 3}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def size(o):
    return len(json.dumps(o, ensure_ascii=False, separators=(",", ":")))


def pack(sections, limit=LIMIT):
    """sections: lista (kljuc, vrednost). Skalari i male vrednosti su nedeljivi; liste i recnici se dele po elementima. Vraca listu delova (recnika)."""
    parts, cur = [], {}

    def flush():
        nonlocal cur
        if cur:
            parts.append(cur)
            cur = {}
    for key, val in sections:
        if size({key: val}) <= limit - (size(cur) if cur else 0) - 2:
            cur[key] = val
            continue
        if size({key: val}) <= limit:  # ne staje u tekuci deo, ali staje u prazan
            flush()
            cur[key] = val
            continue
        if isinstance(val, list):
            flush()
            cur[key] = []
            for it in val:
                cur[key].append(it)
                if size(cur) > limit:
                    cur[key].pop()
                    if not cur[key]:
                        raise ValueError("element liste '%s' je veci od limita" % key)
                    flush()
                    cur[key] = [it]
        elif isinstance(val, dict):
            flush()
            cur[key] = {}
            for k, v in val.items():
                cur[key][k] = v
                if size(cur) > limit:
                    cur[key].pop(k)
                    if not cur[key]:
                        raise ValueError("element recnika '%s' je veci od limita" % key)
                    flush()
                    cur[key] = {k: v}
        else:
            raise ValueError("vrednost '%s' je veca od limita i nedeljiva" % key)
    flush()
    return parts


def fit(sections, slots, limit=LIMIT):
    """Pakuje odeljke tako da staju u `slots` delova: ako ne staju, odbacuje odeljke od kraja (poredak = vaznost), a ako ni to ne pomogne,
    skracuje poslednju listu koja je ostala (npr. pravila) dok ne stane. Uvek vraca delove (nikad ne baca izuzetak zbog velicine)."""
    secs = list(sections)
    while secs:
        parts = pack(secs, limit)
        if len(parts) <= slots:
            return parts
        if len(secs) > 2:
            secs.pop()
            continue
        k, v = secs[-1]
        if isinstance(v, list) and len(v) > 1:
            secs[-1] = (k, v[:max(1, len(v) * 3 // 4)])
            continue
        secs.pop()
    return []


def write_parts(outdir, name, parts):
    """Brise stare delove istog dokumenta i upisuje nove; panel cita fiksan broj mesta (SLOTS), nepostojeca se preskacu."""
    os.makedirs(outdir, exist_ok=True)
    if len(parts) > SLOTS.get(name, 8):
        raise ValueError("dokument %s ima %d delova, a panel cita %d" % (name, len(parts), SLOTS.get(name, 8)))
    for f in glob.glob(os.path.join(outdir, name + ".*.json")):
        os.remove(f)
    for i, p in enumerate(parts):
        with open(os.path.join(outdir, "%s.%d.json" % (name, i)), "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, separators=(",", ":"))
    return len(parts)


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _short(s, n):
    s = str(s or "")
    return s if len(s) <= n else s[:n - 1] + "…"


def lab_sections(panel):
    reg = panel.get("registry") or {}
    hist = panel.get("history") or []
    live = [{"id": r["id"], "hold_hours": r.get("hold_hours"), "why": _short(r.get("why"), 110), "bt": {k: (r.get("bt") or {}).get(k) for k in ("n", "mean", "t", "t_train", "t_test", "verdict")},
             "fwd": {k: (r.get("fwd") or {}).get(k) for k in ("n", "mean")}, "signals": r.get("signals"), "test": r.get("test")} for r in panel.get("live", [])]
    top = [{k: r.get(k) for k in ("id", "test", "n", "mean", "t", "t_train", "t_test", "verdict")} for r in (panel.get("top_backtest") or [])[:10]]
    rules = [dict({k: r.get(k) for k in ("id", "interval", "status", "test", "n", "mean", "t", "recent_mean", "t_train", "t_test", "edge_groups", "live")},
                  unmet=[_short(x, 60) for x in (r.get("unmet") or [])[:2]]) for r in reg.get("rules", [])]
    head = {"updated_utc": panel.get("updated_utc"), "t0_utc": panel.get("t0_utc"), "hours_running": panel.get("hours_running"), "universe_n": panel.get("universe_n"),
            "totals": panel.get("totals"), "cost_pct": panel.get("cost_pct"), "features_rows": panel.get("features_rows"), "backtest_counts": panel.get("backtest_counts"),
            "demoted": panel.get("demoted"), "placebo": panel.get("placebo")}
    proof = panel.get("proof") or {}
    proof_rows = [{k: r.get(k) for k in ("id", "test", "n", "mean", "t", "t_days", "pct", "eta_days", "status", "e_mean", "e_t", "e_t_days", "beta")} for r in proof.get("rows", [])]
    return [("head", head), ("live", live), ("proof_target", proof.get("target")), ("proof", proof_rows), ("top_backtest", top), ("history", hist[-72:]),
            ("registry_head", {"generated_utc": reg.get("generated_utc"), "gates_version": reg.get("gates_version"), "counts": reg.get("counts")}), ("registry_rules", rules)]


def brief_sections(b, health=None):
    keys = ("updated_utc", "regime", "scalars", "extremes_z>=2", "n_features", "key_sources", "source_health_failing", "calendar_next_72h", "earnings_next_14d", "extra",
            "costliest_to_trade", "macro", "sentiment", "smart_money_top", "evidence", "universe_liquid_n")
    return [(k, b[k]) for k in keys if k in b and b[k] is not None]


def trig_sections(t):
    live = [{k: x.get(k) for k in ("variant", "sym", "side", "stop_pct", "tp_pct", "hold_hours", "interval", "bt_verdict", "live")} for x in (t.get("triggers") or []) if x.get("live")]
    return [("updated_utc", t.get("updated_utc")), ("bar_utc", t.get("bar_utc")), ("marks", t.get("marks") or {}), ("live_variants", t.get("live_variants") or {}), ("triggers", live[:24]),
            ("other_triggers", t.get("other_triggers"))]


def feat_sections(f):
    meta = f.get("meta") or {}
    rows = [[k, (meta.get(k) or ["", k])[0], _short((meta.get(k) or ["", k])[1], 80), v.get("v"), v.get("z")] for k, v in (f.get("features") or {}).items()]
    rows.sort(key=lambda r: (r[1], r[0]))
    return [("updated_utc", f.get("updated_utc")), ("n", f.get("n")), ("rows", rows)]


def disc_sections(root):
    """Lovac (lab/discovery.py): sazetak pravila, izbora unapred, radara i najboljih testova. Fajlovi su na main grani (discovery/, calibration/)."""
    rules = (_load(os.path.join(root, "discovery", "rules.json")) or {}).get("rules")
    study = _load(os.path.join(root, "calibration", "discovery.json"))
    if rules is None and not study:
        return None
    radar = _load(os.path.join(root, "discovery", "radar.json")) or {}
    tests = (study or {}).get("tests") or []
    cnt = {}
    for t in tests:
        cnt[t["status"]] = cnt.get(t["status"], 0) + 1
    rc = {}
    for r in (rules or {}).values():
        rc[r["status"]] = rc.get(r["status"], 0) + 1
    head = {"study_utc": (study or {}).get("generated_utc"), "rules_utc": (_load(os.path.join(root, "discovery", "rules.json")) or {}).get("updated_utc"),
            "radar_utc": radar.get("generated_utc"), "universes": (study or {}).get("universes"), "n_tests": len(tests), "test_counts": cnt, "rule_counts": rc,
            "cfg": (study or {}).get("cfg_summary")}
    keys = ("n", "mean", "median", "mean_ex_best", "t", "p", "recent_mean")
    rl = [{"id": rid, "status": r["status"], "since": r.get("forward_start"), "promoted": r.get("promoted_utc"),
           "study": {k: (r.get("study") or {}).get(k) for k in keys},
           "fwd": {k: (r.get("forward") or {}).get(k) for k in ("n", "mean", "t", "sim_mean", "mean_ex_best", "pending")}} for rid, r in sorted((rules or {}).items())]
    now_s = radar.get("generated_utc") or ""
    rd = [{"rule": x["rule"], "status": x["status"], "side": x["side"], "signal_date": x["signal_date"], "from": x["valid_from_utc"], "to": x["valid_until_utc"],
           "hold_hours": x["hold_hours"], "picks": [{k: p.get(k) for k in ("ticker", "px", "stop_pct", "tp_pct", "score")} for p in x["picks"]]}
          for x in radar.get("rules", []) if not now_s or x["valid_until_utc"] >= now_s]  # istekli prozori se ne prikazuju (i ne pune dokument)
    top = [{k: t.get(k) for k in ("id", "n", "mean", "median", "mean_ex_best", "t", "status")} for t in sorted(tests, key=lambda t: -(t["t"] if t.get("t") is not None else -99))[:10]]
    return [("head", head), ("rules", rl), ("radar", rd), ("top", top), ("cases", (study or {}).get("cases") or [])]


def core_sections(c, max_points=120):
    """Jezgro (lab/core.py): glava, tezine i signali, senka unapred (kriva proredjena na max_points) i istorijska referenca. Redosled = vaznost."""
    sh = dict(c.get("shadow") or {})
    cur = sh.pop("curve", None) or []
    if len(cur) > max_points:
        step = -(-len(cur) // max_points)
        cur = cur[::step][:-1] + [cur[-1]]
    head = {k: c.get(k) for k in ("updated_utc", "config_version", "t0_candle", "last_candle", "gross", "cash", "weights_date", "next_rebalance_candle", "schedule_only_ret_pct")}
    bt = c.get("backtest") or {}
    ref = {k: bt.get(k) for k in ("from", "to", "yearly_pct", "yearly_buyhold_pct", "yearly_btc_pct", "full", "buyhold_full", "periods", "placebo_periods", "placebo_sharpe_mean", "months")} if bt else None
    return [("head", head), ("weights", c.get("weights") or {}), ("signals", c.get("signals") or {}), ("shadow", sh), ("ref", ref), ("curve", cur)]


def build(state_dir, root=ROOT):
    out = os.path.join(state_dir, "pf")
    res = {}
    errors = {}

    def doc(name, loader, sections, packer=pack):
        try:
            src = loader()
            if src:
                res[name] = write_parts(out, name, packer(sections(src)))
        except Exception as e:  # noqa: BLE001  # jedan dokument nikad ne obara pakovanje ostalih (2026-10-14: Lovac je pao pa su svi posle njega ostali neosvezeni)
            errors[name] = "%s: %s" % (type(e).__name__, e)
    doc("lab", lambda: _load(os.path.join(state_dir, "lab", "panel.json")), lab_sections)
    doc("brief", lambda: _load(os.path.join(state_dir, "data", "briefing.json")), brief_sections)
    doc("trig", lambda: _load(os.path.join(state_dir, "lab", "triggers.json")), trig_sections)
    doc("feat", lambda: _load(os.path.join(state_dir, "data", "features.json")), feat_sections)
    doc("disc", lambda: disc_sections(root), lambda ds: ds, packer=lambda secs: fit(secs, SLOTS["disc"]))
    doc("core", lambda: _load(os.path.join(state_dir, "core", "core.json")), core_sections, packer=lambda secs: fit(secs, SLOTS["core"]))
    if errors:
        res["errors"] = errors
    return res


def main():
    argv = sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        res = build(state)
    except Exception as e:  # noqa: BLE001  # pakovanje nikad ne obara stražu
        res = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
