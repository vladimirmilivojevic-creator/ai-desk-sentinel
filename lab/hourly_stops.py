"""Satna pravila: da li sirina stopa menja ishod? Uzivo stop je 2,5 x ATR (u granicama klase), a skeptik stalno javlja "stop_too_tight".
Ovde se ista signalna pravila simuliraju sa stopom 1,25 / 2,5 (uzivo) / 4 / 6 x ATR (granice klase se skaliraju istim odnosom), cilj 2 x stop, drzanje 24 h, bez stopa kao
polaznom tackom. Trosak 0,23%. Ulog je kao uzivo: min($120, $4 / stop%), pa se meri i "dolara po trejdu", jer sirji stop znaci manji ulog.
PLACEBO (nasumicni ulazi) je ravnalo: svaki nacin mora da pobedi njega, ne nulu. Samo stdlib.
Upotreba: python -m lab.hourly_stops [izlaz.md] [--fresh]   (koristi lab/cache sveca bez obzira na starost, osim uz --fresh)"""
import os
import statistics as st
import sys

from . import backtest, data, rules, sim, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 24
RULES = ("FADE_L24_z2.5", "FADE_L24_z1.5", "RSIFADE_80", "FADE_L4_z2.5", "MOM_L4_z2.5", "BTCLEAD_z2.0", "PLACEBO_p2")
MODES = {"1.25x": 1.25, "uzivo 2.5x": 2.5, "4x": 4.0, "6x": 6.0}
TICKET_MAX, RISK_USD = 120.0, 4.0


def load_series(fresh=False, days=200):
    """Svece iz lab/cache (bez novog preuzimanja) osim ako je trazeno --fresh."""
    orig = data.cached
    if not fresh:
        data.cached = lambda kind, coin, d, fetch, max_age_s=3600: orig(kind, coin, d, fetch, max_age_s=10 ** 9)
    try:
        cfg, _ = backtest.load_config()
        return backtest.build_series(cfg, days, with_funding=False, log=lambda *a: None)
    finally:
        data.cached = orig


def stop_pct(S, i, m):
    a = S.atr_pct[i]
    if a is None:
        return None
    lo, hi = sim.CLASS_BOUNDS.get(S.cls, (1.2, 3.5))
    k = m / sim.ATR_MULT
    return round(min(max(m * a * 100.0, lo * k), hi * k), 3)


def classify(S, i, side, sp, r):
    if r is None:
        return None
    if abs(r - (-sp - sim.COST_PCT)) < 1e-9:
        return "stop"
    if abs(r - (sp * sim.TP_MULT - sim.COST_PCT)) < 1e-9:
        return "cilj"
    return "vreme"


def study_rule(series, ctx, vid, fam, params):
    sigs = stats.thin(backtest.collect_signals(series, ctx, fam, params, backtest.WARMUP), H)
    if not sigs:
        return None
    t_min = min(series[s].t[backtest.WARMUP] for s in series)
    t_max = max(series[s].t[-1] for s in series)
    out = {"id": vid, "n_signals": len(sigs), "modes": {}}
    modes = {"bez stopa": None}
    modes.update(MODES)
    for name, m in modes.items():
        rows, kinds, dollars = [], {"stop": 0, "cilj": 0, "vreme": 0}, []
        for sym, i, t, side in sigs:
            S = series[sym]
            if m is None:
                r, sp = sim.fixed_return(S, i, side, H), None
                if r is None:
                    continue
                kinds["vreme"] += 1
                ticket = TICKET_MAX
            else:
                sp = stop_pct(S, i, m)
                r = sim.stop_return(S, i, side, sp, H)
                k = classify(S, i, side, sp, r)
                if k is None:
                    continue
                kinds[k] += 1
                ticket = min(TICKET_MAX, RISK_USD / sp * 100.0)
            rows.append((t, r, sym))
            dollars.append(ticket * r / 100.0)
        s = stats.summarize(rows, t_min, t_max)
        n = max(len(rows), 1)
        out["modes"][name] = {"n": s.get("n", 0), "mean": s.get("mean"), "t": (s.get("all") or {}).get("t"), "usd": round(st.mean(dollars), 4) if dollars else None,
                              "stop_share": round(100.0 * kinds["stop"] / n, 1), "tp_share": round(100.0 * kinds["cilj"] / n, 1)}
    return out


def to_markdown(res):
    names = ["bez stopa"] + list(MODES)
    L = ["# Satna pravila: sirina stopa (drzanje 24 h, cilj 2 x stop, neto posle troska %.2f%%)" % sim.COST_PCT, "",
         "Svaka celija: srednji neto prinos %%, t po danima, $ po trejdu (ulog min($120, $4/stop%%)), udeo stop/cilj %%. PLACEBO je ravnalo (nasumicni ulazi). "
         "Sirovi t nije korigovan za broj celija (%d pravila x %d nacina)." % (len(res), len(names)), "",
         "| pravilo | n | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for r in res:
        cells = []
        for n in names:
            m = r["modes"][n]
            cells.append("%s %%, t %s, $%s, st %s/ci %s" % (m["mean"], m["t"], m["usd"], m["stop_share"], m["tp_share"]))
        L.append("| %s | %d | %s |" % (r["id"], r["n_signals"], " | ".join(cells)))
    return "\n".join(L) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_md = args[0] if args else os.path.join(ROOT, "calibration", "hourly_stops.md")
    series = load_series(fresh="--fresh" in sys.argv)
    ctx = backtest.make_ctx(series, (H,))
    variants = {vid: (fam, params) for vid, fam, params in rules.default_variants()}
    res = []
    for vid in RULES:
        if vid in variants:
            r = study_rule(series, ctx, vid, *variants[vid])
            if r:
                res.append(r)
    md = to_markdown(res)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
