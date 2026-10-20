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
    i0 = next(i for i, d in enumerate(dates) if d >= START)
    d_ = dates[i0:]
    sl = lambda x: x[i0:]  # noqa: E731
    base = core.ensemble(px, dates, cfg)
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
    lines.append(_row("JEZGRO (ansambl 14/28/56/112, samo dugo, vol 20%)", d_, sl(base["net"])))
    for L, run in zip(cfg["lookbacks"], base["runs"]):
        lines.append(_row("  samo horizont L%d" % L, d_, sl(run["net"])))
    ls = core.ensemble(px, dates, cfg, long_only=False)
    lines.append(_row("ansambl dugo/kratko (isto)", d_, sl(ls["net"])))
    hi = core.ensemble(px, dates, cfg, cost=0.002)
    lines.append(_row("JEZGRO uz trosak 0,20% po strani", d_, sl(hi["net"])))
    for tv in (0.12, 0.35):
        c2 = dict(cfg, target_vol=tv)
        e2 = core.ensemble(px, dates, c2)
        lines.append(_row("JEZGRO ciljana vol %d%%" % round(tv * 100), d_, sl(e2["net"])))
    offs = []
    for wd in range(7):
        c3 = dict(cfg, rebalance_candle_weekday=wd)
        e3 = core.ensemble(px, dates, c3)
        offs.append(core.metrics(d_, sl(e3["net"]), START, None).get("sharpe"))
    res["weekday_offsets_sharpe_full"] = offs
    # placebo
    pl, plp = [], {p[0]: [] for p in PERIODS}
    for k in range(60):
        e4 = core.ensemble(px, dates, cfg, rng=random.Random(1000 + k))
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
    out_md = os.path.join(ROOT, "calibration", "core_study.md")
    out_js = os.path.join(ROOT, "calibration", "core_study.json")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res, cfg))
    keep = {k: v for k, v in res.items() if k != "table_md"}
    with open(out_js, "w", encoding="utf-8") as f:
        json.dump(keep, f, ensure_ascii=False, separators=(",", ":"))
    print("upisano", out_md, out_js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
