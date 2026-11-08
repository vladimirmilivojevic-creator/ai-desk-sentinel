"""Doprinos izvora podataka (bez AI-ja, besplatno): svakog dana racuna kros-sekcioni rang IC (Spearman) osobina po instrumentu (fonding, premija, otvoreni interes,
promena OI, promena obima, prethodni prinos) u 00:00 UTC prema prinosu instrumenta posle +24 h i +72 h, iz satnog zapisa data lake-a (data/panel_inst.jsonl,
data/panel_global.jsonl). Dnevni IC-jevi se cuvaju i gomilaju, pa dokaz raste svakim danom. t = prosek IC / standardna greska preko dana; BH-FDR 10% preko svih osobina.
Nista ne trguje. Izlaz: <state>/ic/ic.json. Upotreba: python -m lab.ic_track --state _state"""
import json
import math
import os
import statistics as st
import sys
import time

from . import stats as S

H = 3600000
FEATS = ("funding_h", "premium", "oi_chg24", "vol_ratio", "ret24", "ret72", "oi_usd_log")
HORIZONS = (24, 72)
MIN_NAMES = 8


def _rank(x):
    o = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    for k, i in enumerate(o):
        r[i] = float(k)
    return r


def spearman(a, b):
    if len(a) < MIN_NAMES:
        return None
    ra, rb = _rank(a), _rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    c = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    v = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return c / v if v else None


def _read_jsonl(path):
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    out[int(r["t"])] = r
                except (ValueError, KeyError, TypeError):
                    continue
    except OSError:
        pass
    return out


def feature_value(feat, s, t, inst, mark):
    v = inst[t].get(s) or {}
    if feat in ("funding_h", "premium"):
        return v.get(feat)
    if feat == "oi_usd_log":
        return math.log(v["oi_usd"]) if v.get("oi_usd") else None
    t24, t72 = t - 24 * H, t - 72 * H
    if feat == "oi_chg24":
        o0 = (inst.get(t24) or {}).get(s, {}).get("oi_usd")
        return (v["oi_usd"] / o0 - 1) if o0 and v.get("oi_usd") else None
    if feat == "vol_ratio":
        v0 = (inst.get(t24) or {}).get(s, {}).get("vol24")
        return (v["vol24"] / v0 - 1) if v0 and v.get("vol24") else None
    p = mark(t24 if feat == "ret24" else t72, s)
    m0 = mark(t, s)
    return (m0 / p - 1) if p and m0 else None


def daily_ics(inst, glob):
    """{datum: {'feat|h': IC}} za sve 00:00 UTC za koje postoji ishod."""
    def mark(t, s):
        g = glob.get(t)
        return None if not g else (g.get("m") or {}).get(s)
    out = {}
    for t in sorted(inst):
        if (t // H) % 24 != 0 or t not in glob:
            continue
        day = time.strftime("%Y-%m-%d", time.gmtime(t / 1000.0))
        for fh in HORIZONS:
            tf = t + fh * H
            if tf not in glob:
                continue
            for feat in FEATS:
                xs, ys = [], []
                for s in inst[t]:
                    m0, m1 = mark(t, s), mark(tf, s)
                    if not m0 or not m1:
                        continue
                    x = feature_value(feat, s, t, inst, mark)
                    if x is None:
                        continue
                    xs.append(float(x))
                    ys.append(m1 / m0 - 1.0)
                ic = spearman(xs, ys)
                if ic is not None:
                    out.setdefault(day, {})["%s|%d" % (feat, fh)] = round(ic, 4)
    return out


def summarize(daily, q=0.10):
    keys = sorted({k for d in daily.values() for k in d})
    rows, pv = [], []
    for k in keys:
        v = [d[k] for _, d in sorted(daily.items()) if k in d]
        n = len(v)
        if n < 8:
            continue
        m, sd = st.mean(v), st.stdev(v)
        feat, h = k.split("|")
        n_eff = n / max(1, int(h) // 24)  # prozori +72 h se preklapaju (dnevni uzorak), pa je nezavisnih posmatranja manje
        t = m / (sd / math.sqrt(n_eff)) if sd else 0.0
        p = math.erfc(abs(t) / math.sqrt(2.0))
        rows.append({"feat": feat, "h": int(h), "n_days": n, "mean_ic": round(m, 4), "t": round(t, 2), "p": round(p, 4), "last7": round(st.mean(v[-7:]), 4)})
        pv.append((k, p))
    passed = S.bh_fdr(pv, q) if pv else set()
    for r in rows:
        r["fdr"] = ("%s|%d" % (r["feat"], r["h"])) in passed
    rows.sort(key=lambda r: -abs(r["t"]))
    return rows


def run(state_dir, now_ms=None, log=print):
    now_ms = now_ms or int(time.time() * 1000)
    d = os.path.join(state_dir, "data")
    inst = _read_jsonl(os.path.join(d, "panel_inst.jsonl"))
    for t, r in list(inst.items()):
        inst[t] = r.get("i") or {}
    glob = _read_jsonl(os.path.join(d, "panel_global.jsonl"))
    if len(inst) < 48 or len(glob) < 48:
        return {"skipped": "premalo satnih zapisa"}
    path = os.path.join(state_dir, "ic", "ic.json")
    try:
        with open(path, encoding="utf-8") as f:
            prev = json.load(f)
    except (OSError, ValueError):
        prev = {}
    daily = dict(prev.get("daily") or {})
    for day, v in daily_ics(inst, glob).items():
        daily.setdefault(day, {}).update(v)
    rows = summarize(daily)
    out = {"schema": 1, "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ms / 1000.0)), "n_days": len(daily),
           "n_tests": len(rows), "rows": rows, "daily": daily,
           "note": "IC = rang korelacija osobine sa kasnijim prinosom preko instrumenata; t preko dana (prozori +72 h korigovani za preklapanje); tek |t| >= 3 uz FDR i vise nedelja vredi pomena. Jedan rezim tržišta nije dokaz."}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(path + ".tmp", path)
    return {"ok": out["updated_utc"], "days": len(daily), "tests": len(rows)}


def main(argv=None):
    argv = argv or sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        print("ic:", json.dumps(run(state), ensure_ascii=False))
    except Exception as e:  # noqa: BLE001
        print("ic: greska (ignorisano):", str(e)[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
