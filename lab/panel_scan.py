"""Pregled panela: koja osobina zaista predvidja prinos? Dva testa, oba sa korekcijom za mnogo testova (Benjamini-Hochberg):
1) osobine po instrumentu: svakog sata Spearman korelacija (IC) izmedju osobine i prinosa instrumenta MINUS prosek svih instrumenata (poredak unutar preseka);
   IC se uprosecava po UTC danima, t se racuna preko dana (sati istog dana nisu nezavisni).
2) globalne osobine (VIX, strah/pohlepa, HY OAS, Trump brojke...): korelacija sa narednim prinosom prosecnog instrumenta; t sa efektivnim brojem dana.
Ispod MIN_DAYS dana ne tvrdi nista. Samo stdlib. Upotreba: python -m lab.panel_scan [state_dir] [out_md] [out_json]"""
import datetime as dt
import json
import math
import os
import statistics as st
import sys

from . import panelstore, stats

HOUR = panelstore.HOUR
MIN_DAYS = 7
MIN_CROSS = 8
HORIZONS = (4, 24)


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return None if den == 0 else num / den


def _day(t):
    return t // (24 * HOUR)


def t_over_days(vals_by_day):
    d = [st.mean(v) for v in vals_by_day.values() if v]
    n = len(d)
    if n < 3:
        return None, n, None
    sd = st.stdev(d)
    m = st.mean(d)
    return (None if sd == 0 else m / (sd / math.sqrt(n))), n, m


def instrument_ic(rows, horizons=HORIZONS):
    by_t = {}
    for r in rows:
        by_t.setdefault(r["t"], []).append(r)
    res = {}
    for h in horizons:
        key = "yx%d" % h
        feats = sorted({k for r in rows for k in r["x"]})
        for f in feats:
            per_day = {}
            for t, rs in by_t.items():
                pts = [(r["x"][f], r[key]) for r in rs if f in r["x"] and key in r and r["x"][f] is not None]
                if len(pts) < MIN_CROSS:
                    continue
                ic = spearman([p[0] for p in pts], [p[1] for p in pts])
                if ic is not None:
                    per_day.setdefault(_day(t), []).append(ic)
            t_, n_days, mean_ic = t_over_days(per_day)
            if t_ is not None:
                res[(f, h)] = {"feature": f, "h": h, "mean_ic": round(mean_ic, 4), "t": round(t_, 2), "days": n_days, "p": stats.t_to_p(t_)}
    return res


def global_corr(g_rows, horizons=HORIZONS):
    px = panelstore.price_index(g_rows)
    res = {}
    for h in horizons:
        ts_ = sorted(t for t in px if (t + h * HOUR) in px)
        mret = {}
        for t in ts_:
            a, b = px[t], px[t + h * HOUR]
            v = [(b[s] / p - 1.0) * 100.0 for s, p in a.items() if p and b.get(s)]
            if len(v) >= MIN_CROSS:
                mret[t] = st.mean(v)
        names = sorted({k for r in g_rows for k in r["f"]})
        by_t = {r["t"]: r["f"] for r in g_rows}
        for f in names:
            pts = [(by_t[t][f], mret[t]) for t in mret if t in by_t and f in by_t[t]]
            days = len({_day(t) for t in mret if t in by_t and f in by_t[t]})
            if len(pts) < 24 or days < MIN_DAYS:
                continue
            r = spearman([p[0] for p in pts], [p[1] for p in pts])
            if r is None or abs(r) >= 0.999999:
                continue
            t_ = r * math.sqrt(max(days - 2, 1)) / math.sqrt(1 - r * r)
            res[(f, h)] = {"feature": f, "h": h, "rho": round(r, 4), "t": round(t_, 2), "days": days, "p": stats.t_to_p(t_)}
    return res


def run(state_dir):
    g_rows, i_rows = panelstore.load(state_dir)
    rows = panelstore.dataset(g_rows, i_rows)
    days = len({_day(r["t"]) for r in rows})
    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "rows": len(rows), "days_with_outcome": days, "global_rows": len(g_rows), "inst_rows": len(i_rows)}
    if days < MIN_DAYS:
        out["status"] = "premalo podataka: %d od %d dana sa ishodom" % (days, MIN_DAYS)
        return out
    inst = instrument_ic(rows)
    glob = global_corr(g_rows)
    for name, res in (("instrument", inst), ("global", glob)):
        items = list(res.items())
        ok = stats.bh_fdr([(k, v["p"]) for k, v in items], 0.10)
        out[name] = {"tests": len(items), "fdr_pass": len(ok), "top": sorted(({**v, "fdr": k in ok} for k, v in items), key=lambda x: -abs(x["t"]))[:15]}
    out["status"] = "ok"
    return out


def to_markdown(res):
    L = ["# Panel: koja osobina predvidja prinos?", "", "Redova (instrument x sat) sa ishodom: %s, dana: %s. %s" % (res["rows"], res["days_with_outcome"], res.get("status", ""))]
    for name, label in (("instrument", "Osobine po instrumentu (IC = korelacija ranga osobine i prinosa preko instrumenata)"), ("global", "Globalne osobine (korelacija sa prinosom prosecnog instrumenta)")):
        b = res.get(name)
        if not b:
            continue
        L += ["", "## " + label, "", "Testova: %d, prolazi FDR 10%%: %d." % (b["tests"], b["fdr_pass"]), "", "| osobina | sati | %s | t | dana | FDR |" % ("IC" if name == "instrument" else "rho"), "|---|---|---|---|---|---|"]
        for x in b["top"]:
            L.append("| %s | %d | %+.3f | %.2f | %d | %s |" % (x["feature"], x["h"], x.get("mean_ic", x.get("rho")), x["t"], x["days"], "da" if x["fdr"] else "ne"))
    return "\n".join(L) + "\n"


def main():
    state = sys.argv[1] if len(sys.argv) > 1 else "_state"
    out_md = sys.argv[2] if len(sys.argv) > 2 else os.path.join(state, "lab", "panel_scan.md")
    out_json = sys.argv[3] if len(sys.argv) > 3 else os.path.join(state, "lab", "panel_scan.json")
    res = run(state)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res))
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
