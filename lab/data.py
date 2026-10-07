"""Podaci: Hyperliquid satne sveće i istorija fundinga (javni info API), keš na disku. Samo stdlib."""
import json
import os
import time
import urllib.request

HL = "https://api.hyperliquid.xyz/info"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")


def _post(body, timeout=40, tries=4):
    """POST sa ponavljanjem (429/5xx i prekidi veze) i kratkom pauzom izmedju poziva (javni API ogranicava brzinu)."""
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(HL, json.dumps(body).encode(), {"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.load(r)
            time.sleep(0.25)
            return out
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (k + 1))
    raise last


def fetch_candles(coin, days=200, interval="1h", now_ms=None):
    """Zatvorene sveće (poslednja, nezavršena, se odbacuje). Vraća listu dict-ova sortiranu po vremenu."""
    now_ms = now_ms or int(time.time() * 1000)
    rows = _post({"type": "candleSnapshot", "req": {"coin": coin, "interval": interval,
                                                    "startTime": now_ms - days * 86400000, "endTime": now_ms}})
    out = []
    for r in rows:
        if int(r["T"]) >= now_ms:  # sveca jos traje
            continue
        out.append({"t": int(r["t"]), "o": float(r["o"]), "h": float(r["h"]), "l": float(r["l"]), "c": float(r["c"]),
                    "v": float(r.get("v", 0) or 0)})
    out.sort(key=lambda x: x["t"])
    return out


def fetch_funding(coin, days=200, now_ms=None):
    """Satni fonding {t, rate}; API vraca najviše 500 zapisa po pozivu, pa se ide unapred po prozorima."""
    now_ms = now_ms or int(time.time() * 1000)
    start = now_ms - days * 86400000
    out = {}
    while start < now_ms:
        rows = _post({"type": "fundingHistory", "coin": coin, "startTime": start, "endTime": now_ms})
        if not rows:
            break
        for r in rows:
            out[int(r["time"])] = float(r["fundingRate"])
        last = max(int(r["time"]) for r in rows)
        if last <= start:
            break
        start = last + 1
        if len(rows) < 400:
            break
    return [{"t": t, "rate": v} for t, v in sorted(out.items())]


def cached(kind, coin, days, fetch, max_age_s=3600):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "%s_%s_%d.json" % (kind, coin.replace(":", "_"), days))
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age_s:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    data = fetch(coin, days)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data
