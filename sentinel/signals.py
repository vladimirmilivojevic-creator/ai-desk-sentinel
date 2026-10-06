"""Dnevnik signala i ishoda: nacin da desk uci svaki dan i bez trejdova.

Svaki put kad tradable instrument pređe cenovni prag (P okidač), upisuje se signal (najvise jedan po instrumentu na 120 min).
Posle +4 h, +24 h i +72 h racuna se sta bi se desilo da smo PRATILI smer pomaka ("follow") ili ga VRATILI ("fade" = suprotan znak).
Sve je deterministicki kod nad javnim cenama (Hyperliquid sveće), bez AI-ja, pa nema zagadjenja pamcenjem modela.
Agregat (n, prosecan povrat, uspesnost) ide u status/stats.json; zakljucak je dozvoljen tek kad je n >= 10 po grupi.
"""
import statistics

HORIZONS = (4, 24, 72)
COOLDOWN_MIN = 120
MIN_N = 10
KEEP_OPEN_H = 80


def record(psigs, themes, events_by_theme, now, store, vol_ctx=None):
    """Upisuje nove signale u store['open']; vraca listu novih."""
    new = []
    last = store.setdefault("last", {})
    for p in psigs:
        if p.get("stale") or not p.get("trig") or p.get("signal_only") or not p.get("tradable", True):
            continue
        if now - last.get(p["key"], 0) < COOLDOWN_MIN * 60:
            continue
        th = themes.get(p["theme"], {})
        sid = events_by_theme.get(p["theme"]) or "SIG-%d-%s" % (int(now), p["key"])
        sig = {"id": sid, "ts": int(now), "key": p["key"], "theme": p["theme"], "dir": p["dir"], "px": p["px"],
               "m60": p.get("m60"), "m240": p.get("m240"), "rel": round(p.get("rel", 0), 2),
               "confirmed": bool(p.get("confirmed")), "tier": th.get("tier"), "families": sorted(th.get("families", {})),
               "ctx": dict(vol_ctx or {}), "out": {}}
        store.setdefault("open", []).append(sig)
        last[p["key"]] = now
        new.append(sig)
    return new


def _price_at(candles, target):
    """Prva sveca ciji je kraj >= target (kraj u sekundama); None ako je predaleko (> 2 h)."""
    for t_end, close in candles:
        if t_end >= target:
            return close if t_end - target <= 2 * 3600 else None
    return None


def update_outcomes(store, now, fetch_candles, hl_of):
    """fetch_candles(coin, interval, minutes_back) -> [(kraj, close)]. Vraca listu zatvorenih signala ovog kruga."""
    done = []
    keep = []
    cache = {}
    for sig in store.get("open", []):
        age_h = (now - sig["ts"]) / 3600.0
        pending = [h for h in HORIZONS if str(h) not in sig["out"] and age_h >= h]
        if pending:
            coin = hl_of.get(sig["key"])
            if coin:
                if coin not in cache:
                    try:
                        cache[coin] = fetch_candles(coin, "1h", int(age_h * 60) + 180)
                    except Exception:
                        cache[coin] = None
                candles = cache[coin]
                if candles:
                    sgn = 1.0 if sig["dir"] == "up" else -1.0
                    for h in pending:
                        px = _price_at(candles, sig["ts"] + h * 3600)
                        if px is not None and sig["px"]:
                            sig["out"][str(h)] = round((px / sig["px"] - 1.0) * 100.0 * sgn, 3)  # povrat ako PRATIMO
        if all(str(h) in sig["out"] for h in HORIZONS) or age_h > KEEP_OPEN_H:
            done.append(sig)
        else:
            keep.append(sig)
    store["open"] = keep
    if done:
        store.setdefault("closed", []).extend(done)
        store["closed"] = store["closed"][-1000:]
    return done


def stats(store):
    """Agregat po temi i po (tema, potvrdjeno): n, prosek 'follow' povrata po horizontu, udeo pozitivnih."""
    rows = {}
    for sig in store.get("closed", []) + store.get("open", []):
        for grp in (sig["theme"], "%s|%s" % (sig["theme"], "potvrdjeno" if sig["confirmed"] else "nepotvrdjeno"), "SVE"):
            g = rows.setdefault(grp, {h: [] for h in HORIZONS})
            for h in HORIZONS:
                v = sig["out"].get(str(h))
                if v is not None:
                    g[h].append(v)
    out = {}
    for grp, g in rows.items():
        out[grp] = {}
        for h in HORIZONS:
            v = g[h]
            out[grp]["h%d" % h] = {"n": len(v), "mean_follow": round(statistics.mean(v), 3) if v else None,
                                   "pos_share": round(sum(1 for x in v if x > 0) / len(v), 2) if v else None,
                                   "enough": len(v) >= MIN_N}
    return out
