"""Registar dokaza: status svakog pravila po unapred zadatim kapijama (config/registry_gates.json).
Statusi: odbacen | kandidat | probni | ziv | penzionisan. Pravilo ne preskace stepenice: 'probni' trazi istorijske kapije,
'ziv' trazi jos i kapije unapred (n, dani, pobeda nad placebom). Cista funkcija nad rezultatima laba (bez mreze i bez AI).
Upotreba: python -m lab.registry [izlaz.json] [izlaz.md] [forward_stats.json]"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_ORDER = ("ziv", "probni", "kandidat", "odbacen", "penzionisan")


def load_gates(path=None):
    with open(path or os.path.join(ROOT, "config", "registry_gates.json"), encoding="utf-8") as f:
        return json.load(f)


def _hist_row(r):
    s = r["stats"]
    w = (s.get("windows") or {}).get("last270d") or {}
    groups = r.get("groups") or {}
    return {"test": r["test"], "n": s.get("n", 0), "days": s.get("all", {}).get("days"), "mean": s.get("mean"), "t": s.get("all", {}).get("t"),
            "t_train": s.get("train", {}).get("t"), "t_test": s.get("test", {}).get("t"), "recent_mean": w.get("mean"), "recent_t": w.get("t"),
            "fdr": bool(r.get("fdr_pass")), "lab_verdict": r.get("verdict"),
            "edge_groups": sorted(g for g, v in groups.items() if v.get("n", 0) >= 30 and (v.get("mean") or 0) > 0),
            "group_means": {g: v.get("mean") for g, v in groups.items() if v.get("n", 0) >= 30}}


def best_hist(rows, gates):
    """Najbolji E-test pravila (po t) medju onima sa dovoljno uzoraka; redosled preferencije samo razbija nerešeno."""
    h = gates["hist"]
    ok = [x for x in rows if x["test"].startswith("E") and x["n"] >= h["min_n"] and x["t"] is not None]
    if not ok:
        ok = [x for x in rows if x["test"].startswith("E") and x["t"] is not None]
    if not ok:
        return None
    pref = h.get("prefer_tests", [])
    return max(ok, key=lambda x: (x["t"], -(pref.index(x["test"]) if x["test"] in pref else 99)))


def hist_failures(b, gates):
    """Spisak neprolaznih istorijskih kapija (prazan = sve proslo)."""
    h, bad = gates["hist"], []
    if b["n"] < h["min_n"]:
        bad.append("n %d < %d" % (b["n"], h["min_n"]))
    if (b["days"] or 0) < h["min_days"]:
        bad.append("dana %s < %d" % (b["days"], h["min_days"]))
    if (b["t"] or 0) < h["min_t_all"]:
        bad.append("t %.2f < %.1f" % (b["t"] or 0, h["min_t_all"]))
    if h.get("fdr_required") and not b["fdr"]:
        bad.append("ne prolazi FDR 10%")
    if b["recent_mean"] is None or b["recent_mean"] <= h["recent_mean_gt"]:
        bad.append("poslednjih 270 d srednje %s <= %s" % (b["recent_mean"], h["recent_mean_gt"]))
    if (b["t_train"] if b["t_train"] is not None else -9) <= h["train_t_min"]:
        bad.append("prvi deo t %s" % b["t_train"])
    if (b["t_test"] if b["t_test"] is not None else -9) < h["test_t_min"]:
        bad.append("drugi deo t %s < %.1f" % (b["t_test"], h["test_t_min"]))
    return bad


def fwd_failures(f, placebo_mean, gates):
    """f: forward ishod ({n, mean, days, t_naive}) ili None. Vraca (spisak neprolaznih, penzionisati?)."""
    g, d = gates["fwd"], gates["demote"]
    if not f or not f.get("n"):
        return ["nema ishoda unapred"], False
    retire = f["n"] >= d["min_n"] and f.get("t_naive") is not None and f["t_naive"] <= d["t_naive_max"] and (f.get("mean") or 0) < 0
    bad = []
    if f["n"] < g["min_n"]:
        bad.append("unapred n %d < %d" % (f["n"], g["min_n"]))
    if (f.get("days") or 0) < g["min_days"]:
        bad.append("unapred dana %s < %d" % (f.get("days"), g["min_days"]))
    if f.get("t_naive") is None or f["t_naive"] < g["t_naive_min"]:
        bad.append("unapred t %s < %.1f" % (f.get("t_naive"), g["t_naive_min"]))
    if placebo_mean is not None and (f.get("mean") or 0) < placebo_mean + g["beat_placebo_by_pct"]:
        bad.append("unapred ne pobedjuje placebo (%.3f vs %.3f)" % (f.get("mean") or 0, placebo_mean))
    return bad, retire


def classify(rows, fwd, placebo_mean, gates):
    """(status, razlozi, najbolji istorijski red) za jedno pravilo."""
    b = best_hist(rows, gates)
    if b is None:
        return "kandidat", ["nema istorijskog testa"], None
    if (b["t"] or 0) < gates["reject"]["t_all_below"] or (b["mean"] or 0) <= 0:
        return "odbacen", ["t %s, srednje %s" % (b["t"], b["mean"])], b
    bad = hist_failures(b, gates)
    if bad:
        return "kandidat", bad, b
    fbad, retire = fwd_failures(fwd, placebo_mean, gates)
    if retire:
        return "penzionisan", ["unapred jasno gubi: " + ", ".join(fbad)], b
    if fbad:
        return "probni", fbad, b
    return "ziv", [], b


def build(results, fwd_stats=None, gates=None, now=None):
    """results: lista redova backtest-a (bez placeba) sa 'id','test','stats','groups','fdr_pass','verdict', plus 'interval'.
    fwd_stats: sadrzaj state/lab/stats.json (neobavezno)."""
    gates = gates or load_gates()
    by_id = {}
    for r in results:
        if "PLACEBO" in r["id"] or "RAND" in r["id"]:
            continue
        by_id.setdefault(r["id"], {"family": r.get("family"), "interval": r.get("interval"), "rows": []})["rows"].append(_hist_row(r))
    fv = (fwd_stats or {}).get("variants", {})
    items = []
    for vid, v in sorted(by_id.items()):
        daily = v["interval"] == "1d"
        key = "E7" if daily else "E24"
        pl = fv.get("D_PLACEBO_p5" if daily else "PLACEBO_p2", {}).get("tests", {}).get(key, {}).get("mean")
        fwd = fv.get(vid, {}).get("tests", {}).get(key)
        status, why, b = classify(v["rows"], fwd, pl, gates)
        items.append({"id": vid, "family": v["family"], "interval": v["interval"], "status": status, "unmet": why, "best": b, "fwd": fwd})
    counts = {}
    for it in items:
        counts[it["status"]] = counts.get(it["status"], 0) + 1
    items.sort(key=lambda x: (STATUS_ORDER.index(x["status"]), -((x["best"] or {}).get("t") or -99)))
    return {"generated_utc": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "gates_version": gates["version"], "counts": counts,
            "rules": items}


def to_markdown(reg, top=25):
    L = ["# Registar dokaza", "",
         "Generisano %s, kapije v%s (config/registry_gates.json). Statusi: %s." % (reg["generated_utc"], reg["gates_version"],
                                                                                 ", ".join("%s %d" % (k, v) for k, v in sorted(reg["counts"].items()))), "",
         "| pravilo | interval | status | test | n | srednje % | t | poslednjih 270 d | t prvi / drugi deo | grupe sa prednoscu | sta fali |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for it in reg["rules"][:top]:
        b = it["best"] or {}
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s |" % (
            it["id"], it["interval"], it["status"], b.get("test"), b.get("n"), b.get("mean"), b.get("t"), b.get("recent_mean"), b.get("t_train"),
            b.get("t_test"), ", ".join(b.get("edge_groups") or []) or "-", "; ".join(it["unmet"]) or "-"))
    return "\n".join(L) + "\n"


def load_results(paths):
    out = []
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        for r in d.get("results", []):
            out.append(dict(r, interval=d.get("interval")))
    return out


def main():
    out_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "calibration", "registry.json")
    out_md = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "calibration", "registry.md")
    fwd = None
    if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
        with open(sys.argv[3], encoding="utf-8") as f:
            fwd = json.load(f)
    cal = os.path.join(ROOT, "calibration")
    paths = [os.path.join(cal, "lab_v3_1d.json"), os.path.join(cal, "lab_v3_1h.json")]
    results = load_results(paths) or load_results([os.path.join(cal, "lab_backtest_1d.json"), os.path.join(cal, "lab_backtest_1h.json")])
    reg = build(results, fwd)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(reg))
    print("registar:", reg["counts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
