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
                rn, _, turn = ps.basket_netted(members, score, H, k, sign, cost_pct, min_names)
                mn = ps.metrics(rn, t_from)
                results.append({"sharpe_netted": mn.get("sharpe"), "t_netted": mn.get("t"), "turnover_day": round(turn, 3), "feature": f, "sign": sign, "H": H, "tranches": n, "sharpe": m["sharpe"], "t": m["t"], "ann_return_pct": m["ann_return_pct"],
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


def ols(y, X):
    """Obicna regresija sa slobodnim clanom (Gaussova eliminacija, stdlib). Vraca (koeficijenti [alfa, b1..], R2, t_alfa)."""
    n, k = len(y), len(X[0]) + 1
    A = [[1.0] + list(r) for r in X]
    xtx = [[sum(A[r][i] * A[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    xty = [sum(A[r][i] * y[r] for r in range(n)) for i in range(k)]

    def solve(M, v):
        M = [row[:] + [v[i]] for i, row in enumerate(M)]
        for c in range(k):
            p = max(range(c, k), key=lambda r: abs(M[r][c]))
            M[c], M[p] = M[p], M[c]
            for r in range(k):
                if r != c and M[c][c] != 0:
                    f = M[r][c] / M[c][c]
                    M[r] = [a - f * b for a, b in zip(M[r], M[c])]
        return [M[i][k] / M[i][i] for i in range(k)]

    beta = solve(xtx, xty)
    res = [y[r] - sum(A[r][i] * beta[i] for i in range(k)) for r in range(n)]
    ss_res, my = sum(e * e for e in res), sum(y) / n
    ss_tot = sum((v - my) ** 2 for v in y)
    s2 = ss_res / max(n - k, 1)
    # var(alfa) = s2 * (X'X)^-1[0][0]; (X'X)^-1 prvi stub resavamo kao sistem sa jedinicnim vektorom
    inv0 = solve(xtx, [1.0] + [0.0] * (k - 1))[0]
    t_alpha = beta[0] / math.sqrt(s2 * inv0) if s2 * inv0 > 0 else None
    return beta, (1.0 - ss_res / ss_tot) if ss_tot > 0 else None, t_alpha


def control_scores(members):
    """Poznati faktori kao kontrole: realizovana vol 30 d, prinos 30 d i 90 d (sve zadnjih dana do svece i)."""
    rets = [[None] + [m.c[i] / m.c[i - 1] - 1.0 for i in range(1, m.n)] for m in members]

    def vol30(mi, i, t):
        r = rets[mi][i - 29:i + 1] if i >= 30 else None
        return st.pstdev(r) if r else None

    def ret(L):
        return lambda mi, i, t: members[mi].c[i] / members[mi].c[i - L] - 1.0 if i >= L else None

    return {"vol30": vol30, "ret30": ret(30), "ret90": ret(90)}


def confound_check(members, tables, t_from, picks, cost_pct=0.23, k=5, min_names=10, t_to=None):
    """Za izabrane (osobina, znak, H): regresija dnevnih prinosa korpe na korpe kontrolnih faktora (nizak vol, momentum 30 d i 90 d, isto H).
    Vraca alfu (godisnje %), t alfe, R2 i beta prema kontrolama. Ako alfa nestane, osobina je samo poznat faktor pod drugim imenom."""
    ctl = control_scores(members)
    out = []
    for f, sign, H in picks:
        y_rows, _ = ps.basket_series(members, lambda mi, i, t, _f=f: tables[mi][_f][i], H, k, sign, cost_pct, min_names)
        ctl_rows = {}
        for name, fn, s in (("nizak_vol", ctl["vol30"], -1), ("mom30", ctl["ret30"], 1), ("mom90", ctl["ret90"], 1)):
            ctl_rows[name] = dict(ps.basket_series(members, fn, H, k, s, cost_pct, min_names)[0])
        ts = [t for t, _ in y_rows if t >= t_from and (t_to is None or t < t_to) and all(t in d for d in ctl_rows.values())]
        if len(ts) < 100:
            continue
        ymap = dict(y_rows)
        y = [ymap[t] for t in ts]
        X = [[ctl_rows[n][t] for n in ("nizak_vol", "mom30", "mom90")] for t in ts]
        beta, r2, ta = ols(y, X)
        out.append({"feature": f, "sign": sign, "H": H, "alpha_ann_pct": round(beta[0] * 365, 2), "t_alpha": None if ta is None else round(ta, 2),
                    "r2": None if r2 is None else round(r2, 3), "beta": dict(zip(("nizak_vol", "mom30", "mom90"), (round(b, 3) for b in beta[1:]))), "days": len(ts)})
    return out


def to_markdown(res, top=20):
    L = ["# Studija derivatskih osobina (Binance javni arhiv), dnevne svece, kripto grupa", "",
         "Generisano %s. Instrumenata: %d, od %s, trosak po krugu %.2f%%, k=%d, testova (unapred zadat skup): %d, BH-FDR 10%% preko celog skupa." % (
             res["generated_utc"], res["members"], res["t_from"], res["cost_pct"], res["k"], res["tests"]), "",
         "Placebo (nasumican poredak, 20 zrna): " + "; ".join("H%d srednji Sharpe %.2f, sd %.2f, max %.2f" % (h, p["mean"], p["sd"], p["max"])
                                                              for h, p in sorted(res["placebo_sharpe"].items()) if p), "",
         "Sharpe i t su po tranšima (svaki se otvara i zatvara za sebe, konzervativno); 'prebijanje' = jedna pozicija po simbolu, trosak samo na promenu tezine (kako bi stvarno islo na berzi).", "",
         "| osobina | znak (+ dugo visoko, - kontra) | H | Sharpe | t | Sharpe prebijanje, t | promet dnevno | god. prinos % | pad % | Sharpe po godinama | Sharpe uz stvarni taker | z prema placebu | FDR |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["results"][:top]:
        L.append("| %s | %+d | %d | %.2f | %.2f | %s, %s | %s | %.1f | %.1f | %s | %s | %s | %s |" % (
            r["feature"], r["sign"], r["H"], r["sharpe"], r["t"], r.get("sharpe_netted"), r.get("t_netted"), r.get("turnover_day"), r["ann_return_pct"], r["max_dd_pct"],
            {y: v["sharpe"] for y, v in r["by_year"].items()}, r["sharpe_taker_cost"], r["z_vs_placebo"], "da" if r["fdr_pass"] else "ne"))
    n_pos = sum(1 for r in res["results"] if (r["t"] or 0) > 0)
    L += ["", "Pozitivan t u %d od %d testova (znaci su ogledalo, pa se oko polovine ocekuje i bez prednosti); prolaze FDR: %d." % (
        n_pos, res["tests"], sum(1 for r in res["results"] if r["fdr_pass"]))]
    if res.get("confound"):
        L += ["", "## Da li je to samo poznat faktor? Regresija korpe na kontrole (nizak vol 30 d, momentum 30 d i 90 d, isto H, isti trosak)", "",
              "| osobina | znak | H | alfa god. % | t alfe | R2 | beta nizak_vol / mom30 / mom90 | dana |", "|---|---|---|---|---|---|---|---|"]
        for c in res["confound"]:
            b = c["beta"]
            L.append("| %s | %+d | %d | %.1f | %s | %s | %s / %s / %s | %d |" % (c["feature"], c["sign"], c["H"], c["alpha_ann_pct"], c["t_alpha"], c["r2"],
                                                                           b["nizak_vol"], b["mom30"], b["mom90"], c["days"]))
        L.append("")
        L.append("Placebo napomena: nasumican poredak placa isti trosak po tranšu, pa mu je Sharpe jako negativan (trosak, ne prednost); poredi se samo neto Sharpe i t, "
                 "a 'z prema placebu' pokazuje koliko osobina gubi manje od slucajnosti, ne da zaradjuje. Simulacija ne prebija iste pozicije izmedju tranša, pa precenjuje trosak "
                 "sporo promenljivih osobina.")
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


def iso_ms(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def replicate(members, tables, hyp, min_names=10):
    """Ponavljanje unapred zapisane hipoteze na uzorku koji nije koriscen za nalaz; kriterijumi dolaze iz zapisa, ne iz koda."""
    a, b = hyp["replication_sample"].split("..")
    t_from, t_to = iso_ms(a), iso_ms(b) + 86400000
    f, sign, H, k = hyp["feature"], hyp["sign"], hyp["H"], hyp.get("k", 5)
    score = lambda mi, i, t: tables[mi][f][i]  # noqa: E731
    rows, n = ps.basket_series(members, score, H, k, sign, hyp["cost_pct"], min_names)
    m = ps.metrics(rows, t_from, t_to)
    m_taker = ps.metrics(ps.basket_series(members, score, H, k, sign, 0.10, min_names)[0], t_from, t_to)
    nr, _, turn = ps.basket_netted(members, score, H, k, sign, hyp["cost_pct"], min_names)
    m_net = ps.metrics(nr, t_from, t_to)
    m_net10 = ps.metrics(ps.basket_netted(members, score, H, k, sign, 0.10, min_names)[0], t_from, t_to)
    conf = confound_check(members, tables, t_from, [(f, sign, H)], hyp["cost_pct"], k, min_names, t_to)
    pas = hyp["pass"]
    sharpe, t = m.get("sharpe"), m.get("t")
    alpha = conf[0]["alpha_ann_pct"] if conf else None
    checks = {"net_sharpe": sharpe is not None and sharpe >= pas["net_sharpe_min"], "net_t": t is not None and t >= pas["net_t_min"],
              "alpha_positive": (alpha is not None and alpha > 0) if pas.get("alpha_after_controls_positive") else True}
    return {"id": hyp["id"], "sample": hyp["replication_sample"], "n_days": m.get("n_days"), "net_sharpe": sharpe, "net_t": t, "ann_return_pct": m.get("ann_return_pct"),
            "max_dd_pct": m.get("max_dd_pct"), "sharpe_taker_cost": m_taker.get("sharpe"), "by_year": m.get("by_year"), "confound": conf,
            "netted": {"sharpe": m_net.get("sharpe"), "t": m_net.get("t"), "sharpe_taker_cost": m_net10.get("sharpe"), "turnover_day": round(turn, 3)},
            "members_active": len({s.sym for s, tb in zip(members, tables) if any(x is not None for x in tb[f])}), "checks": checks,
            "passed": all(checks.values())}


def replicate_main():
    with open(os.path.join(ROOT, "config", "preregistered_hypotheses.json"), encoding="utf-8") as fh:
        hyps = json.load(fh)["hypotheses"]
    series, bn, _ = load_inputs()
    members, tables = build_members(series, bn)
    out = [replicate(members, tables, h) for h in hyps]
    md = ["# Ponavljanje unapred zapisanih hipoteza (config/preregistered_hypotheses.json)", ""]
    for r in out:
        md += ["## %s na uzorku %s" % (r["id"], r["sample"]), "",
               "Neto Sharpe %s (uz stvarni taker %s), t %s, godisnji prinos %s%%, najveci pad %s%%, dana %s, aktivnih instrumenata %s." % (
                   r["net_sharpe"], r["sharpe_taker_cost"], r["net_t"], r["ann_return_pct"], r["max_dd_pct"], r["n_days"], r["members_active"]),
               "Po godinama: %s" % ({y: v["sharpe"] for y, v in (r["by_year"] or {}).items()}),
               "Dopuna (nije kriterijum): uz prebijanje pozicija neto Sharpe %s, t %s (uz stvarni taker %s), dnevni promet %s kapitala." % (
                   r["netted"]["sharpe"], r["netted"]["t"], r["netted"]["sharpe_taker_cost"], r["netted"]["turnover_day"]),
               "Posle kontrola (nizak vol, momentum 30 d i 90 d): %s" % (r["confound"][0] if r["confound"] else "nema dovoljno dana"),
               "Kriterijumi (zapisani unapred): %s. **Ishod: %s.**" % (r["checks"], "PROSLO" if r["passed"] else "NIJE PROSLO"), ""]
    text = "\n".join(md)
    with open(os.path.join(ROOT, "calibration", "replication.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "calibration", "replication.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 0


def main():
    if sys.argv[1:2] == ["replicate"]:
        return replicate_main()
    out_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "calibration", "deriv_study.json")
    out_md = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "calibration", "deriv_study.md")
    series, bn, t_from = load_inputs()
    members, tables = build_members(series, bn)
    print("instrumenata sa derivatskim podacima: %d" % len(members))
    res = run_study(members, tables, t_from)
    picks = [(r["feature"], r["sign"], r["H"]) for r in res["results"][:6]]
    res["confound"] = confound_check(members, tables, t_from, picks)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res))
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
