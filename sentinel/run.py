"""Straza: jedan krug (poziva se svakih ~5 min iz GitHub Actions). Bez AI-ja.

Straza je zvono, ne svedok: ne trguje i ne odlucuje. Mozak sve brojke ponovo proverava.
Pokretanje: python -m sentinel.run --state _state --root . [--dry] [--probe]
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import os
import sys
import time

from . import calendar_guard, episodes, notify, scoring, signals, sources
from .util import SourceError, canon, iso, pct, read_json, sha12, utcnow, write_json

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(os.path.dirname(HERE), "config")


def cfg_load(name):
    d = read_json(os.path.join(CONFIG, name))
    if d is None:
        raise SystemExit("nedostaje config/" + name)
    return d


class State:
    def __init__(self, path):
        self.path = path
        self.data = {}

    def get(self, name, default):
        if name not in self.data:
            self.data[name] = read_json(os.path.join(self.path, name + ".json"), default)
        return self.data[name]

    def save(self):
        for name, obj in self.data.items():
            write_json(os.path.join(self.path, name + ".json"), obj)


class Health:
    """3 uzastopna pada = izvor 'degradiran' i njegovi signali se ne racunaju dok ne prorade."""

    def __init__(self, d):
        self.d = d

    def record(self, name, ok, ms, err=None):
        h = self.d.setdefault(name, {"fails": 0, "ok": None, "last_ok": None, "last_err": None, "ms": None})
        h["ms"] = ms
        h["ok"] = ok
        if ok:
            h["fails"], h["last_ok"], h["last_err"] = 0, iso(time.time()), None
        else:
            h["fails"] += 1
            h["last_err"] = err

    def usable(self, name):
        h = self.d.get(name)
        return not h or h["fails"] < 3

    def degraded(self):
        return sorted(k for k, v in self.d.items() if v["fails"] >= 3)


def par(tasks, health, workers=8):
    """tasks: {ime: (fn, args)}. Vraca {ime: rezultat ili None}; belezi zdravlje izvora."""
    out = {}

    def one(item):
        name, (fn, args) = item
        t = time.time()
        try:
            return name, fn(*args), int((time.time() - t) * 1000), None
        except SourceError as e:
            return name, None, int((time.time() - t) * 1000), str(e)
        except Exception as e:  # lose formatiran odgovor
            return name, None, int((time.time() - t) * 1000), type(e).__name__

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for name, res, ms, err in ex.map(one, tasks.items()):
            health.record(name, err is None, ms, err)
            out[name] = res
    return out


def fmt_pct(x):
    return ("%+.1f%%" % x).replace(".", ",") if x is not None else "n/a"


def build_message(theme, ev, kind, insts, fire_note):
    names = {i["key"]: i["name"] for i in insts}
    moves = ", ".join("%s %s/60m" % (names.get(p["key"], p["key"]), fmt_pct(p["m60"])) for p in ev["psigs"])
    fams = ", ".join("%s %s" % (k, str(v).replace(".", ",")) for k, v in ev["families"].items())
    sched = " [ZAKAZANO: %s]" % ev["scheduled"][0] if ev["scheduled"] else ""
    return ("%s %s%s | %s | ocena %s (%s) | %s%s" % (ev["tier"], theme, {"escalate": " eskalacija", "step": " novi korak"}
            .get(kind, ""), moves, str(ev["score"]).replace(".", ","), fams, fire_note, sched))[:400]


def collect(cfg, insts, q, state, health, now):
    """Dohvata sve izvore paralelno. Vraca recnik sirovih rezultata."""
    tasks = {}
    for dex in sorted({i["dex"] for i in insts}):
        tasks["hl_ctx_" + (dex or "main")] = (sources.hl_ctx, (dex,))
    for i in insts:
        if not i.get("ctx_only"):
            tasks["hl_candles_" + i["key"]] = (sources.hl_candles, (i["hl"], "5m", 300))
        if i.get("yahoo"):
            tasks["yahoo_" + i["key"]] = (sources.yahoo_series, (i["yahoo"],))
    for n, qq in enumerate(q["google_news"]):
        tasks["gnews_%d" % n] = (sources.gnews, (qq,))
    for f in q["rss"]:
        tasks["rss_" + f["name"]] = (sources.rss, (f["url"], f["name"]))
    for f in q["official_rss"]:
        tasks["official_" + f["name"]] = (sources.rss, (f["url"], f["name"]))
    tasks["polymarket"] = (sources.polymarket, ())
    return par(tasks, health)


def refresh_vol(insts, state, health, now):
    vol = state.get("vol", {})
    stale = [i for i in insts if not i.get("ctx_only") and now - vol.get(i["key"], {}).get("ts", 0) > 86400]
    if not stale:
        return vol
    res = par({"hl_vol_" + i["key"]: (sources.hl_candles, (i["hl"], "1h", 20 * 1440)) for i in stale}, health)
    for i in stale:
        rows = res.get("hl_vol_" + i["key"])
        if rows:
            vol[i["key"]] = {"sigma60": scoring.sigma_from_hourly([c for _, c in rows]), "ts": now}
    return vol


def run(args):
    now = time.time()
    cfg, insts = cfg_load("sentinel.json"), cfg_load("instruments.json")["instruments"]
    q, cal = cfg_load("queries.json"), cfg_load("calendar.json")
    S = State(args.state)
    health = Health(S.get("health", {}))
    log = []

    raw = collect(cfg, insts, q, S, health, now)
    ctx = {}
    for k, v in raw.items():
        if k.startswith("hl_ctx_") and v:
            ctx.update(v)

    prices = S.get("prices", {})
    for i in insts:
        c = ctx.get(i["hl"])
        if c:
            buf = prices.setdefault(i["key"], [])
            buf.append([now, c["mark"]])
            buf[:] = [x for x in buf if now - x[0] <= 6 * 3600]

    vol = refresh_vol(insts, S, health, now)
    S.data["vol"] = vol

    psigs = []
    for i in insts:
        key = i["key"]
        series, provider = None, None
        ys = raw.get("yahoo_" + key) if health.usable("yahoo_" + key) else None
        second = ys
        if i.get("ctx_only") and ys and now - ys[-1][0] <= cfg["stale_minutes"] * 60:
            # VIX i DXY: pravi indeks je Yahoo; xyz:VIX i xyz:DXY na Hyperliquid-u imaju drugu skalu
            series, provider, second = ys, "yahoo", None
        elif raw.get("hl_candles_" + key) and health.usable("hl_candles_" + key):
            series, provider = list(raw["hl_candles_" + key]), "hl-sveće"
            if ctx.get(i["hl"]):
                series.append((now, ctx[i["hl"]]["mark"]))
        elif len(prices.get(key, [])) >= 2:
            series, provider = [(t, p) for t, p in prices[key]], "hl-bafer"
        if not series and ys:
            series, provider, second = ys, "yahoo", None
        sig = scoring.price_signal(i, series, provider, second, (vol.get(key) or {}).get("sigma60"), cfg, now)
        c = ctx.get(i["hl"])
        if c and c.get("prev_day") and not (i.get("ctx_only") and sig.get("provider") == "yahoo"):
            sig["ch24"] = pct(c["mark"], c["prev_day"])  # za VIX/DXY sa Yahoo-a ne mesamo skale Hyperliquid-a
        if c:
            sig["funding"] = c.get("funding")
        psigs.append(sig)

    # nivo VIX poredi se samo sa pravim VIX-om (Yahoo), nikad sa xyz:VIX iz bafera
    vix = next((p.get("px") for p in psigs if p["key"] == "VIX" and not p.get("stale") and p.get("provider") == "yahoo"),
               None)
    cross = scoring.cross_signal(psigs, cfg, vix)

    items = []
    for k, v in raw.items():
        if (k.startswith("gnews_") or k.startswith("rss_")) and v and health.usable(k):
            items.extend(v)
    head = scoring.headline_signal(items, now, cfg, q)
    head_hist = S.get("head_hist", {})
    head = scoring.apply_baseline(head, head_hist, cfg)
    off_items = []
    for k, v in raw.items():
        if k.startswith("official_") and v and health.usable(k):
            off_items.extend(v)
    offi = scoring.official_signal(off_items, now, cfg, q)

    hist = S.get("poly", {})
    movers = []
    if raw.get("polymarket") and health.usable("polymarket"):
        movers = scoring.prediction_signal(raw["polymarket"], hist, now, cfg, q)

    gd = {"fired": False, "ratio": None}
    meta = S.get("meta", {})
    if cfg["gdelt"]["enabled"] and now >= meta.get("gdelt_block", 0) and now - meta.get("gdelt_last", 0) >= cfg["gdelt"][
            "every_min"] * 60:
        meta["gdelt_last"] = now
        r = par({"gdelt": (sources.gdelt_timeline, ("(war OR missile OR blockade OR strike) sourcelang:eng",))}, health)
        if r.get("gdelt"):
            gd = scoring.gdelt_signal(r["gdelt"], cfg)
        elif (health.d.get("gdelt") or {}).get("last_err") == "HTTP 429":
            meta["gdelt_block"] = now + 20 * 60

    themes = scoring.evaluate_themes(psigs, cross, head, offi, movers, gd, cfg)
    flags = calendar_guard.scheduled_flags(now, cal)

    open_eps = S.get("episodes", {"open": {}})["open"]
    fires = S.get("firelog", {"fires": []})["fires"]
    recent = S.get("events_recent", {"events": []})["events"]
    new_events, messages = [], []
    day = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y%m%dT%H%MZ")

    for th, ev in sorted(themes.items()):
        ev["psigs"] = [p for p in psigs if p["key"] in ev["instruments"]]
        ev["scheduled"] = flags
        act = episodes.step(th, ev, psigs, now, open_eps, cfg)
        if not act or act["kind"] == "closed":
            continue
        eid, n = "EV-%s-%s" % (day, th), 1
        while any(e["id"] == eid for e in new_events + recent):
            n += 1
            eid = "EV-%s-%s-%d" % (day, th, n)
        ok, why = episodes.fire_allowed(fires, now, cfg)
        will_fire = ok and ev["tier"] in ("N2", "N3")
        event = {
            "schema": 1, "id": eid, "ts": iso(now), "theme": th, "tier": ev["tier"], "kind": act["kind"],
            "score": ev["score"], "families": ev["families"], "why": ev["why"], "direction": ev["direction"],
            "scheduled": flags, "mode": cfg["mode"], "brain_fired": will_fire, "fire_gate": why,
            "instruments": [{"key": p["key"], "hl": next(i["hl"] for i in insts if i["key"] == p["key"]),
                             "px": p.get("px"), "m60": p.get("m60"), "m240": p.get("m240"), "ch24": p.get("ch24"),
                             "confirmed": p.get("confirmed"), "funding": p.get("funding"), "provider": p["provider"],
                             "thr60": next(i["thr60"] for i in insts if i["key"] == p["key"]), "eff60": p.get("eff60")}
                            for p in ev["psigs"]],
            "all_moves": {p["key"]: p.get("m60") for p in psigs if not p.get("stale")},
            "untrusted_text": {"headlines": [{"title": x["title"], "source": x["source"]} for x in head["top"]],
                               "predictions": [{"q": m["q"], "delta": round(m["delta"], 2)} for m in movers[:3]]},
        }
        raw_bytes = canon(event)
        path = os.path.join(args.root, "events", day[:4], day[4:6], eid + ".json")
        if not args.dry or args.write_events:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(raw_bytes)
        new_events.append({"id": eid, "tier": ev["tier"], "theme": th, "sha12": sha12(raw_bytes), "fire": will_fire})
        note = ("mozak okinut" if will_fire else "mozak se NE okida (%s)" % why)
        messages.append(build_message(th, ev, act["kind"], insts, note))
        recent.insert(0, {"id": eid, "ts": iso(now), "theme": th, "tier": ev["tier"], "text": messages[-1],
                          "scheduled": bool(flags)})

    # dnevnik signala i ishoda (ucenje bez trejdova): svaki cenovni okidac, makar ostao N1
    sstore = S.get("signals", {"open": [], "closed": [], "last": {}})
    vol_ctx = {p["key"]: round(p["px"], 2) for p in psigs if p["key"] in ("VIX", "OVX", "GVZ") and not p.get("stale")}
    ev_by_theme = {e["theme"]: e["id"] for e in new_events}
    signals.record(psigs, themes, ev_by_theme, now, sstore, vol_ctx)
    hl_of = {i["key"]: i["hl"] for i in insts if not i.get("ctx_only") and i.get("hl")}
    closed_now = signals.update_outcomes(sstore, now, sources.hl_candles, hl_of)
    if closed_now and (not args.dry or args.write_events):
        month = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m")
        sp = os.path.join(args.root, "signals", "closed-%s.jsonl" % month)
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        with open(sp, "ab") as f:
            for sg in closed_now:
                f.write(canon(sg))
    S.data["signals"] = sstore

    # okidanje mozga: jedan poziv za sve nove N2+ dogadjaje ovog kruga
    firing = [e for e in new_events if e["fire"]]
    fire_result = None
    if firing:
        tier = "N3" if any(e["tier"] == "N3" for e in firing) else "N2"
        payload = {"v": 1, "tier": tier, "event_ids": [e["id"] for e in firing],
                   "sha12": {e["id"]: e["sha12"] for e in firing}}
        if getattr(args, "defer_fire", False) and not args.dry:
            # okidanje tek POSLE objave dogadjaja na main (inace mozak moze da stigne pre fajla)
            write_json(os.path.join(args.state, "pending_fire.json"), {"payload": payload, "created": iso(now),
                                                                      "attempts": 0})
            fires.append(now)
            fire_result = (True, "u redu za okidanje")
        else:
            fire_result = notify.fire_brain(payload, dry=args.dry)
            if fire_result[0]:
                fires.append(now)
        messages.append("FIRE %s: %s" % (tier, fire_result[1]))
        log.append(("fire", fire_result[1]))
    for m in messages:
        ok, info = notify.telegram(m, dry=args.dry)
        log.append(("telegram", info))

    # zdravlje izvora: obavest najvise na 6 h
    deg = health.degraded()
    if deg and now - meta.get("deg_alert", 0) > 6 * 3600 and not args.dry:
        notify.telegram("Straza: izvori ne rade 3 puta zaredom: %s" % ", ".join(deg)[:300])
        meta["deg_alert"] = now

    # dnevni log (prethodni dan) i dnevni pregled
    runlog = S.get("runlog", {"lines": []})["lines"]
    today = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m-%d")
    if meta.get("day") and meta["day"] != today:
        old = [x for x in runlog if x["ts"].startswith(meta["day"])]
        if old and not args.dry:
            lp = os.path.join(args.root, "log", meta["day"] + ".jsonl")
            os.makedirs(os.path.dirname(lp), exist_ok=True)
            with open(lp, "wb") as f:
                for x in old:
                    f.write(canon(x))
    meta["day"] = today
    hour = dt.datetime.fromtimestamp(now, dt.timezone.utc).hour
    if hour >= cfg["digest_hour_utc"] and meta.get("digest") != today:
        last24 = [e for e in recent if now - _ts(e["ts"]) < 86400]
        txt = "Straza, dnevni pregled: %d dogadjaja N2+ u 24 h (N3: %d). Degradirani izvori: %s. Rezim: %s." % (
            len(last24), sum(1 for e in last24 if e["tier"] == "N3"), ", ".join(deg) or "nema", cfg["mode"])
        notify.telegram(txt, dry=args.dry)
        meta["digest"] = today

    runlog.append({"ts": iso(now), "mode": cfg["mode"],
                   "moves": {p["key"]: (None if p.get("m60") is None else round(p["m60"], 2)) for p in psigs
                             if not p.get("stale")},
                   "tiers": {t: v["tier"] for t, v in themes.items() if v["tier"]},
                   "head_n": head["n"], "movers": len(movers), "degraded": deg})
    runlog[:] = runlog[-cfg["keep_runlog_lines"]:]
    S.data["runlog"] = {"lines": runlog}
    recent[:] = recent[:50]
    S.data["events_recent"] = {"events": recent}
    S.data["episodes"] = {"open": open_eps}
    fires[:] = [t for t in fires if now - t < 2 * 86400]
    S.data["firelog"] = {"fires": fires}
    S.data["prices"], S.data["poly"], S.data["meta"], S.data["health"] = prices, hist, meta, health.d
    S.data["head_hist"] = head_hist

    status = {
        "v": 1, "updated": iso(now), "mode": cfg["mode"], "fire_enabled": cfg["fire_enabled"],
        "instruments": [{"key": p["key"], "name": p["name"], "px": p.get("px"), "ch24": p.get("ch24"),
                         "m60": p.get("m60"), "m240": p.get("m240"), "stale": bool(p.get("stale")),
                         "hot": bool(p.get("trig")), "provider": p.get("provider")} for p in psigs],
        "themes": {t: {"tier": v["tier"], "score": v["score"], "families": sorted(v["families"])}
                   for t, v in themes.items()},
        "events": recent[:20],
        "sources": {k: {"ok": v["ok"], "fails": v["fails"], "last_ok": v["last_ok"]} for k, v in health.d.items()},
        "heartbeat": {"ts": iso(now), "interval_min": 5}, "scheduled": flags, "degraded": deg,
        "headlines_scored": head["n"],
    }
    os.makedirs(os.path.join(args.state, "status"), exist_ok=True)
    S.save()
    write_json(os.path.join(args.state, "status", "latest.json"), status)
    # mali fajl za Desk Park (preko read_link); bez detalja o izvorima
    slim = {k: status[k] for k in ("v", "updated", "mode", "fire_enabled", "instruments", "themes", "scheduled",
                                  "degraded", "headlines_scored", "heartbeat")}
    slim["events"] = recent[:10]
    slim["signals"] = {"open": len(sstore.get("open", [])), "closed": len(sstore.get("closed", []))}
    write_json(os.path.join(args.state, "status", "stats.json"),
               {"updated": iso(now), "open": len(sstore.get("open", [])), "closed": len(sstore.get("closed", [])),
                "min_n": signals.MIN_N, "stats": signals.stats(sstore)})
    slim["sources_ok"] = sum(1 for v in health.d.values() if v["ok"])
    slim["sources_total"] = len(health.d)
    write_json(os.path.join(args.state, "status", "panel.json"), slim)
    write_json(os.path.join(args.state, "heartbeat.json"), status["heartbeat"])
    summary(psigs, themes, head, movers, offi, cross, flags, deg, new_events, log, now)
    return 0


def _ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()


def summary(psigs, themes, head, movers, offi, cross, flags, deg, new_events, log, now):
    print("== straza", iso(now))
    for p in psigs:
        if p.get("stale"):
            print("  %-7s STARA/nema (%s)" % (p["key"], p.get("reason")))
        else:
            print("  %-7s %-10s px %-10.4g m60 %s m240 %s %s%s" % (
                p["key"], p["provider"], p["px"], fmt_pct(p.get("m60")), fmt_pct(p.get("m240")),
                "TRIG " if p.get("trig") else "", "potvrdjeno" if p.get("confirmed") else ""))
    print("  naslovi ocenjeni: %d | zvanicni: %d | prediction pomaci: %d | X: %s | zakazano: %s | degradirano: %s" % (
        head["n"], len(offi), len(movers), cross["reasons"] or "-", flags or "-", deg or "-"))
    for t, v in themes.items():
        if v["tier"]:
            print("  tema %-7s %s ocena %s %s" % (t, v["tier"], v["score"], v["families"]))
    for e in new_events:
        print("  NOVI DOGADJAJ", e)
    for l in log:
        print("  ", l)


def probe():
    """Jedan poziv svakog izvora: status, kasnjenje, uzorak. Za proveru iz GitHub Actions."""
    insts = cfg_load("instruments.json")["instruments"]
    q = cfg_load("queries.json")
    tasks = {"hl_ctx_xyz": (sources.hl_ctx, ("xyz",)), "hl_ctx_main": (sources.hl_ctx, ("",)),
             "hl_candles_BRENT": (sources.hl_candles, ("xyz:BRENTOIL", "5m", 300)),
             "yahoo_BZ=F": (sources.yahoo_series, ("BZ=F",)), "yahoo_BTC-USD": (sources.yahoo_series, ("BTC-USD",)),
             "yahoo_^VIX": (sources.yahoo_series, ("^VIX",)),
             "gnews": (sources.gnews, (q["google_news"][0],)), "polymarket": (sources.polymarket, ()),
             "gdelt": (sources.gdelt_timeline, ("(war OR missile) sourcelang:eng",))}
    for f in q["rss"] + q["official_rss"]:
        tasks["rss_" + f["name"]] = (sources.rss, (f["url"], f["name"]))
    h = Health({})
    t0 = time.time()
    res = par(tasks, h)
    print("izvor | ok | ms | uzorak")
    for k in tasks:
        v = res.get(k)
        hh = h.d[k]
        sample = "-" if v is None else ("%d redova" % len(v))
        print("%s | %s | %s | %s %s" % (k, "DA" if hh["ok"] else "NE", hh["ms"], sample, hh["last_err"] or ""))
    print("ukupno %.1f s" % (time.time() - t0))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="_state")
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry", action="store_true", help="bez Telegram-a, bez okidanja, bez upisa dnevnog loga")
    ap.add_argument("--write-events", action="store_true")
    ap.add_argument("--defer-fire", action="store_true",
                    help="ne okidaj mozak u ovom koraku nego upisi pending_fire.json (okida sentinel.fire posle objave)")
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args(argv)
    if a.probe:
        return probe()
    os.makedirs(a.state, exist_ok=True)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
