"""Prikupljanje dodatnih podataka (fonding, otvoreni interes, premija, obim) svaki sat i kasnija studija: da li se njima moze predvideti
sledeci prinos. Novi podaci se skupljaju UNAPRED (istorijski OI ne postoji u javnom API-ju), pa studija ima smisla tek posle dana/nedelja.
Sve je deterministicko i bez AI-ja. Izlaz: <state>/lab/features.jsonl (poslednjih 45 dana) i izvestaj `python -m lab.feature_study`."""
import json
import math
import os
import statistics as st

from . import data

KEEP_ROWS = 24 * 45


def collect(universe, bar_ms):
    """Jedan red: {t, f: {sym: [mark, funding, oi_usd, premium, vol24h_usd]}} iz metaAndAssetCtxs (glavni dex i xyz)."""
    want = {u["hl"]: u["sym"] for u in universe}
    row = {}
    for dex in (None, "xyz"):
        body = {"type": "metaAndAssetCtxs"}
        if dex:
            body["dex"] = dex
        meta, ctxs = data._post(body)
        for a, c in zip(meta["universe"], ctxs):
            sym = want.get(a["name"])
            if not sym:
                continue
            try:
                mark = float(c["markPx"])
                row[sym] = [mark, float(c.get("funding") or 0.0), round(float(c.get("openInterest") or 0.0) * mark, 2),
                            float(c.get("premium") or 0.0), round(float(c.get("dayNtlVlm") or 0.0), 2)]
            except (KeyError, TypeError, ValueError):
                continue
    return {"t": bar_ms, "f": row}


def load(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    except OSError:
        pass
    return rows


def append(path, row):
    """Dodaje red (jedan po satu), cuva poslednjih KEEP_ROWS."""
    rows = load(path)
    if rows and rows[-1].get("t") == row["t"]:
        return len(rows)
    rows.append(row)
    rows = rows[-KEEP_ROWS:]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    os.replace(tmp, path)
    return len(rows)


def rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    for r, i in enumerate(order):
        out[i] = float(r)
    return out


def spearman(x, y):
    if len(x) < 5:
        return None
    rx, ry = rank(x), rank(y)
    mx, my = st.mean(rx), st.mean(ry)
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy)


FEATURES = {
    "funding": lambda cur, prev: cur[1],
    "oi_change_24h": lambda cur, prev: None if (prev is None or prev[2] <= 0) else cur[2] / prev[2] - 1.0,
    "premium": lambda cur, prev: cur[3],
    "vol_change_24h": lambda cur, prev: None if (prev is None or prev[4] <= 0) else cur[4] / prev[4] - 1.0,
}


def study(rows, horizons=(4, 24)):
    """Poprecna (cross-sectional) Spearman korelacija svake osobine sa narednim prinosom, po vremenu; t se racuna po DANIMA
    (satni redovi su jako povezani). Vraca {osobina: {H: {days, mean_ic, t}}}."""
    by_t = {r["t"]: r["f"] for r in rows}
    ts = sorted(by_t)
    out = {}
    day_ms = 86400000
    for name, fn in FEATURES.items():
        out[name] = {}
        for H in horizons:
            per_day = {}
            for t in ts:
                fut = by_t.get(t + H * 3600000)
                if fut is None:
                    continue
                prev = by_t.get(t - 24 * 3600000)
                xs, ys = [], []
                for sym, cur in by_t[t].items():
                    if sym not in fut or fut[sym][0] <= 0 or cur[0] <= 0:
                        continue
                    v = fn(cur, prev.get(sym) if prev else None)
                    if v is None:
                        continue
                    xs.append(v)
                    ys.append(fut[sym][0] / cur[0] - 1.0)
                ic = spearman(xs, ys)
                if ic is not None:
                    per_day.setdefault(t // day_ms, []).append(ic)
            daily = [sum(v) / len(v) for v in per_day.values()]
            if len(daily) >= 3:
                m, sd = st.mean(daily), st.stdev(daily)
                out[name][H] = {"days": len(daily), "mean_ic": round(m, 4), "t": None if sd == 0 else round(m / (sd / math.sqrt(len(daily))), 2)}
            else:
                out[name][H] = {"days": len(daily), "mean_ic": None, "t": None}
    return out


def report(res, n_rows):
    L = ["# Studija osobina (fonding, OI, premija, obim)", "", "Redova (sati): %d. IC = poprečna Spearman korelacija osobine sa narednim prinosom; t po danima." % n_rows, "",
         "| osobina | horizont | dana | srednji IC | t |", "|---|---|---|---|---|"]
    for name, hs in res.items():
        for H, r in hs.items():
            L.append("| %s | %d h | %d | %s | %s |" % (name, H, r["days"], r["mean_ic"], r["t"]))
    L.append("")
    L.append("Pozitivan IC: veća vrednost osobine prethodi većem prinosu; negativan: manjem. Ispod 10 dana t nije pouzdan.")
    return "\n".join(L) + "\n"
