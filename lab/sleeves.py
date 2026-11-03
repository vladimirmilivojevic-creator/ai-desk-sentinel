"""Eksperimenti (senka): vise unapred upisanih varijanti trenda i poretka (config/sleeves.json) koje se prate paralelno unapred od T0,
posle troska i fondinga, istim motorom kao Jezgro (lab/core.py). NE TRGUJE i ne trosi tokene. Pada tiho. Jednom dnevno (posle 00:05 UTC).
Izlaz: <state>/sleeves/sleeves.json. Upotreba: python -m lab.sleeves --state _state"""
import json
import os
import sys
import time

from . import core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_cfg(path=None):
    with open(path or os.path.join(ROOT, "config", "sleeves.json"), encoding="utf-8") as f:
        return json.load(f)


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def compute_all(scfg, base, rows, fund_rows, now_ms):
    """rows/fund_rows: podaci za uniju simbola. Vraca listu sazetaka po varijanti."""
    out = []
    for sl in scfg["sleeves"]:
        syms = [s for s in scfg["universes"][sl["universe"]] if s in rows]
        cfg = dict(base, t0_candle=scfg["t0_candle"], universe=syms, min_names=min(len(syms), 4), lookbacks=sl["lookbacks"], long_only=sl["long_only"],
                   target_vol=sl["target_vol"], mode=sl.get("mode", "trend"), csm_k=sl.get("csm_k", 6))
        row = {"id": sl["id"], "text": sl["text"], "n": len(syms)}
        try:
            fr = {s: fund_rows[s] for s in syms if fund_rows and s in fund_rows} or None
            res = core.compute(cfg, {s: rows[s] for s in syms}, now_ms, None, fr)
        except Exception as e:  # noqa: BLE001
            row["error"] = str(e)[:80]
            out.append(row)
            continue
        if res.get("error"):
            row["error"] = res["error"]
        else:
            sh = res["shadow"]
            row.update({"ret_pct": sh["ret_pct"], "maxdd_pct": sh["maxdd_pct"], "days": sh["days"], "gross": res["gross"], "btc_pct": sh["btc_pct"],
                        "top": sorted(res["weights"].items(), key=lambda kv: -abs(kv[1]))[:4]})
        out.append(row)
    return out


def run(state_dir, now_ms=None, fetch=None, fetch_fund=None, log=print, force=False):
    scfg = load_cfg()
    base = core.load_cfg()
    now_ms = now_ms or int(time.time() * 1000)
    path = os.path.join(state_dir, "sleeves", "sleeves.json")
    prev = _load(path, {})
    yday = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000.0 - 86400))
    if not force and prev.get("last_candle") == yday and prev.get("version") == scfg["version"]:
        return {"skipped": "vec racunato za " + yday}
    if not force and time.gmtime(now_ms / 1000.0).tm_hour == 0 and time.gmtime(now_ms / 1000.0).tm_min < 5:
        return {"skipped": "svece se tek zatvara"}
    union = sorted({s for u in scfg["universes"].values() for s in u})
    cfg = dict(base, universe=union, t0_candle=scfg["t0_candle"])
    rows = core.fetch_rows(cfg, now_ms, fetch, log)
    fund_rows = None
    if fetch_fund is not None or fetch is None:  # sa tudjom funkcijom cena (testovi) mreza za fonding se ne dira
        try:
            fund_rows = core.fetch_fund_rows(cfg, now_ms, fetch_fund, log)
        except Exception as e:  # noqa: BLE001
            log("sleeves: fonding nije dostupan (%s)" % str(e)[:80])
    if not rows:
        return {"error": "nema cena"}
    last = max(d for r in rows.values() for d, _ in r)
    res = compute_all(scfg, base, rows, fund_rows, now_ms)
    out = {"schema": 1, "updated_utc": core.iso(now_ms), "version": scfg["version"], "t0_candle": scfg["t0_candle"], "last_candle": last, "sleeves": res,
           "funding_included": bool(fund_rows)}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(path + ".tmp", path)
    return {"ok": last, "n": len(res)}


def main(argv=None):
    argv = argv or sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        print("sleeves:", json.dumps(run(state, force="--force" in argv), ensure_ascii=False))
    except Exception as e:  # noqa: BLE001
        print("sleeves: greska (ignorisano):", str(e)[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
