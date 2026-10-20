"""Istorijska provera jezgra (lab/core.py): Binance perp dnevne svece (lokalni kes lab/cache/bn_<SIMBOL>USDT.json, 2020-11..), isti kod i ista pravila
kao uzivo, bez ikakvog podesavanja na rezultatima. Poredi sa kupi-i-drzi, daje rezultat po godinama (ukljucuje medvedju 2022), osetljivost na dan
nedeljnog rebalansa, trosak i ciljanu volatilnost, i placebo (nasumicni znak, ista mehanika).
Izlaz: calibration/core_study.md i calibration/core_study.json (referenca koju jezgro prikazuje u panelu).
Upotreba: python -m lab.core_study  (traži lokalni kes; ne radi u Actions-u)"""
import json
import os
import random
import sys
import time

from . import core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
START = "2021-04-01"
PERIODS = [("2021-04..2022-12", START, "2022-12-31"), ("2023..2024", "2023-01-01", "2024-12-31"), ("2025..danas", "2025-01-01", None), ("sve", START, None)]


def load_rows(cfg):
    rows = {}
    for s in cfg["universe"]:
        p = os.path.join(CACHE, "bn_%sUSDT.json" % s)
        with open(p, encoding="utf-8") as f:
            x = json.load(f)
        rows[s] = list(zip(x["d"], x["c"]))
    return rows


def load_funding(cfg):
    """Binance mesecni fonding (lokalni kes lab/cache/carry/fr_<SIMBOL>USDT_<YYYY-MM>.json) kao {sym: [(datum, zbir stopa dana)]}."""
    import glob
    out = {}
    for s in cfg["universe"]:
        pts = []
        for f in sorted(glob.glob(os.path.join(CACHE, "carry", "fr_%sUSDT_*.json" % s))):
            with open(f, encoding="utf-8") as fh:
                pts += [(t, v) for t, v in json.load(fh)]
        if pts:
            out[s] = core.daily_funding(pts)
    return out


def _row(name, dates, rets):
    cells = []
    for _, a, b in PERIODS:
        m = core.metrics(dates, rets, a, b)
        cells.append("Sharpe %s, god. %s%%, pad %s%%" % (m.get("sharpe"), m.get("ann_pct"), m.get("maxdd_pct")) if m.get("sharpe") is not None else "n/a")
    return "| %s | %s |" % (name, " | ".join(cells))


def study(cfg=None, rows=None, log=print):
    cfg = cfg or core.load_cfg()
    rows = rows or load_rows(cfg)
    dates, px = core.build_matrix(rows)
    fund = core.align_funding(dates, load_funding(cfg))
    i0 = next(i for i, d in enumerate(dates) if d >= START)
    d_ = dates[i0:]
    sl = lambda x: x[i0:]  # noqa: E731
    base = core.ensemble(px, dates, cfg, fund=fund)
    nofund = core.ensemble(px, dates, cfg)
    res = {"universe": sorted(px), "from": d_[0], "to": d_[-1], "variants": {}}
    lines = []
    lines.append("| varijanta | " + " | ".join(p[0] for p in PERIODS) + " |")
    lines.append("|---|" + "---|" * len(PERIODS))
    # kupi-i-drzi (jednako ponderisano, dnevno prebalansirano, bez troska: u korist poredjenja) i BTC
    r_all = core._returns(px, len(dates))
    ew = [sum(v for v in (r_all[s][i] for s in px) if v is not None) / max(1, sum(1 for s in px if r_all[s][i] is not None)) if i else 0.0 for i in range(len(dates))]
    btc = [r_all["BTC"][i] or 0.0 for i in range(len(dates))]
    lines.append(_row("kupi-i-drzi, jednako (bez troska)", d_, sl(ew)))
    lines.append(_row("BTC kupi-i-drzi", d_, sl(btc)))
    lines.append(_row("JEZGRO (ansambl 14/28/56/112, samo dugo, vol 20%, UZ FONDING)", d_, sl(base["net"])))
    lines.append(_row("  isto BEZ fondinga (kako je prvo racunato)", d_, sl(nofund["net"])))
    for L, run in zip(cfg["lookbacks"], base["runs"]):
        lines.append(_row("  samo horizont L%d" % L, d_, sl(run["net"])))
    ls = core.ensemble(px, dates, cfg, long_only=False, fund=fund)
    lines.append(_row("ansambl dugo/kratko (isto)", d_, sl(ls["net"])))
    hi = core.ensemble(px, dates, cfg, cost=0.002, fund=fund)
    lines.append(_row("JEZGRO uz trosak 0,20% po strani", d_, sl(hi["net"])))
    for tv in (0.12, 0.35):
        c2 = dict(cfg, target_vol=tv)
        e2 = core.ensemble(px, dates, c2, fund=fund)
        lines.append(_row("JEZGRO ciljana vol %d%%" % round(tv * 100), d_, sl(e2["net"])))
    offs = []
    for wd in range(7):
        c3 = dict(cfg, rebalance_candle_weekday=wd)
        e3 = core.ensemble(px, dates, c3, fund=fund)
        offs.append(core.metrics(d_, sl(e3["net"]), START, None).get("sharpe"))
    res["weekday_offsets_sharpe_full"] = offs
    # placebo
    pl, plp = [], {p[0]: [] for p in PERIODS}
    for k in range(60):
        e4 = core.ensemble(px, dates, cfg, rng=random.Random(1000 + k), fund=fund)
        pl.append(core.metrics(d_, sl(e4["net"]), START, None).get("sharpe"))
        for nm, a, b in PERIODS:
            plp[nm].append(core.metrics(d_, sl(e4["net"]), a, b))
    pl = [x for x in pl if x is not None]
    pm = sum(pl) / len(pl)
    psd = (sum((x - pm) ** 2 for x in pl) / (len(pl) - 1)) ** 0.5
    res["placebo_sharpe_mean"], res["placebo_sharpe_sd"] = round(pm, 2), round(psd, 2)
    res["placebo_periods"] = {nm: {"sharpe": round(sum(m["sharpe"] for m in v) / len(v), 2), "ann_pct": round(sum(m["ann_pct"] for m in v) / len(v), 1),
                                   "maxdd_pct": round(sum(m["maxdd_pct"] for m in v) / len(v), 1)} for nm, v in plp.items()}
    lines.append("| placebo (nasumican znak, prosek 60, ISTA mehanika) | " + " | ".join(
        "Sharpe %s, god. %s%%, pad %s%%" % (res["placebo_periods"][p[0]]["sharpe"], res["placebo_periods"][p[0]]["ann_pct"], res["placebo_periods"][p[0]]["maxdd_pct"]) for p in PERIODS) + " |")
    yearly = core.yearly(d_, sl(base["net"]))
    res["yearly_pct"] = yearly
    res["yearly_buyhold_pct"] = core.yearly(d_, sl(ew))
    res["yearly_btc_pct"] = core.yearly(d_, sl(btc))
    res["full"] = core.metrics(d_, sl(base["net"]), START, None)
    res["full_no_funding"] = core.metrics(d_, sl(nofund["net"]), START, None)
    res["yearly_no_funding_pct"] = core.yearly(d_, sl(nofund["net"]))
    res["buyhold_full"] = core.metrics(d_, sl(ew), START, None)
    res["periods"] = {p[0]: core.metrics(d_, sl(base["net"]), p[1], p[2]) for p in PERIODS}
    # mesecni
    byM = {}
    for d, x in zip(d_, sl(base["net"])):
        byM[d[:7]] = byM.get(d[:7], 1.0) * (1.0 + x)
    mv = [(v - 1.0) * 100 for v in byM.values()]
    res["months"] = {"n": len(mv), "positive": sum(1 for v in mv if v > 0), "worst_pct": round(min(mv), 1), "best_pct": round(max(mv), 1), "median_pct": round(sorted(mv)[len(mv) // 2], 2)}
    res["table_md"] = "\n".join(lines)
    return res


def pit_study(cfg, start="2021-06-01", log=print):
    """POSTENIJI TEST: univerzum kakav je bio tog dana (top N po prosecnom dolarskom prometu 30 d, ukljucuje 101 ugasenu kovanicu, bar 120 dana istorije),
    isti motor, uz fonding. Prvi test (12 najvecih i najstarijih) je gornja granica jer su te kovanice preziveli do danas."""
    import glob
    rows, vol_rows, fund_rows = {}, {}, {}
    for f in glob.glob(os.path.join(CACHE, "bn_*USDT.json")):
        sym = os.path.basename(f)[3:-9]
        with open(f, encoding="utf-8") as fh:
            x = json.load(fh)
        rows[sym] = list(zip(x["d"], x["c"]))
        vol_rows[sym] = dict(zip(x["d"], x["v"]))
    for sym in rows:
        pts = []
        for f in glob.glob(os.path.join(CACHE, "carry", "fr_%sUSDT_*.json" % sym)):
            with open(f, encoding="utf-8") as fh:
                pts += [(t, v) for t, v in json.load(fh)]
        if pts:
            fund_rows[sym] = core.daily_funding(pts)
    dates, px = core.build_matrix(rows)
    n, pos = len(dates), {d: i for i, d in enumerate(dates)}
    vols = {}
    for s in px:
        col = [None] * n
        for d, v in vol_rows[s].items():
            if d in pos and v is not None:
                col[pos[d]] = float(v)
        vols[s] = col
    fund = core.align_funding(dates, fund_rows)
    c2 = dict(cfg, min_names=8, csm_k=6, ann_days=365)
    i0 = next(i for i, d in enumerate(dates) if d >= start)
    d_ = dates[i0:]
    out = {"from": d_[0], "to": d_[-1], "n_coins": len(px), "n_delisted": sum(1 for s in px if next((x for x in reversed(px[s]) if x is not None), None) is not None and px[s][-1] is None), "variants": {}}

    def put(key, label, net):
        m = core.metrics(d_, net[i0:], None, None, 365)
        out["variants"][key] = {"label": label, "full": m, "since_2025": core.metrics(d_, net[i0:], "2025-01-01", None, 365), "yearly": core.yearly(d_, net[i0:])}
        log("pit %-34s Sharpe %s god %s%% pad %s%%" % (label, m.get("sharpe"), m.get("ann_pct"), m.get("maxdd_pct")))
        return net
    res = {}
    for N in (12, 30):
        elig = core.pit_eligibility(dates, px, vols, N)
        res["trend%d" % N] = put("trend%d" % N, "trend dugo, top-%d po prometu" % N, core.ensemble(px, dates, c2, fund=fund, elig=elig)["net"])
        if N == 30:
            res["csm"] = put("csm", "poredak neutralno (L7/14/28), top-30", core.ensemble(px, dates, c2, fund=fund, elig=elig, mode="csm", lookbacks=[7, 14, 28])["net"])
            put("trend_ls30", "trend dugo/kratko, top-30", core.ensemble(px, dates, c2, fund=fund, elig=elig, long_only=False)["net"])
    put("combo", "kombinacija 50/50 trend12 + poredak", [0.5 * a + 0.5 * b for a, b in zip(res["trend12"], res["csm"])])
    rowsb, fr = {}, {}
    for names, key, lab in ((["BTC"], "btc", "trend samo BTC"), (["BTC", "ETH"], "btc_eth", "trend BTC+ETH")):
        rb = {s: rows[s] for s in names}
        db, pb = core.build_matrix(rb)
        fb = core.align_funding(db, {s: fund_rows[s] for s in names})
        e = core.ensemble(pb, db, dict(cfg, min_names=len(names), ann_days=365), fund=fb)
        ib = next(i for i, d in enumerate(db) if d >= start)
        m = core.metrics(db[ib:], e["net"][ib:], None, None, 365)
        out["variants"][key] = {"label": lab, "full": m, "since_2025": core.metrics(db[ib:], e["net"][ib:], "2025-01-01", None, 365), "yearly": core.yearly(db[ib:], e["net"][ib:])}
    r_btc = core._returns({"BTC": px["BTC"]}, n)["BTC"]
    bh = [(r_btc[i] or 0.0) - (fund["BTC"][i] or 0.0) for i in range(n)]
    out["variants"]["btc_hold"] = {"label": "BTC kupi-i-drzi (uz fonding)", "full": core.metrics(d_, bh[i0:], None, None, 365), "yearly": core.yearly(d_, bh[i0:])}
    return out


def to_markdown(res, cfg):
    y, yb, yq = res["yearly_pct"], res["yearly_buyhold_pct"], res["yearly_btc_pct"]
    ys = sorted(y)
    md = ["# Jezgro: istorijska provera (trend-ansambl na velikim kovanicama)", "",
          "Generisano %s, `python -m lab.core_study`. Pravila su upisana unapred u `config/core.json` (verzija %d) i nisu podesavana na ovim rezultatima. "
          "Podaci: Binance perp dnevne svece %s..%s, %d kovanica (%s). Trosak %.3f%% po strani (kao paper simulacija), signal na zatvaranju, prinos od sledeceg dana." % (
              time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), cfg["version"], res["from"], res["to"], len(res["universe"]), ", ".join(res["universe"]), cfg["cost_per_side_pct"]),
          "", "## Ukratko", "",
          "- Ceo period (%s..%s): Sharpe %s, prosecno %s%% godisnje pri volatilnosti %s%%, najveci pad %s%%. Kupi-i-drzi iste kovanice: Sharpe %s, pad %s%%." % (
              res["from"], res["to"], res["full"]["sharpe"], res["full"]["ann_pct"], res["full"]["vol_pct"], res["full"]["maxdd_pct"], res["buyhold_full"]["sharpe"], res["buyhold_full"]["maxdd_pct"]),
          "- Placebo (nasumican znak umesto trenda, ista mehanika, 60 ponavljanja): Sharpe u proseku %s (sd %s). Placebo je samo-dugo sa oko pola vremena u poziciji, pa nosi isti kripto rast: ZASLUGA TRENDA JE RAZLIKA prema placebu, ne ceo rezultat." % (res["placebo_sharpe_mean"], res["placebo_sharpe_sd"]),
          "- Mesecno: pozitivno %d od %d meseci, najgori %s%%, najbolji %s%%, medijana %s%%." % (res["months"]["positive"], res["months"]["n"], res["months"]["worst_pct"], res["months"]["best_pct"], res["months"]["median_pct"]),
          "- Dan nedeljnog rebalansa menja ishod (Sharpe po danima nedelje, ceo period): %s." % res["weekday_offsets_sharpe_full"],
          "", "## Rezultat po godinama (neto %, jezgro / kupi-i-drzi / BTC)", "", "| godina | jezgro | kupi-i-drzi | BTC |", "|---|---|---|---|"]
    for k in ys:
        md.append("| %s | %s | %s | %s |" % (k, y[k], yb.get(k), yq.get(k)))
    pit = res.get("pit")
    pit_md = []
    if pit:
        pit_md = ["", "## Pošteniji test: univerzum kakav je bio tog dana (uključuje ugašene kovanice), uz fonding", "",
                  "Prvi test gore koristi 12 najvećih i najstarijih kovanica koje su preživele do danas, pa je to **gornja granica**. Ovde se u svakom trenutku bira top N po prosečnom dolarskom prometu (30 d) između %d perpetuala sa Binance-a, uključujući ugašene (%s do %s), isti motor, uz fonding i trošak %.3f%% po strani." % (pit["n_coins"], pit["from"], pit["to"], cfg["cost_per_side_pct"]), "",
                  "| varijanta | Sharpe | t | god. % | vol % | najveći pad % | od 2025: Sharpe | po godinama |", "|---|---|---|---|---|---|---|---|"]
        for k, v in pit["variants"].items():
            f = v["full"]
            s25 = (v.get("since_2025") or {}).get("sharpe")
            pit_md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (v["label"], f.get("sharpe"), f.get("t"), f.get("ann_pct"), f.get("vol_pct"), f.get("maxdd_pct"), s25, v.get("yearly")))
        pit_md += ["", "Čitanje: pošteniji test daje Sharpe oko 0,5 (oko 10% godišnje uz pad oko -27%), t oko 1,1, a to se statistički ne razlikuje od nule. Poredak neutralno (market-neutral) je u istom testu oko 0,3 i ne drži dokaz. Jezgro je zato upravljano držanje kripto rizika, ne dokazana prednost."]
    md += ["", "## Po periodima i varijantama", "", res["table_md"], "",
           "## Ograničenja (iskreno)", "",
           "- Istorija je kratka (oko 5 godina) i sadrzi samo dva velika rasta i jedan medved (2022). To je jedan uzorak trzista, ne zakon.",
           "- Kovanice su bile jedne od najvecih 2020-2021 i prezivele su do danas (pristrasnost prezivelih), iako smo namerno uzeli najvece i najstarije. Uzorak 2025..danas je najmanje pristrasan.",
           "- Jezgro je u sustini upravljan nacin drzanja kripto rizika (trend, volatilnost). U padu 2022. je izgubilo, u rastu 2023-24. zaradilo; ne zaradjuje kad trzista nema.",
           "- Nista od ovoga nije dokaz buduce dobiti. Unapred se meri od T0 (`config/core.json`), a odluku o pravom novcu donosi iskljucivo vlasnik."]
    return "\n".join(md) + "\n"


def main(argv=None):
    cfg = core.load_cfg()
    res = study(cfg)
    res["pit"] = pit_study(cfg)
    out_md = os.path.join(ROOT, "calibration", "core_study.md")
    out_js = os.path.join(ROOT, "calibration", "core_study.json")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res, cfg))
    res["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    keep = {k: v for k, v in res.items() if k != "table_md"}
    with open(out_js, "w", encoding="utf-8") as f:
        json.dump(keep, f, ensure_ascii=False, separators=(",", ":"))
    print("upisano", out_md, out_js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
