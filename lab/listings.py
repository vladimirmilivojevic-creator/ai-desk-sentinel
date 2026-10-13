"""Radar listinga (senka). Svaki krug straze cita javna saopstenja o novim listinzima (Upbit: spisak obavestenja; Coinbase: nov proizvod na spisku),
prepoznaje oznaku kovanice SKRIPTOM (bez AI-ja), belezi cenu u trenutku kad je straza videla saopstenje i koliko je cena vec otisla od saopstenja,
pa meri sta bi se desilo da se pokret pratio (ili izbegao) posle 15 min, 1 h, 4 h i 24 h, neto posle troska. Nikad ne trguje i ne budi mozak.
Poziva ga lab/jumps.py sa istim cenama (bez dodatnih poziva Hyperliquid-u). Pada tiho: nikad ne obara stražu.
Izlaz u <state>/listings/: seen.json, events.json, summary.json."""
import datetime as dt
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN = 60000
UA = {"User-Agent": "Mozilla/5.0 (sentinel-listings)"}


def load_cfg(path=None):
    with open(path or os.path.join(ROOT, "config", "listings.json"), encoding="utf-8") as f:
        return json.load(f)


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_json(url, timeout=20):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return json.load(r)


# ---------------------------------------------------------------- izvori (zamenjivi u testovima)
def fetch_upbit(cfg):
    return (_get_json(cfg["upbit"]["url"]).get("data") or {}).get("notices") or []


def fetch_coinbase_bases(cfg):
    """Skup osnovnih oznaka koje se trguju (online) na Coinbase-u uz USD/USDT/USDC."""
    quotes = set(cfg["coinbase"]["quotes"])
    return {p["base_currency"] for p in _get_json(cfg["coinbase"]["url"], 40) if p.get("quote_currency") in quotes and p.get("status") == "online"
            and not p.get("trading_disabled")}


def spot_price(sym, cfg):
    j = _get_json(cfg["binance_spot"] % sym, 15)
    return float(j["price"])


# ---------------------------------------------------------------- obrada
def parse_upbit(notices, cfg):
    """[{id, t_ms, title, syms}] samo za PRVA saopstenja o novom listingu (izmene, otkazivanja, upozorenja i gasenja se preskacu)."""
    u = cfg["upbit"]
    out = []
    for n in notices:
        title = str(n.get("title") or "")
        if not any(w in title for w in u["listing_words"]) or any(w in title for w in u["skip_words"]):
            continue
        syms = [s for s in re.findall(r"\(([A-Z0-9]{1,12})\)", title)]
        try:
            t = dt.datetime.fromisoformat(str(n["listed_at"]))
        except (KeyError, ValueError):
            continue
        if syms:
            out.append({"id": str(n.get("id")), "t_ms": int(t.timestamp() * 1000), "title": title, "syms": syms})
    return out


def hl_name(sym, ctx):
    for k in (sym, "k" + sym):
        if k in ctx:
            return k, (1000.0 if k != sym else 1.0)
    return None, 1.0


def price_of(sym, ctx, cfg, spot=None):
    """(cena po jedinici kovanice, izvor, OI u USD ili None) ili None. Hyperliquid oznaka ako postoji, inace Binance spot."""
    k, scale = hl_name(sym, ctx)
    if k:
        try:
            return float(ctx[k]["mark"]) / scale, "hl", float(ctx[k].get("oi_usd") or 0.0)
        except (KeyError, TypeError, ValueError):
            pass
    try:
        return (spot or spot_price)(sym, cfg), "binance", None
    except Exception:  # noqa: BLE001
        return None


def price_before(snap, sym, t_ms, ctx, max_back_min=40):
    """Cena iz radara skokova (oznake na ~5 min) neposredno PRE saopstenja, ili None."""
    k, scale = hl_name(sym, ctx)
    pts = (snap or {}).get(k or "", [])
    best = None
    for p in pts:
        if p[0] <= t_ms and t_ms - p[0] <= max_back_min * MIN:
            best = p
    return None if best is None else best[1] / scale


def make_event(source, ref, sym, t_ms, now_ms, ctx, snap, cfg, spot=None):
    got = price_of(sym, ctx, cfg, spot)
    px0, venue, oi = (got if got else (None, None, None))
    before = price_before(snap, sym, t_ms, ctx) if px0 else None
    cost = cfg["cost_pct"]["no_perp"] if venue != "hl" else cfg["cost_pct"]["thin" if (oi or 0) < cfg["thin_oi_usd"] else "normal"]
    return {"id": "%s:%s:%s" % (source, ref, sym), "source": source, "sym": sym, "t_ms": t_ms, "t": iso(t_ms), "detected_ms": now_ms, "detected": iso(now_ms),
            "delay_min": round((now_ms - t_ms) / MIN, 1), "px0": px0, "venue": venue, "oi_usd": None if oi is None else round(oi),
            "px_before": before, "move_before_detect_pct": None if not (px0 and before) else round((px0 / before - 1.0) * 100.0, 2),
            "cost": cost, "due": {str(m): now_ms + m * MIN for m in cfg["outcomes_min"]}, "out": {str(m): None for m in cfg["outcomes_min"]},
            "peak_pct": 0.0, "trough_pct": 0.0}


def update_outcomes(events, ctx, cfg, now_ms, spot=None):
    for e in events:
        if e["px0"] is None or all(v is not None for v in e["out"].values()):
            continue
        if now_ms > e["detected_ms"] + (max(map(int, e["due"])) + cfg["late_min"]) * MIN:
            for m, v in e["out"].items():
                if v is None:
                    e["out"][m] = {"missed": True}
            continue
        got = price_of(e["sym"], ctx, cfg, spot)
        if not got:
            continue
        move = (got[0] / e["px0"] - 1.0) * 100.0
        e["peak_pct"], e["trough_pct"] = round(max(e["peak_pct"], move), 2), round(min(e["trough_pct"], move), 2)
        for m, due in e["due"].items():
            if e["out"][m] is not None or now_ms < due:
                continue
            e["out"][m] = {"missed": True} if now_ms - due > cfg["late_min"] * MIN else {"gross": round(move, 3), "net": round(move - e["cost"], 3), "px": got[0]}
    return events


def _stats(vals):
    n = len(vals)
    if not n:
        return {"n": 0}
    s = sorted(vals)
    return {"n": n, "mean": round(sum(vals) / n, 3), "median": round(s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2, 3), "pos": round(100.0 * sum(1 for v in vals if v > 0) / n, 1)}


def summarize(events, cfg):
    out = {}
    for key, es in (("all", events), ("upbit", [e for e in events if e["source"] == "upbit"]), ("coinbase", [e for e in events if e["source"] == "coinbase"])):
        row = {"events": len(es), "with_price": sum(1 for e in es if e["px0"]),
               "move_before_detect": _stats([e["move_before_detect_pct"] for e in es if e["move_before_detect_pct"] is not None]),
               "delay_min": _stats([e["delay_min"] for e in es])}
        for m in map(str, cfg["outcomes_min"]):
            done = [e for e in es if e["out"].get(m) and "net" in e["out"][m]]
            row["follow_net_%sm" % m] = _stats([e["out"][m]["net"] for e in done])
            row["fade_net_%sm" % m] = _stats([-e["out"][m]["gross"] - e["cost"] for e in done])
        out[key] = row
    return out


def run(state_dir, ctx, now_ms, snap=None, cfg=None, log=print, upbit=None, coinbase=None, spot=None):
    cfg = cfg or load_cfg()
    d = os.path.join(state_dir, "listings")
    seen = _load(os.path.join(d, "seen.json"), {})
    events = _load(os.path.join(d, "events.json"), [])
    update_outcomes(events, ctx, cfg, now_ms, spot)
    new, health = [], {}
    try:
        notices = parse_upbit((upbit or fetch_upbit)(cfg), cfg)
        known = set(seen.get("upbit", []))
        for n in notices:
            if "upbit" in seen and n["id"] not in known:  # prvi krug samo upisuje stara saopstenja (nema lazno novih dogadjaja)
                for sym in n["syms"]:
                    new.append(make_event("upbit", n["id"], sym, n["t_ms"], now_ms, ctx, snap, cfg, spot))
        seen["upbit"] = sorted(known | {n["id"] for n in notices})[-cfg["seen_keep"]:]
        health["upbit"] = "ok"
    except Exception as e:  # noqa: BLE001
        health["upbit"] = "%s %s" % (type(e).__name__, str(e)[:60])
    try:
        bases = (coinbase or fetch_coinbase_bases)(cfg)
        if "coinbase" in seen:
            for b in sorted(bases - set(seen["coinbase"])):
                new.append(make_event("coinbase", iso(now_ms)[:13], b, now_ms, now_ms, ctx, snap, cfg, spot))  # saopstenje nema vreme: koristi se trenutak otkrivanja
        seen["coinbase"] = sorted(set(seen.get("coinbase", [])) | bases)
        health["coinbase"] = "ok"
    except Exception as e:  # noqa: BLE001
        health["coinbase"] = "%s %s" % (type(e).__name__, str(e)[:60])
    ids = {e["id"] for e in events}
    new = [e for e in new if e["id"] not in ids]
    events = (events + new)[-cfg["keep_events"]:]
    _save(os.path.join(d, "seen.json"), seen)
    _save(os.path.join(d, "events.json"), events)
    _save(os.path.join(d, "summary.json"), {"updated_utc": iso(now_ms), "cfg_version": cfg["version"], "sources": health, "events": len(events),
                                            "summary": summarize(events, cfg),
                                            "last": [{k: e[k] for k in ("t", "source", "sym", "delay_min", "venue", "move_before_detect_pct", "peak_pct")} for e in events[-8:]]})
    for e in new:
        log("listing: %s %s (%s), cena vec %s%% od saopstenja" % (e["source"], e["sym"], e["venue"], e["move_before_detect_pct"]))
    return {"events": len(events), "new": len(new), "sources": health}
