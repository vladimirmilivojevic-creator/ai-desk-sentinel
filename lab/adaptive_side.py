"""Biranje strane "prati ili suprotno" prema nedavnom ucinku: da li pomaze?
Parovi pravila sa ISTIM okidacem a suprotnom stranom (MOM/FADE, RSIFOLLOW/RSIFADE, DON_follow/DON_fade, BB_follow/BB_fade, CSM_mom/CSM_rev) daju dogadjaje sa
sirovim prinosom "prati" g (suprotna strana je tacno -g). U trenutku dogadjaja t strana se bira iz proseka g za dogadjaje starije od 24 h (ishod poznat) a mladje od W dana:
prosek > 0 -> prati, inace suprotno. Poredi se sa fiksnim "prati" i fiksnim "suprotno" (oba neto posle troska 0,23%).
Nulta hipoteza (vremenski izbor strane nema veze sa prinosima) = kruzno pomeranje niza strana po danima (cuva trajanje i ucestalost promena, lomi vezu sa prinosima).
Benjamini-Hochberg preko prozora W. Ne tvrdi nista bez dovoljno dogadjaja. Samo stdlib. Upotreba: python -m lab.adaptive_side [izlaz.md] [--fresh]"""
import os
import random
import statistics as st
import sys

from . import backtest, hourly_stops, rules, sim, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 24
DAY = 86400000
PAIRS = {"MOM": [v for v in rules.default_variants() if v[1] == "MOM" and not v[2]["fade"]],
         "RSI": [v for v in rules.default_variants() if v[1] == "RSIX" and not v[2]["fade"]],
         "DON": [v for v in rules.default_variants() if v[1] == "DON" and not v[2]["fade"]],
         "BB": [v for v in rules.default_variants() if v[1] == "BB" and not v[2]["fade"]],
         "CSM": [v for v in rules.default_variants() if v[1] == "CSM" and v[2]["momentum"]]}
WINDOWS = (3, 5, 7, 10, 14)
MIN_PAST = 20


def follow_events(series, ctx):
    """Lista (t, g, vid): sirovi prinos u % posle H svece za stranu 'prati', bez troska."""
    ev = []
    for fam, variants in PAIRS.items():
        for vid, f, params in variants:
            for sym, i, t, side in stats.thin(backtest.collect_signals(series, ctx, f, params, backtest.WARMUP), H):
                S = series[sym]
                if i + H >= S.n:
                    continue
                ev.append((t, sim.sign(side) * (S.c[i + H] / S.c[i] - 1.0) * 100.0, vid))
    ev.sort()
    return ev


def choose_sides(ev, window_days, lag_h=24, min_past=MIN_PAST):
    """Strana (+1 prati, -1 suprotno) za svaki dogadjaj ili None kad nema dovoljno proslosti. Dvostruki pokazivac, O(n)."""
    sides, lo, hi, s, n = [], 0, 0, 0.0, 0
    for t, g, _ in ev:
        while hi < len(ev) and ev[hi][0] <= t - lag_h * 3600000:
            s += ev[hi][1]
            n += 1
            hi += 1
        while lo < hi and ev[lo][0] < t - window_days * DAY:
            s -= ev[lo][1]
            n -= 1
            lo += 1
        sides.append((1 if s / n > 0 else -1) if n >= min_past else None)
    return sides


def evaluate(ev, sides, cost=sim.COST_PCT):
    rows = [(t, sd * g - cost, v) for (t, g, v), sd in zip(ev, sides) if sd is not None]
    return rows


def mean_net(ev, sides):
    r = [x[1] for x in evaluate(ev, sides)]
    return st.mean(r) if r else None


def shift_null(ev, sides, n_sims=500, seed=11):
    """Kruzno pomeranje strana po danima: srednji neto prinos za nasumicno vremensko poravnanje strana."""
    days = sorted({t // DAY for t, _, _ in ev})
    day_side = {}
    for (t, _, _), sd in zip(ev, sides):
        if sd is not None:
            day_side.setdefault(t // DAY, []).append(sd)
    ds = {d: (1 if st.mean(v) > 0 else -1) for d, v in day_side.items()}  # strana tog dana (vecina)
    base = [ds.get(d) for d in days]
    rnd = random.Random(seed)
    out = []
    n = len(days)
    for _ in range(n_sims):
        k = rnd.randrange(1, n)
        m = {d: base[(j + k) % n] for j, d in enumerate(days)}
        sd = [m.get(t // DAY) if sides[idx] is not None else None for idx, (t, _, _) in enumerate(ev)]
        v = mean_net(ev, sd)
        if v is not None:
            out.append(v)
    return out


def run(series, ctx):
    ev = follow_events(series, ctx)
    if len(ev) < 100:
        return {"status": "premalo dogadjaja", "events": len(ev)}
    t_min, t_max = ev[0][0], ev[-1][0]
    fixed = {"prati": [(t, g - sim.COST_PCT, v) for t, g, v in ev], "suprotno": [(t, -g - sim.COST_PCT, v) for t, g, v in ev]}
    out = {"status": "ok", "events": len(ev), "days": len({t // DAY for t, _, _ in ev}), "cost_pct": sim.COST_PCT, "windows": [],
           "fixed": {k: {"mean": round(st.mean(x[1] for x in v), 4), "t": stats.daily_t([(t, r) for t, r, _ in v])["t"]} for k, v in fixed.items()}}
    daily = {}
    for t, g, _ in ev:
        daily.setdefault(t // DAY, []).append(g)
    ds = [st.mean(v) for _, v in sorted(daily.items()) if len(v) >= 3]
    if len(ds) > 10:
        m = st.mean(ds)
        den = sum((x - m) ** 2 for x in ds)
        out["autocorr_lag1_daily_follow"] = round(sum((ds[i] - m) * (ds[i - 1] - m) for i in range(1, len(ds))) / den, 3) if den else None
    pv = []
    for w in WINDOWS:
        sides = choose_sides(ev, w)
        rows = evaluate(ev, sides)
        if len(rows) < 100:
            continue
        obs = st.mean(r[1] for r in rows)
        null = shift_null(ev, sides)
        p = (1 + sum(1 for x in null if x >= obs)) / (1 + len(null))
        out["windows"].append({"W": w, "n": len(rows), "mean_net": round(obs, 4), "t": stats.daily_t([(t, r) for t, r, _ in rows])["t"],
                               "follow_share": round(sum(1 for s in sides if s == 1) / sum(1 for s in sides if s is not None), 3),
                               "null_mean": round(st.mean(null), 4), "null_p95": round(sorted(null)[int(0.95 * len(null))], 4), "p": round(p, 4)})
        pv.append((w, p))
    ok = stats.bh_fdr(pv, 0.10)
    for r in out["windows"]:
        r["fdr"] = r["W"] in ok
    return out


def to_markdown(res):
    if res.get("status") != "ok":
        return "# Biranje strane\n\n%s (%s dogadjaja)\n" % (res.get("status"), res.get("events"))
    L = ["# Biranje strane prati / suprotno prema nedavnom ucinku", "",
         "Dogadjaja: %d u %d dana, trosak %.2f%%. Fiksno 'prati': %s%% (t %s); fiksno 'suprotno': %s%% (t %s). Autokorelacija dnevnog prosecnog 'prati' ishoda (lag 1): %s." % (
             res["events"], res["days"], res["cost_pct"], res["fixed"]["prati"]["mean"], res["fixed"]["prati"]["t"], res["fixed"]["suprotno"]["mean"], res["fixed"]["suprotno"]["t"],
             res.get("autocorr_lag1_daily_follow")), "",
         "| prozor W (dana) | n | neto % | t | udeo 'prati' | nulta srednja % | nulta 95. percentil % | p | prolazi FDR |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res["windows"]:
        L.append("| %d | %d | %+.3f | %s | %.2f | %+.3f | %+.3f | %.3f | %s |" % (r["W"], r["n"], r["mean_net"], r["t"], r["follow_share"], r["null_mean"], r["null_p95"], r["p"], "da" if r["fdr"] else "ne"))
    return "\n".join(L) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_md = args[0] if args else os.path.join(ROOT, "calibration", "adaptive_side.md")
    series = hourly_stops.load_series(fresh="--fresh" in sys.argv)
    ctx = backtest.make_ctx(series, (H,))
    res = run(series, ctx)
    md = to_markdown(res)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
