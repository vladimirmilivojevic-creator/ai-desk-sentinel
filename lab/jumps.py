"""Radar skokova (senka). Svaki krug straze (oko 5 min) uzme oznake cena svih instrumenata sa Hyperliquid-a (glavni dex i xyz, dva poziva),
zapamti ih nekoliko sati unazad i beleži nagle skokove i padove: >= +-15% za 60 min ili >= +-25% za 240 min (config/jumps.json, upisano unapred).
Za svaki dogadjaj meri sta bi se desilo da se pokret PRATIO (isti smer) posle 1 h, 4 h i 24 h, neto posle troska, i najveci/najmanji pokret
u medjuvremenu. Nikad ne trguje, ne budi mozak i ne trosi tokene; pada tiho (nikad ne obara stražu).
Izlaz u <state>/jumps/: snap.json (oznake), events.json (dogadjaji sa ishodima), summary.json (zbir po okidacu i smeru).
Upotreba: python -m lab.jumps --state _state"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN = 60000


def load_cfg(path=None):
    with open(path or os.path.join(ROOT, "config", "jumps.json"), encoding="utf-8") as f:
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
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ms / 1000.0))


def update_snap(snap, ctx, now_ms, keep_min):
    """snap: {coin: [[t_ms, mark, vol24], ...]} (staro se odseca posle keep_min). Nevazece oznake se preskacu."""
    for coin, c in ctx.items():
        try:
            mark, vol = float(c["mark"]), float(c.get("vol24") or 0.0)
        except (KeyError, TypeError, ValueError):
            continue
        if not mark > 0:
            continue
        pts = snap.setdefault(coin, [])
        if pts and pts[-1][0] >= now_ms:
            continue
        pts.append([now_ms, mark, vol])
    cut = now_ms - keep_min * MIN
    for coin in list(snap):
        snap[coin] = [p for p in snap[coin] if p[0] >= cut]
        if not snap[coin] or coin not in ctx and snap[coin][-1][0] < now_ms - 30 * MIN:
            del snap[coin]
    return snap


def base_point(pts, now_ms, window_min, tol_min):
    """Tacka najbliza trenutku now - window u okviru tolerancije, ili None (rupa u podacima: nema poredjenja)."""
    target = now_ms - window_min * MIN
    best = None
    for p in pts:
        d = abs(p[0] - target)
        if d <= tol_min * MIN and (best is None or d < abs(best[0] - target)):
            best = p
    return best


def detect(snap, ctx, events, cfg, now_ms):
    """Novi dogadjaji za sve instrumente koji su pre mimo hladjenja prešli prag. Jedan dogadjaj po instrumentu u cooldown_min."""
    out, tol = [], cfg["base_tolerance_min"]
    recent = {}
    for e in events:
        recent[e["coin"]] = max(recent.get(e["coin"], 0), e["t_ms"])
    for coin, pts in snap.items():
        if not pts or pts[-1][0] != now_ms or coin not in ctx:
            continue
        if now_ms - recent.get(coin, 0) < cfg["cooldown_min"] * MIN:
            continue
        cur = pts[-1]
        rets = {}
        for name, t in cfg["triggers"].items():
            b = base_point(pts, now_ms, t["window_min"], tol)
            if b:
                rets[name] = (cur[1] / b[1] - 1.0) * 100.0, b
        hit = None
        for name, t in cfg["triggers"].items():  # burst ima prednost nad ramp
            r = rets.get(name)
            if r and abs(r[0]) >= t["ret_pct"]:
                hit = (name, r[0], r[1])
                break
        if not hit:
            continue
        name, ret, base = hit
        c = ctx[coin]
        oi = float(c.get("oi_usd") or 0.0)
        out.append({"id": "%s@%s" % (coin, iso(now_ms)), "coin": coin, "t_ms": now_ms, "t": iso(now_ms), "trigger": name,
                    "dir": "up" if ret > 0 else "down", "ret_pct": round(ret, 2), "mark": cur[1], "vol24": round(cur[2]),
                    "vol24_base": round(base[2]), "oi_usd": round(oi), "thin": oi < cfg["thin_oi_usd"],
                    "due": {str(m): now_ms + m * MIN for m in cfg["outcomes_min"]}, "out": {str(m): None for m in cfg["outcomes_min"]},
                    "peak_pct": 0.0, "trough_pct": 0.0})
    return out


def update_outcomes(events, ctx, cfg, now_ms):
    """Za svaki dogadjaj: najveci i najmanji pokret u smeru dogadjaja (u %), i ishod 'prati pokret' kad dodje vreme (neto posle troska).
    Ishod kasni vise od late_min = 'missed' (ne racuna se). Menja events na mestu."""
    for e in events:
        c = ctx.get(e["coin"])
        if not c:
            continue
        try:
            px = float(c["mark"])
        except (KeyError, TypeError, ValueError):
            continue
        if not px > 0:
            continue
        sign = 1.0 if e["dir"] == "up" else -1.0
        move = sign * (px / e["mark"] - 1.0) * 100.0
        if now_ms <= e["t_ms"] + max(map(int, e["due"])) * MIN + cfg["late_min"] * MIN:
            e["peak_pct"] = round(max(e["peak_pct"], move), 2)
            e["trough_pct"] = round(min(e["trough_pct"], move), 2)
        cost = cfg["cost_pct"]["thin" if e["thin"] else "normal"]
        for m, due in e["due"].items():
            if e["out"][m] is not None or now_ms < due:
                continue
            if now_ms - due > cfg["late_min"] * MIN:
                e["out"][m] = {"missed": True}
                continue
            e["out"][m] = {"gross": round(move, 3), "net": round(move - cost, 3), "px": px}
    return events


def _stats(vals):
    n = len(vals)
    if not n:
        return {"n": 0}
    s = sorted(vals)
    mean = sum(vals) / n
    out = {"n": n, "mean": round(mean, 3), "median": round(s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2, 3),
           "pos": round(100.0 * sum(1 for v in vals if v > 0) / n, 1)}
    if n >= 5:
        var = sum((v - mean) ** 2 for v in vals) / (n - 1)
        out["t_naive"] = round(mean / ((var / n) ** 0.5), 2) if var > 0 else None  # dogadjaji u istom satu su zavisni: samo okvirno
    return out


def summarize(events, cfg):
    """{"trigger/dir/thin": {"n": broj dogadjaja, "60": {...}, "240": {...}, "1440": {...}}} za 'prati' (neto) i srednji vrh/dno."""
    groups = {}
    for e in events:
        for key in ("all", "%s/%s" % (e["trigger"], e["dir"]), "%s/%s/%s" % (e["trigger"], e["dir"], "tanko" if e["thin"] else "likvidno")):
            groups.setdefault(key, []).append(e)
    out = {}
    for key, es in sorted(groups.items()):
        row = {"events": len(es), "peak_mean": round(sum(e["peak_pct"] for e in es) / len(es), 2),
               "trough_mean": round(sum(e["trough_pct"] for e in es) / len(es), 2)}
        for m in map(str, cfg["outcomes_min"]):
            done = [e for e in es if e["out"].get(m) and "net" in e["out"][m]]
            row["follow_net_%sm" % m] = _stats([e["out"][m]["net"] for e in done])
            row["fade_net_%sm" % m] = _stats([-e["out"][m]["gross"] - cfg["cost_pct"]["thin" if e["thin"] else "normal"] for e in done])
        out[key] = row
    return out


def run(state_dir, cfg=None, ctx=None, now_ms=None, log=print, listings=False):
    cfg = cfg or load_cfg()
    now_ms = now_ms or int(time.time() * 1000)
    if ctx is None:
        from . import collectors as C
        ctx = C.hl_contexts()
    d = os.path.join(state_dir, "jumps")
    snap = _load(os.path.join(d, "snap.json"), {})
    events = _load(os.path.join(d, "events.json"), [])
    update_snap(snap, ctx, now_ms, cfg["snapshot_keep_min"])
    update_outcomes(events, ctx, cfg, now_ms)
    new = detect(snap, ctx, events, cfg, now_ms)
    events.extend(new)
    events = events[-cfg["keep_events"]:]
    _save(os.path.join(d, "snap.json"), snap)
    _save(os.path.join(d, "events.json"), events)
    _save(os.path.join(d, "summary.json"), {"updated_utc": iso(now_ms), "cfg_version": cfg["version"], "coins": len(snap),
                                            "events": len(events), "summary": summarize(events, cfg), "last": [
                                                {k: e[k] for k in ("t", "coin", "trigger", "dir", "ret_pct", "oi_usd", "thin", "peak_pct")}
                                                for e in events[-8:]]})
    for e in new:
        log("skok: %s %s %+.1f%% (%s), OI $%.1fM" % (e["coin"], e["trigger"], e["ret_pct"], e["dir"], e["oi_usd"] / 1e6))
    res = {"ok": True, "coins": len(snap), "new": len(new), "events": len(events)}
    if listings:  # radar listinga koristi iste cene (bez dodatnih poziva) i nikad ne sme da obori radar skokova
        try:
            from . import listings as L
            res["listings"] = L.run(state_dir, ctx, now_ms, snap=snap, log=log)
        except Exception as e:  # noqa: BLE001
            res["listings"] = {"error": type(e).__name__}
    return res


def main():
    argv = sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        res = run(state, listings=True)
    except Exception as e:  # noqa: BLE001  # radar skokova nikad ne sme da obori stražu
        res = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
