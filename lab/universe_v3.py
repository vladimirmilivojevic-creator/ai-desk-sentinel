"""Gradi prosireni univerzum (laboratorija v3) iz Hyperliquid podataka: likvidnost, spread i starost; klasifikuje grupe i klase.
Samo instrumenti koji postoje na Liquid-u (glavni dex i xyz). Izlaz: config/lab_v3.json (proverljiv artefakt, ponovo se pravi po potrebi).
Upotreba: python -m lab.universe_v3 [min_vol=2e6] [min_oi=10e6] [max_spread_bps=5] [min_age_days=90]"""
import json
import os
import sys
import time

from . import collectors as C, data

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OIL = {"xyz:BRENTOIL", "xyz:CL", "xyz:OIL"}
GAS = {"xyz:NATGAS", "xyz:GAS", "xyz:TTF"}
METALS = {"xyz:GOLD", "xyz:SILVER", "xyz:PLATINUM", "xyz:PALLADIUM", "xyz:COPPER", "xyz:ALUMINIUM", "xyz:URANIUM"}


def classify(sym, category):
    """(grupa, klasa) za pravila i granice stopa; None = ne ulazi u univerzum."""
    if not sym.startswith("xyz:"):
        return ("crypto", "crypto")
    cat = (category or "").lower()
    if cat in ("stocks", "stock"):
        return ("stock", "stock")
    if cat == "indices":
        return ("macro", "index")
    if cat == "commodities":
        if sym in OIL:
            return ("macro", "oil")
        if sym in GAS:
            return ("macro", "gas")
        return ("macro", "metal")
    return None  # preipo, fx, rates: preskacemo u v3


def build(min_vol=2e6, min_oi=10e6, max_spread_bps=5.0, min_age_days=90, log=print):
    ctx = C.hl_contexts()
    cats = {c[0]: c[1] for c in C.hl_post({"type": "perpCategories"})}
    liquid = C.liquid_universe(ctx, min_vol, min_oi)
    rows = []
    for r in liquid:
        sym = r["sym"]
        cls = classify(sym, cats.get(sym))
        if cls is None:
            continue
        try:
            book = C.book_metrics(C.hl_post({"type": "l2Book", "coin": sym}))
        except Exception:  # noqa: BLE001
            book = None
        if not book or book["spread_bps"] > max_spread_bps:
            log("odbijen (spread/knjiga): %s" % sym)
            continue
        try:
            daily = data.fetch_candles(sym, min_age_days + 30, interval="1d")
        except Exception:  # noqa: BLE001
            daily = []
        if len(daily) < min_age_days:
            log("odbijen (premlad ili bez istorije): %s (%d dana)" % (sym, len(daily)))
            continue
        rows.append({"sym": sym, "hl": sym, "group": cls[0], "cls": cls[1], "vol24": r["vol24"], "oi_usd": r["oi_usd"], "spread_bps": book["spread_bps"],
                     "slip120_bps": (book["slip_buy_bps"] or {}).get("120"), "age_days": len(daily)})
    return {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "filters": {"min_vol": min_vol, "min_oi": min_oi,
            "max_spread_bps": max_spread_bps, "min_age_days": min_age_days}, "days": 200, "universe": rows}


def main():
    a = [float(x) for x in sys.argv[1:5]]
    kw = dict(zip(("min_vol", "min_oi", "max_spread_bps", "min_age_days"), a))
    if "min_age_days" in kw:
        kw["min_age_days"] = int(kw["min_age_days"])
    cfg = build(**kw)
    out = os.path.join(ROOT, "config", "lab_v3.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print("univerzum:", len(cfg["universe"]), dict(Counter((u["group"], u["cls"]) for u in cfg["universe"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
