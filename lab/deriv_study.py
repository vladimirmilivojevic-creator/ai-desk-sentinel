"""Studija derivatskih osobina (Binance javni arhiv: otvoreni interes, odnos dugih/kratkih, taker odnos) kao signala za poredak unutar
kripto grupe, na dnevnim svecama. Isti nacin merenja kao portfolio_sim: dugo/kratko korpa, tranše po danu, trosak po krugu, Sharpe i t.
Skup hipoteza je UNAPRED zadat (FEATURES x znak x H), korekcija BH-FDR preko celog skupa, a nasumicni poredak (placebo) daje empirijsku
raspodelu Sharpe-a pod 'nema prednosti'. Samo stdlib. Upotreba: python -m lab.deriv_study [izlaz.json] [izlaz.md]"""
import datetime as dt
import hashlib
import json
import math
import os
import statistics as st
import sys
import time

from . import backtest, binance_backfill as bb, portfolio_sim as ps, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES = ("oi_chg_3", "oi_chg_7", "top_pos_ls", "top_acc_ls", "glob_ls", "taker_z", "top_pos_ls_z", "glob_ls_z", "smart_div")
HOLDS = (1, 3, 7)
SIGNS = (1, -1)
Z_WIN = 30


def day_of(t_ms):
    return dt.datetime.fromtimestamp(t_ms / 1000, dt.timezone.utc).date().isoformat()


def _z(vals, i, win=Z_WIN, min_obs=20):
    """z-skor vrednosti i u odnosu na prethodnih `win` dana iste serije (bez tekuceg dana)."""
    x = vals[i]
    if x is None:
        return None
    hist = [v for v in vals[max(0, i - win):i] if v is not None]
    if len(hist) < min_obs:
        return None
    sd = st.pstdev(hist)
    return (x - st.mean(hist)) / sd if sd > 0 else None


def feature_table(times, bn):
    """times: UTC svece (ms) instrumenta; bn: {datum: osobine}. Vraca {osobina: lista po indeksu svece (None = nema)}."""
    rows = [bn.get(day_of(t)) for t in times]
    n = len(rows)

    def col(k):
        return [None if r is None else r.get(k) for r in rows]

    amt, tpl, tac, gls, tkr = col("oi_amt"), col("top_pos_ls"), col("top_acc_ls"), col("glob_ls"), col("taker")
    out = {k: [None] * n for k in FEATURES}
    for L, key in ((3, "oi_chg_3"), (7, "oi_chg_7")):
        for i in range(L, n):
            if amt[i] and amt[i - L]:
                out[key][i] = amt[i] / amt[i - L] - 1.0
    out["top_pos_ls"], out["top_acc_ls"], out["glob_ls"] = tpl[:], tac[:], gls[:]
    zt, zg = [None] * n, [None] * n
    for i in range(n):
        out["taker_z"][i] = _z(tkr, i)
        zt[i], zg[i] = _z(tpl, i), _z(gls, i)
    out["top_pos_ls_z"], out["glob_ls_z"] = zt, zg
    out["smart_div"] = [None if a is None or b is None else a - b for a, b in zip(zt, zg)]
    return out


def random_score(seed):
    def f(mi, i, t, _s=seed):
        h = hashlib.md5(("%s:%d:%d" % (_s, mi, t)).encode()).digest()
        return int.from_bytes(h[:6], "big") / float(1 << 48)
    return f


def build_members(series, bn_by_sym, group="crypto", min_days=200):
    """Instrumenti grupe sa dovoljno derivatskih podataka. bn_by_sym: {HL simbol: {datum: osobine}}."""
    members, tables = [], []
    for s in series.values():
        if s.group != group:
            continue
        bn = bn_by_sym.get(s.sym) or {}
        if len(bn) < min_days:
            continue
        members.append(s)
        tables.append(feature_table(s.t, bn))
    return members, tables


def run_study(members, tables, t_from, cost_pct=0.23, k=5, min_names=10, n_placebo=20, log=print):
    results = []
    for f in FEATURES:
        for sign in SIGNS:
            for H in HOLDS:
                score = (lambda mi, i, t, _f=f: tables[mi][_f][i])
                rows, n = ps.basket_series(members, score, H, k, sign, cost_pct, min_names)
                m = ps.metrics(rows, t_from)
                if m.get("n_days", 0) < 100:
                    continue
                m10 = ps.metrics(ps.basket_series(members, score, H, k, sign, 0.10, min_names)[0], t_from)
                results.append({"feature": f, "sign": sign, "H": H, "tranches": n, "sharpe": m["sharpe"], "t": m["t"], "ann_return_pct": m["ann_return_pct"],
                                "max_dd_pct": m["max_dd_pct"], "n_days": m["n_days"], "by_year": m["by_year"], "sharpe_taker_cost": m10.get("sharpe")})
    pv = [((r["feature"], r["sign"], r["H"]), stats.t_to_p(r["t"])) for r in results if r["t"] is not None]
    ok = stats.bh_fdr(pv, 0.10)
    for r in results:
        r["fdr_pass"] = (r["feature"], r["sign"], r["H"]) in ok
    placebo = {}
    for H in HOLDS:
        sh = []
        for seed in range(n_placebo):
            rows, _ = ps.basket_series(members, random_score(seed), H, k, 1, cost_pct, min_names)
            m = ps.metrics(rows, t_from)
            if m.get("sharpe") is not None:
                sh.append(m["sharpe"])
        placebo[H] = {"n": len(sh), "mean": round(st.mean(sh), 3), "sd": round(st.pstdev(sh), 3), "max": round(max(sh), 3)} if sh else None
    for r in results:
        p = placebo.get(r["H"])
        r["z_vs_placebo"] = round((r["sharpe"] - p["mean"]) / p["sd"], 2) if p and p["sd"] else None
    results.sort(key=lambda r: -(r["t"] if r["t"] is not None else -99))
    return {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "members": len(members), "cost_pct": cost_pct, "k": k,
            "tests": len(results), "t_from": day_of(t_from), "placebo_sharpe": placebo, "results": results}


def to_markdown(res, top=20):
    L = ["# Studija derivatskih osobina (Binance javni arhiv), dnevne svece, kripto grupa", "",
         "Generisano %s. Instrumenata: %d, od %s, trosak po krugu %.2f%%, k=%d, testova (unapred zadat skup): %d, BH-FDR 10%% preko celog skupa." % (
             res["generated_utc"], res["members"], res["t_from"], res["cost_pct"], res["k"], res["tests"]), "",
         "Placebo (nasumican poredak, 20 zrna): " + "; ".join("H%d srednji Sharpe %.2f, sd %.2f, max %.2f" % (h, p["mean"], p["sd"], p["max"])
                                                              for h, p in sorted(res["placebo_sharpe"].items()) if p), "",
         "| osobina | znak (+ dugo visoko, - kontra) | H | Sharpe | t | god. prinos % | pad % | Sharpe po godinama | Sharpe uz stvarni taker | z prema placebu | FDR |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["results"][:top]:
        L.append("| %s | %+d | %d | %.2f | %.2f | %.1f | %.1f | %s | %s | %s | %s |" % (
            r["feature"], r["sign"], r["H"], r["sharpe"], r["t"], r["ann_return_pct"], r["max_dd_pct"],
            {y: v["sharpe"] for y, v in r["by_year"].items()}, r["sharpe_taker_cost"], r["z_vs_placebo"], "da" if r["fdr_pass"] else "ne"))
    n_pos = sum(1 for r in res["results"] if (r["t"] or 0) > 0)
    L += ["", "Pozitivan t u %d od %d testova (znaci su ogledalo, pa se oko polovine ocekuje i bez prednosti); prolaze FDR: %d." % (
        n_pos, res["tests"], sum(1 for r in res["results"] if r["fdr_pass"]))]
    return "\n".join(L) + "\n"


def load_inputs(t_start="2025-01-01"):
    cfg, _ = backtest.load_config()
    series = backtest.build_series(cfg, 1500, with_funding=False, interval="1d", log=lambda *a: None)
    bn = {}
    for s in series.values():
        b = bb.bn_symbol(s.sym)
        if b:
            bn[s.sym] = bb.series(b)
    t_from = int(dt.datetime.fromisoformat(t_start).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    return series, bn, t_from


def main():
    out_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "calibration", "deriv_study.json")
    out_md = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "calibration", "deriv_study.md")
    series, bn, t_from = load_inputs()
    members, tables = build_members(series, bn)
    print("instrumenata sa derivatskim podacima: %d" % len(members))
    res = run_study(members, tables, t_from)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res))
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
