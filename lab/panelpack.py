"""Pakuje podatke za panel u male delove (pf/<ime>.<i>.json) jer alat read_link koji panel koristi ODSECA svaki odgovor na ~6000 znakova (JSON se lomi).
Svaki deo ima najvise LIMIT znakova; liste i recnici se seku po elementima, a panel delove sklapa (liste se nadovezuju, recnici spajaju).
Izlaz: <state>/pf/lab.*.json, brief.*.json, trig.*.json, feat.*.json. Samo stdlib. Upotreba: python -m lab.panelpack --state _state"""
import glob
import json
import os
import sys

LIMIT = 5400
SLOTS = {"lab": 6, "brief": 4, "trig": 3, "feat": 8, "disc": 3}
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


def write_parts(outdir, name, parts):
    """Brise stare delove istog dokumenta i upisuje nove; panel cita fiksan broj mesta (SLOTS), nepostojeca se preskacu."""
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, name + ".*.json")):
        os.remove(f)
    if len(parts) > SLOTS.get(name, 8):
        raise ValueError("dokument %s ima %d delova, a panel cita %d" % (name, len(parts), SLOTS.get(name, 8)))
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
    return [("head", head), ("live", live), ("top_backtest", top), ("history", hist[-72:]), ("registry_head", {"generated_utc": reg.get("generated_utc"), "gates_version": reg.get("gates_version"),
            "counts": reg.get("counts")}), ("registry_rules", rules)]


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
    rd = [{"rule": x["rule"], "status": x["status"], "side": x["side"], "signal_date": x["signal_date"], "from": x["valid_from_utc"], "to": x["valid_until_utc"],
           "hold_hours": x["hold_hours"], "picks": [{k: p.get(k) for k in ("ticker", "px", "stop_pct", "tp_pct", "score")} for p in x["picks"]]} for x in radar.get("rules", [])]
    top = [{k: t.get(k) for k in ("id", "n", "mean", "median", "mean_ex_best", "t", "status")} for t in sorted(tests, key=lambda t: -(t["t"] if t.get("t") is not None else -99))[:10]]
    return [("head", head), ("rules", rl), ("radar", rd), ("top", top), ("cases", (study or {}).get("cases") or [])]


def build(state_dir, root=ROOT):
    out = os.path.join(state_dir, "pf")
    res = {}
    panel = _load(os.path.join(state_dir, "lab", "panel.json"))
    if panel:
        res["lab"] = write_parts(out, "lab", pack(lab_sections(panel)))
    b = _load(os.path.join(state_dir, "data", "briefing.json"))
    if b:
        res["brief"] = write_parts(out, "brief", pack(brief_sections(b)))
    t = _load(os.path.join(state_dir, "lab", "triggers.json"))
    if t:
        res["trig"] = write_parts(out, "trig", pack(trig_sections(t)))
    f = _load(os.path.join(state_dir, "data", "features.json"))
    if f:
        res["feat"] = write_parts(out, "feat", pack(feat_sections(f)))
    try:
        ds = disc_sections(root)
    except Exception:  # noqa: BLE001  # Lovac nikad ne obara pakovanje ostalih dokumenata
        ds = None
    if ds:
        res["disc"] = write_parts(out, "disc", pack(ds))
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
