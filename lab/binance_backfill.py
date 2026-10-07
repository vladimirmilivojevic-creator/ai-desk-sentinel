"""Istorija derivatskih podataka sa Binance javnog arhiva (data.binance.vision, CloudFront, bez kljuca i bez API-ja):
dnevni 'metrics' fajlovi (5-min otvoreni interes, odnos dugih/kratkih top trgovaca, globalni odnos, taker odnos) svedeni na dnevne osobine
po UTC danu. Osobina za dan D koristi samo trake do 23:55 tog dana, pa je poznata pre ulaza na zatvaranju dana D (bez gledanja unapred).
Cuva se u lab/cache/binance/<SIMBOL>.json (van gita). Upotreba: python -m lab.binance_backfill [od=2024-12-01] [do=juce] [radnika=12]"""
import csv
import datetime as dt
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "binance")
URL = "https://data.binance.vision/data/futures/um/daily/metrics/%s/%s-metrics-%s.zip"
UA = "ai-desk-sentinel/0.3 (public research, read-only)"
FIELDS = ("oi_val", "oi_val_open", "oi_amt", "top_acc_ls", "top_pos_ls", "glob_ls", "taker")


def bn_symbol(sym):
    """HL naziv -> Binance perp (k-prefiks na HL znaci 1000x token); xyz: instrumenti nemaju Binance perp."""
    if sym.startswith("xyz:") or ":" in sym:
        return None
    if len(sym) > 1 and sym[0] == "k" and sym[1:].isupper():
        return "1000%sUSDT" % sym[1:]
    return "%sUSDT" % sym


def parse_metrics(text):
    """CSV tekst jednog dana -> dnevne osobine (poslednja traka dana za nivoe, srednje za taker odnos); None ako nema trake."""
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        return None
    rows.sort(key=lambda r: r["create_time"])

    def num(r, k):
        try:
            return float(r[k])
        except (KeyError, TypeError, ValueError):
            return None

    last, first = rows[-1], rows[0]
    takers = [x for x in (num(r, "sum_taker_long_short_vol_ratio") for r in rows) if x is not None]
    out = {"oi_val": num(last, "sum_open_interest_value"), "oi_val_open": num(first, "sum_open_interest_value"),
           "oi_amt": num(last, "sum_open_interest"),
           "top_acc_ls": num(last, "count_toptrader_long_short_ratio"), "top_pos_ls": num(last, "sum_toptrader_long_short_ratio"),
           "glob_ls": num(last, "count_long_short_ratio"), "taker": sum(takers) / len(takers) if takers else None, "bars": len(rows)}
    return out if out["oi_val"] else None


def fetch_day(symbol, day, timeout=25, tries=3):
    """Vraca (status, feats): 'ok' | 'missing' (404: simbola tada nije bilo / jos nije objavljeno) | 'error'."""
    url = URL % (symbol, symbol, day)
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(2_000_000)
            z = zipfile.ZipFile(io.BytesIO(raw))
            return "ok", parse_metrics(z.read(z.namelist()[0]).decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return "missing", None
            time.sleep(1.0 * (k + 1))
        except Exception:  # noqa: BLE001
            time.sleep(1.0 * (k + 1))
    return "error", None


def load(symbol):
    p = os.path.join(CACHE, symbol + ".json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save(symbol, days):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, symbol + ".json"), "w", encoding="utf-8") as f:
        json.dump(days, f, separators=(",", ":"), sort_keys=True)


def date_range(start, end):
    a, b = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    return [(a + dt.timedelta(days=i)).isoformat() for i in range((b - a).days + 1)]


def backfill(symbols, start, end, workers=12, fetch=fetch_day, log=print, today=None):
    """Dopunjuje kes. 404 se pamti kao null samo za dane starije od 3 dana (noviji fajl moze samo kasniti). Vraca brojeve."""
    today = today or dt.datetime.now(dt.timezone.utc).date()
    cutoff = (today - dt.timedelta(days=3)).isoformat()
    caches = {s: load(s) for s in symbols}
    jobs = [(s, d) for s in symbols for d in date_range(start, end) if d not in caches[s]]
    stats = {"jobs": len(jobs), "ok": 0, "missing": 0, "error": 0}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for n, ((s, d), (status, feats)) in enumerate(zip(jobs, ex.map(lambda j: fetch(j[0], j[1]), jobs)), start=1):
            if status == "ok" and feats:
                caches[s][d] = feats
                stats["ok"] += 1
            elif status == "missing" or (status == "ok" and not feats):
                if d < cutoff:
                    caches[s][d] = None
                stats["missing"] += 1
            else:
                stats["error"] += 1
            if n % 2000 == 0:
                for sym in symbols:
                    save(sym, caches[sym])
                log("  %d/%d, %.0f s" % (n, len(jobs), time.time() - t0))
    for sym in symbols:
        save(sym, caches[sym])
    return stats


def series(symbol):
    """{datum: osobine} samo za dane koji imaju podatke."""
    return {d: v for d, v in load(symbol).items() if v}


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else "2024-12-01"
    end = sys.argv[2] if len(sys.argv) > 2 else (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)).isoformat()
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    with open(os.path.join(ROOT, "config", "lab_v3.json"), encoding="utf-8") as f:
        uni = json.load(f)["universe"]
    pairs = [(u["sym"], bn_symbol(u["sym"])) for u in uni if u["group"] == "crypto"]
    syms = sorted({b for _, b in pairs if b})
    print("simbola: %d, od %s do %s" % (len(syms), start, end))
    st = backfill(syms, start, end, workers)
    print("gotovo:", st)
    for s in syms:
        n = len(series(s))
        if n < 200:
            print("  malo podataka:", s, n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
