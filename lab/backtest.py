"""Istorijska provera cele biblioteke pravila na celom svetu instrumenata (config/lab.json).
Ovo proverava DETERMINISTICKA pravila (ne AI): AI model bi 'pamtio' istoriju i rezultat ne bi vredeo.
Upotreba: python -m lab.backtest [izlaz.json] [izlaz.md]
Testovi: 4 po varijanti (fiksni horizont 4 h, 24 h, 72 h i 'izvrsna' varijanta sa stopom 2,5 x ATR, ciljem 2x i vremenskim stopom 24 h).
Statistika: neto posle troska 0,23%, nepreklapajuci uzorci, t po danima, 60/40 podela vremena, Bonferroni za broj testova."""
import json
import os
import sys
import time

from . import data, rules, sim, stats
from .indicators import Series

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HORIZONS = (4, 24, 72)
WARMUP = 210


def load_config():
    with open(os.path.join(ROOT, "config", "lab.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    cand_path = os.path.join(ROOT, "config", "lab_candidates.json")
    cands = []
    if os.path.exists(cand_path):
        with open(cand_path, encoding="utf-8") as f:
            cands = json.load(f).get("candidates", [])
    return cfg, cands


def build_series(cfg, days=None, with_funding=True, log=print, interval="1h"):
    days = days or cfg.get("days", 200)
    out = {}
    warm = WARMUP if interval == "1h" else 210
    for u in cfg["universe"]:
        try:
            cs = data.cached("c" if interval == "1h" else "d", u["hl"], days,
                             lambda coin, d: data.fetch_candles(coin, d, interval=interval))
        except Exception as e:  # noqa: BLE001
            log("preskacem %s: %s" % (u["sym"], type(e).__name__))
            continue
        if len(cs) < warm + (100 if interval == "1h" else 60):
            log("premalo svece za %s (%d)" % (u["sym"], len(cs)))
            continue
        fund = None
        if with_funding:
            try:
                fund = data.cached("f", u["hl"], days, lambda coin, d: data.fetch_funding(coin, d), max_age_s=6 * 3600)
            except Exception as e:  # noqa: BLE001
                log("bez fundinga za %s: %s" % (u["sym"], type(e).__name__))
        out[u["sym"]] = Series(cs, fund, sym=u["sym"], group=u["group"], cls=u["cls"])
    return out


def bench_table(series, horizons):
    """Prosecan unapred prinos korpe (iste grupe) po vremenu i horizontu: {(grupa, H): {t: sredina}}. Sluzi da se ukloni opsti rast
    (npr. kripto bik) i prezivljavanje: pravilo se meri kao PREKO korpe, ne kao sirov prinos."""
    out = {}
    groups = {}
    for S in series.values():
        groups.setdefault(S.group, []).append(S)
    for g, members in groups.items():
        for H in horizons:
            acc = {}
            for S in members:
                for i in range(0, S.n - H):
                    acc.setdefault(S.t[i], []).append(S.c[i + H] / S.c[i] - 1.0)
            out[(g, H)] = {t: sum(v) / len(v) for t, v in acc.items() if len(v) >= 3}
    return out


def make_ctx(series, horizons=HORIZONS):
    ctx = {"csm": rules.csm_context(series), "bench": bench_table(series, tuple(horizons))}
    if "BTC" in series:
        ctx["btc"] = series["BTC"]
        ctx["btc_index"] = {t: i for i, t in enumerate(series["BTC"].t)}
    return ctx


def collect_signals(series, ctx, fam, params, warm=WARMUP):
    fn = rules.FAMILIES[fam]
    sigs = []
    for sym, S in sorted(series.items()):
        for i in range(warm, S.n - 1):
            side = fn(S, i, ctx, **params)
            if side:
                sigs.append((sym, i, S.t[i], side))
    return sigs


def evaluate(series, sigs, horizons=HORIZONS, with_x=True, ctx_bench=None):
    """Vraca {test: lista (t, ret%, sym)} za fiksne horizonte i (opciono) X24."""
    res = {}
    for H in horizons:
        rows = []
        for sym, i, t, side in stats.thin(sigs, H):
            r = sim.fixed_return(series[sym], i, side, H)
            if r is not None:
                rows.append((t, r, sym))
        res["H%d" % H] = rows
        ex = []
        for sym, i, t, side in stats.thin(sigs, H):
            S = series[sym]
            r = sim.fixed_return(S, i, side, H)
            m = (ctx_bench or {}).get((S.group, H), {}).get(t)
            if r is not None and m is not None:
                ex.append((t, r - sim.sign(side) * m * 100.0, sym))  # neto prinos MINUS prinos korpe u istom smeru
        res["E%d" % H] = ex
    if with_x:
        rows = []
        for sym, i, t, side in stats.thin(sigs, 24):
            S = series[sym]
            r = sim.stop_return(S, i, side, sim.stop_pct_for(S, i, S.cls), 24)
            if r is not None:
                rows.append((t, r, sym))
        res["X24"] = rows
    return res


def by_group(series, rows):
    g = {}
    for t, r, sym in rows:
        g.setdefault(series[sym].group, []).append(r)
    return {k: {"n": len(v), "mean": round(sum(v) / len(v), 4)} for k, v in sorted(g.items())}


def run(log=print, days=None, interval="1h"):
    cfg, cands = load_config()
    daily = interval == "1d"
    days = days or (1500 if daily else None)
    series = build_series(cfg, days, log=log, interval=interval, with_funding=not daily)
    ctx = make_ctx(series, (1, 3, 7) if daily else HORIZONS)
    if daily:
        variants, horizons, with_x, warm = rules.daily_variants(), (1, 3, 7), False, 210
        # makro i akcije nemaju dugu istoriju: dnevni testovi koriste sve sto postoji
    else:
        variants, horizons, with_x, warm = rules.default_variants() + rules.candidate_variants(cands), HORIZONS, True, WARMUP
    ref = series.get("BTC") or next(iter(series.values()))
    t_min, t_max = ref.t[warm], ref.t[-1 - max(horizons)]
    k_tests = len(variants) * len(horizons)  # primarni testovi su "E" (preko korpe); ostali su informativni
    results = []
    for vid, fam, params in variants:
        sigs = collect_signals(series, ctx, fam, params, warm)
        ev = evaluate(series, sigs, horizons, with_x, ctx["bench"])
        for test, rows in ev.items():
            s = stats.summarize(rows, t_min, t_max)
            results.append({"id": vid, "family": fam, "params": params, "test": test, "stats": s,
                            "verdict": stats.verdict(s, k_tests) if test.startswith("E") else "info",
                            "groups": by_group(series, rows) if s.get("n", 0) else {}})
        log("%-18s signala %6d" % (vid, len(sigs)))
    return {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "interval": interval, "days": days or cfg.get("days"),
            "instruments": sorted(series), "window_ms": [t_min, t_max], "k_tests": k_tests,
            "bonferroni_z": round(stats.bonferroni_z(k_tests), 2), "cost_pct": sim.COST_PCT, "results": results}


def to_markdown(res):
    L = ["# Laboratorija: istorijska provera pravila", "",
         "Generisano %s. Instrumenata: %d, dana: %s, testova: %d, Bonferroni z = %.2f, trošak po krugu %.2f%%." % (
             res["generated_utc"], len(res["instruments"]), res["days"], res["k_tests"], res["bonferroni_z"], res["cost_pct"]),
         "Neto posle troška, nepreklapajući uzorci, t po danima (korelisani instrumenti se ne broje kao nezavisni), deo za proveru = poslednjih 40% vremena.", "",
         "| pravilo | test | n | srednje % | pobede % | t svi | t prvi deo | t drugi deo | presuda |", "|---|---|---|---|---|---|---|---|---|"]
    rows = [r for r in res["results"] if r["stats"].get("n", 0) >= 30 and r["test"].startswith("E")]
    rows.sort(key=lambda r: -(r["stats"]["all"].get("t") or -99))
    for r in rows[:40]:
        s = r["stats"]
        L.append("| %s | %s | %d | %+.3f | %.0f | %s | %s | %s | %s |" % (
            r["id"], r["test"], s["n"], s["mean"], s["win_pct"], s["all"].get("t"), s["train"].get("t"), s["test"].get("t"), r["verdict"]))
    counts = {}
    for r in res["results"]:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    L += ["", "Presude (ukupno testova %d): %s" % (len(res["results"]), ", ".join("%s %d" % kv for kv in sorted(counts.items())))]
    return "\n".join(L) + "\n"


def main():
    interval = os.environ.get("LAB_INTERVAL", "1h")
    res = run(interval=interval)
    out_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "lab", "backtest_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)
    md = to_markdown(res)
    out_md = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "calibration", "lab_backtest.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
