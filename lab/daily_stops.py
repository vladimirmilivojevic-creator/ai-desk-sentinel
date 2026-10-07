"""Dnevna pravila: testirano (fiksno drzanje H dana) nasuprot uzivo (stop 2,5 x ATR u granicama 3-12% i cilj 3 x stop). Meri da li stop i cilj
menjaju ocekivanje, koliko cesto se pogode i kolika je najveca nepovoljna/povoljna ekskurzija (MAE/MFE) unutar drzanja.
Samo stdlib. Upotreba: python -m lab.daily_stops [izlaz.md] [grupa=crypto] (LAB_CONFIG=config/lab_v3.json)"""
import os
import statistics as st
import sys

from . import backtest, rules, sim, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 7
# (ATR mnozilac, donja granica %, gornja granica %, cilj = tp_mult x stop)
MODES = {"fiksno": None, "uzivo": (2.5, 3.0, 12.0, 3.0), "uzi": (1.5, 2.0, 8.0, 3.0), "siri": (4.0, 5.0, 20.0, 3.0)}
RULES = ("D_MOM_L7_z0.5", "D_MOM_L21_z0.5", "D_MOM_L14_z1.0", "D_CSM_mom_L7", "D_CSM_mom_L14", "D_CSM_mom_L30")


def stop_for(S, i, mode):
    m, lo, hi, _ = MODES[mode]
    a = S.atr_pct[i]
    return None if a is None else min(max(m * a * 100.0, lo), hi)


def trade(S, i, side, mode, h=H):
    """(neto prinos %, ishod) gde je ishod 'stop' | 'cilj' | 'vreme'; None ako nema podataka."""
    if mode == "fiksno":
        r = sim.fixed_return(S, i, side, h)
        return None if r is None else (r, "vreme")
    sp = stop_for(S, i, mode)
    if sp is None:
        return None
    r = sim.stop_return(S, i, side, sp, h, tp_mult=MODES[mode][3])
    if r is None:
        return None
    if abs(r - (-sp - sim.COST_PCT)) < 1e-9:
        return r, "stop"
    if abs(r - (sp * MODES[mode][3] - sim.COST_PCT)) < 1e-9:
        return r, "cilj"
    return r, "vreme"


def excursion(S, i, side, h=H):
    """(MAE %, MFE %) od ulaza na zatvaranju svece i do h svece unapred; MAE je nepovoljno pomeranje (pozitivan broj)."""
    if i + h >= S.n:
        return None
    e = S.c[i]
    hi = max(S.h[i + 1:i + h + 1])
    lo = min(S.l[i + 1:i + h + 1])
    if side == "long":
        return (e - lo) / e * 100.0, (hi - e) / e * 100.0
    return (hi - e) / e * 100.0, (e - lo) / e * 100.0


def study_rule(series, ctx, vid, fam, params, group=None, warm=210):
    sigs = [s for s in backtest.collect_signals(series, ctx, fam, params, warm) if group is None or series[s[0]].group == group]
    sigs = stats.thin(sigs, H)
    if not sigs:
        return None
    t_min = min(series[s].t[warm] for s in series)
    t_max = max(series[s].t[-1] for s in series)
    out = {"id": vid, "n_signals": len(sigs), "modes": {}}
    for mode in MODES:
        rows, kinds = [], {"stop": 0, "cilj": 0, "vreme": 0}
        for sym, i, t, side in sigs:
            x = trade(series[sym], i, side, mode)
            if x is None:
                continue
            rows.append((t, x[0], sym))
            kinds[x[1]] += 1
        s = stats.summarize(rows, t_min, t_max)
        n = max(len(rows), 1)
        out["modes"][mode] = {"n": s.get("n", 0), "mean": s.get("mean"), "t": (s.get("all") or {}).get("t"),
                              "stop_pct_share": round(100.0 * kinds["stop"] / n, 1), "tp_pct_share": round(100.0 * kinds["cilj"] / n, 1)}
    ex = [e for e in (excursion(series[s], i, side) for s, i, _, side in sigs) if e]
    if ex:
        mae = sorted(e[0] for e in ex)
        mfe = sorted(e[1] for e in ex)
        out["mae_p50"], out["mae_p90"] = round(mae[len(mae) // 2], 2), round(mae[int(len(mae) * 0.9)], 2)
        out["mfe_p50"], out["mfe_p90"] = round(mfe[len(mfe) // 2], 2), round(mfe[int(len(mfe) * 0.9)], 2)
        out["live_stop_median_pct"] = round(st.median(x for x in (stop_for(series[s], i, "uzivo") for s, i, _, _ in sigs) if x), 2)
    return out


def to_markdown(res, group):
    L = ["# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=%d dana, grupa %s" % (H, group or "sve"), "",
         "Neto posle troska %.2f%%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%%); 'siri' 4 x ATR (5-20%%). "
         "Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo." % sim.COST_PCT, "",
         "| pravilo | n | " + " | ".join("%s srednje %%, t" % m for m in MODES) + " | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |",
         "|---|---|" + "---|" * len(MODES) + "---|---|---|---|---|"]
    for r in res:
        m = r["modes"]
        L.append("| %s | %d | %s | %s | %s | %s/%s | %s/%s | %s |" % (
            r["id"], r["n_signals"], " | ".join("%s, %s" % (m[k]["mean"], m[k]["t"]) for k in MODES), m["uzivo"]["stop_pct_share"], m["uzivo"]["tp_pct_share"],
            r.get("mae_p50"), r.get("mae_p90"), r.get("mfe_p50"), r.get("mfe_p90"), r.get("live_stop_median_pct")))
    return "\n".join(L) + "\n"


def main():
    out_md = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "calibration", "daily_stops.md")
    group = sys.argv[2] if len(sys.argv) > 2 else "crypto"
    group = None if group == "all" else group
    cfg, _ = backtest.load_config()
    series = backtest.build_series(cfg, 1500, with_funding=False, interval="1d", log=lambda *a: None)
    ctx = backtest.make_ctx(series, (H,))
    variants = {vid: (fam, params) for vid, fam, params in rules.daily_variants()}
    res = []
    for vid in RULES:
        if vid not in variants:
            continue
        r = study_rule(series, ctx, vid, variants[vid][0], variants[vid][1], group)
        if r:
            res.append(r)
    md = to_markdown(res, group)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
