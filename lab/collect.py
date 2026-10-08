"""Orkestrator kolektora (data lake) + briefing za AI. Radi unutar workflow-a straze posle laboratorije.
Gating po zadatku (satno / na 4 h / dnevno) preko <state>/data/meta.json, izolacija gresaka po izvoru, zdravlje izvora u health.json.
Upotreba: python -m lab.collect --state _state [--force]"""
import json
import os
import statistics as st
import sys
import time

from . import backtest, binance_backfill as bb, collectors as C, collectors2 as C2, featstore, panel_scan, panelstore, trump

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOUR = 3600000
DAY = 86400000
HISTORY_KEEP = 24 * 45
RETRY_MS = 3 * HOUR
RETIRED = ("gdelt",)
HOURLY_ROWS = 24 * 7  # satni redovi samo za poslednjih 7 dana, starije svodimo na jedan red dnevno (ocenjivanje prognoza koristi satne redove)
BRIEFING_MAX_BYTES = 12_000


def iso(ms):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ms / 1000.0))


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


def due(meta, task, now_ms, every_ms=None, daily=False):
    last = meta.get("last", {}).get(task)
    if last is None:
        return True
    if daily:
        return iso(last)[:10] != iso(now_ms)[:10]
    return now_ms - last >= every_ms - 60000  # tolerancija 1 min zbog kasnjenja okidaca


def run_task(name, fn, data_dir, meta, health, now_ms, log):
    """Izvrsi zadatak; uspeh pise <name>.json, greska cuva stari fajl i belezi zdravlje."""
    h = health.setdefault(name, {"last_ok_utc": None, "last_error": None, "consecutive_failures": 0})
    try:
        res = fn()
        res = {"updated_utc": iso(now_ms), "data": res}
        _save(os.path.join(data_dir, name + ".json"), res)
        meta.setdefault("last", {})[name] = now_ms
        h.update(last_ok_utc=iso(now_ms), last_error=None, consecutive_failures=0)
        return res
    except Exception as e:  # noqa: BLE001  # jedan izvor nikad ne obara ostale
        h["last_error"] = "%s: %s" % (type(e).__name__, e)
        h["consecutive_failures"] = h.get("consecutive_failures", 0) + 1
        log("kolektor %s nije uspeo: %s" % (name, h["last_error"]))
        return _load(os.path.join(data_dir, name + ".json"), None)


def scalars(files):
    """Kljucne skalarne osobine za istoriju i z-skorove (None kad nema podatka)."""
    g = lambda d, *ks: _dig(d, ks)  # noqa: E731
    mk = (files.get("market") or {}).get("data", {})
    dv = (files.get("derivs") or {}).get("data", {})
    mac = (files.get("macro") or {}).get("data", {})
    sen = (files.get("sentiment") or {}).get("data", {})
    sm = (files.get("smart_money") or {}).get("data", {})
    return {
        "btc_fund_h": g(mk, "BTC", "ctx", "funding_h"), "eth_fund_h": g(mk, "ETH", "ctx", "funding_h"),
        "btc_oi_usd": g(mk, "BTC", "ctx", "oi_usd"), "btc_spread_bps": g(mk, "BTC", "book", "spread_bps"),
        "btc_bin_minus_hl_h": g(mk, "BTC", "fund_xv", "bin_minus_hl_h"),
        "dvol_btc": g(dv, "deribit", "dvol_btc", "last"), "dvol_eth": g(dv, "deribit", "dvol_eth", "last"),
        "put_call_oi": g(dv, "deribit", "btc_put_call_oi"), "okx_lsr_btc": g(dv, "okx_lsr", "BTC", "last"),
        "vix": g(mac, "yahoo", "VIX", "last"), "vix3m": g(mac, "yahoo", "VIX3M", "last"), "dxy": g(mac, "yahoo", "DXY", "last"),
        "hy_oas": g(mac, "fred", "BAMLH0A0HYM2", "last"), "fear_greed": g(sen, "fear_greed", "last"),
        "stable_chg_7d": g(sen, "stablecoins", "chg_7d_pct"), "btc_smart_net_share": g(sm, "coins", "BTC", "net_share"),
        "cz_btc_oi_usd": g(dv, "coinalyze", "BTC", "oi_usd"), "cz_btc_funding": g(dv, "coinalyze", "BTC", "funding_mean"),
        "cz_btc_liq_long_24h": g(dv, "coinalyze", "BTC", "liq_long_24h"), "cz_btc_liq_short_24h": g(dv, "coinalyze", "BTC", "liq_short_24h"),
        "cz_btc_lsr": g(dv, "coinalyze", "BTC", "lsr_last"),
    }


def _dig(d, ks):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def zscores(row, history, min_rows=48):
    out = {}
    for k, v in row.items():
        if v is None:
            continue
        past = [h[k] for h in history if isinstance(h.get(k), (int, float))]
        if len(past) >= min_rows and st.pstdev(past) > 0:
            out[k] = round((v - st.mean(past)) / st.pstdev(past), 2)
    return out


def regime(files):
    """Gruba, pravilima zasnovana oznaka rizika (hipoteza, ne dokaz): komponente se vide da bi ih AI proverio."""
    s = scalars(files)
    comp, score = {}, 0
    if s["vix"] is not None:
        comp["vix_visok"] = s["vix"] > 25
        score -= 1 if s["vix"] > 25 else (0 if s["vix"] > 18 else -1)
    if s["vix"] is not None and s["vix3m"] is not None:
        comp["vix_backwardation"] = s["vix"] > s["vix3m"]
        score -= 1 if s["vix"] > s["vix3m"] else 0
    oas = _dig((files.get("macro") or {}).get("data", {}), ("fred", "BAMLH0A0HYM2", "chg_5"))
    if oas is not None:
        comp["kreditni_raspon_raste"] = oas > 0.25
        score -= 1 if oas > 0.25 else 0
    if s["fear_greed"] is not None:
        comp["kripto_strah"] = s["fear_greed"] < 25
        comp["kripto_pohlepa"] = s["fear_greed"] > 75
    if s["dvol_btc"] is not None:
        comp["dvol_visok"] = s["dvol_btc"] > 60
        score -= 1 if s["dvol_btc"] > 60 else 0
    label = "risk_off" if score <= -2 else ("risk_on" if score >= 1 else "neutral")
    return {"label": label, "score": score, "components": comp, "note": "heuristika, ne dokaz"}


def extra_block(files):
    """Sazetak novih izvora za AI (puna tabela je u data/features.json)."""
    d = lambda k: ((files.get(k) or {}).get("data") or {})  # noqa: E731
    kl = d("kalshi")
    cf_ = {k: v.get("pctl") for k, v in d("cftc").items() if v}
    ll = d("llama")
    tr = d("trump")
    return {"trump": ({k: tr.get(k) for k in ("posts_1h", "posts_4h", "posts_24h", "shout_24h", "company_24h", "last_age_min", "topics_24h", "n_events")} if tr else None),
            "fed": {k: kl.get(k) for k in ("event", "days_to_meeting", "modal_level", "p_up", "p_down", "expected_rate")} if kl else None,
            "cftc_pctl_3y": cf_ or None, "dex_vol_chg_7d": (ll.get("dex") or {}).get("chg_7d"), "bn": (d("bn_daily").get("agg") or None),
            "okx_btc": (d("okx_flow").get("BTC") or None)}


def _key_status(h):
    if not h:
        return "nepoznato"
    e = h.get("last_error")
    if not e:
        return "radi (poslednji uspeh %s)" % (h.get("last_ok_utc") or "-")
    return "ceka kljuc" if "nema kljuca" in str(e) else "greska: %s" % e


def compact_history(rows, now_ms):
    """Satni redovi za poslednjih HOURLY_ROWS sati, a starije jedan red po danu (poslednji u danu): istorija ostaje mala, a z-skorovi dugi."""
    rows = sorted(rows, key=lambda r: r.get("t", 0))
    cut = (now_ms // HOUR) * HOUR - HOURLY_ROWS * HOUR
    old, recent = [r for r in rows if r.get("t", 0) < cut], [r for r in rows if r.get("t", 0) >= cut]
    daily = {}
    for r in old:
        daily[iso(r["t"])[:10]] = r  # poslednji red tog dana pobedjuje
    return list(daily.values())[-(HISTORY_KEEP // 24):] + recent


def build_briefing(files, z, now_ms, registry=None, health=None, n_features=None, evidence=None):
    cal = (files.get("calendar") or {}).get("data", {})
    mk = (files.get("market") or {}).get("data", {})
    uni = (files.get("universe") or {}).get("data", {})
    extremes = {k: v for k, v in z.items() if abs(v) >= 2.0}
    cost = {}
    for s, row in mk.items():
        b = (row or {}).get("book")
        if b and b.get("slip_buy_bps", {}).get("120") is not None:
            cost[s] = {"spread_bps": b["spread_bps"], "slip120_bps": b["slip_buy_bps"]["120"]}
    worst = dict(sorted(cost.items(), key=lambda kv: -(kv[1]["spread_bps"] + kv[1]["slip120_bps"]))[:8])
    bf = {"updated_utc": iso(now_ms), "regime": regime(files), "scalars": scalars(files), "extremes_z>=2": extremes,
          "calendar_next_72h": (cal.get("events") or [])[:12], "earnings_next_14d": cal.get("earnings", {}),
          "smart_money_top": dict(list(((files.get("smart_money") or {}).get("data", {}).get("coins") or {}).items())[:8]),
          "macro": {k: v for k, v in ((files.get("macro") or {}).get("data", {}).get("yahoo") or {}).items() if v},
          "sentiment": (files.get("sentiment") or {}).get("data", {}), "costliest_to_trade": worst,
          "universe_liquid_n": len(uni.get("liquid", [])) if isinstance(uni, dict) else None,
          "registry": registry or {}, "source_health_failing": {k: v["last_error"] for k, v in (health or {}).items() if v.get("last_error")},
          "key_sources": {"coinalyze": _key_status((health or {}).get("derivs_coinalyze")), "finnhub": cal.get("finnhub") or "nepoznato"},
          "n_features": n_features, "extra": extra_block(files), "evidence": evidence}
    raw = json.dumps(bf, ensure_ascii=False, separators=(",", ":"))
    if len(raw.encode("utf-8")) > BRIEFING_MAX_BYTES:  # skrati najvece sekcije, nikad ne seci usred JSON-a
        bf["extra"] = {k: v for k, v in bf["extra"].items() if k in ("fed",)}
        if bf.get("evidence"):
            bf["evidence"] = dict(bf["evidence"], findings=bf["evidence"].get("findings", [])[:6])
        bf["sentiment"] = {k: v for k, v in bf["sentiment"].items() if k != "wiki_attention"}
        bf["macro"] = dict(list(bf["macro"].items())[:8])
        bf["smart_money_top"] = dict(list(bf["smart_money_top"].items())[:4])
    return bf


def _evidence():
    """Dokazi iz studija (rezim + Trump) za AI; svaka studija zasebno, nedostaje = izostavljena."""
    ev = _load(os.path.join(ROOT, "config", "evidence.json"), None)
    tev = _load(os.path.join(ROOT, "config", "events_evidence.json"), None)
    if tev:
        ev = dict(ev or {}, trump=tev)
    return ev


def registry_summary(state_dir):
    p = _load(os.path.join(state_dir, "lab", "panel.json"), {})
    if not p:
        return {}
    return {"live": [{"id": x["id"], "bt_t": (x.get("bt") or {}).get("t"), "bt_verdict": (x.get("bt") or {}).get("verdict"),
                      "fwd_n": (x.get("fwd") or {}).get("n", 0), "fwd_mean": (x.get("fwd") or {}).get("mean")} for x in p.get("live", [])],
            "backtest_counts": p.get("backtest_counts"), "placebo_hourly_bt": ((p.get("placebo") or {}).get("hourly_bt") or {}).get("mean"),
            "demoted": p.get("demoted")}


def run(state_dir, now_ms=None, force=False, log=print, env=None):
    env = os.environ if env is None else env
    now_ms = now_ms or int(time.time() * 1000)
    data_dir = os.path.join(state_dir, "data")
    meta = _load(os.path.join(data_dir, "meta.json"), {})
    health = _load(os.path.join(data_dir, "health.json"), {})
    for k in RETIRED:  # izvori koji vise ne rade ne smeju da ostanu kao lazna greska u zdravlju
        health.pop(k, None)
    cfg, _ = backtest.load_config()
    syms = [u["sym"] for u in cfg["universe"]]
    stocks = [s for s in syms if s.startswith("xyz:")]
    files = {n: _load(os.path.join(data_dir, n + ".json"), None) for n in ("market", "derivs", "macro", "sentiment", "calendar", "smart_money", "universe",
                                                                         "cftc", "llama", "kalshi", "okx_flow", "bn_daily", "onchain", "gdelt", "trump")}
    # novi kljuc (Coinalyze) ne ceka sledeci sat: ako je zadnja greska bila "nema kljuca", a kljuc sada postoji, odmah ponovo
    key_just_added = bool(env.get("COINALYZE_API_KEY")) and "nema kljuca" in str((health.get("derivs_coinalyze") or {}).get("last_error") or "")
    hourly = force or key_just_added or due(meta, "market", now_ms, HOUR)
    four_h = force or due(meta, "smart_money", now_ms, 4 * HOUR)
    daily_new = force or due(meta, "sentiment", now_ms, daily=True)
    ctx_cache = {}

    def get_ctx():
        if "c" not in ctx_cache:
            ctx_cache["c"] = C.hl_contexts()
        return ctx_cache["c"]

    if hourly or daily_new:  # univerzum: dnevno (point-in-time), a kontekst treba i za knjige
        if force or due(meta, "universe", now_ms, daily=True):
            files["universe"] = run_task("universe", lambda: {"liquid": C.liquid_universe(get_ctx())}, data_dir, meta, health, now_ms, log)
    if hourly:
        liquid = [r["sym"] for r in ((files.get("universe") or {}).get("data", {}) or {}).get("liquid", [])]
        book_syms = list(dict.fromkeys(syms + liquid))
        files["market"] = run_task("market", lambda: C.collect_market(book_syms, get_ctx()), data_dir, meta, health, now_ms, log)

        def derivs():
            out = {}
            for name, fn in (("deribit", lambda: C.collect_deribit(now_ms)), ("okx_lsr", C.collect_okx_lsr),
                             ("coinalyze", lambda: C.collect_coinalyze(env.get("COINALYZE_API_KEY"), now_ms))):
                try:
                    out[name] = fn()
                    health.setdefault("derivs_" + name, {})
                    health["derivs_" + name].update(last_ok_utc=iso(now_ms), last_error=None)
                except Exception as e:  # noqa: BLE001
                    out[name] = None
                    health.setdefault("derivs_" + name, {})["last_error"] = "%s: %s" % (type(e).__name__, e)
            return out
        files["derivs"] = run_task("derivs", derivs, data_dir, meta, health, now_ms, log)
        yahoo = run_task("macro_yahoo", C.collect_yahoo, data_dir, meta, health, now_ms, log)
        files["calendar"] = run_task("calendar", lambda: C.collect_calendar(now_ms, stocks, env.get("FINNHUB_API_KEY")), data_dir, meta, health, now_ms, log)
        files["okx_flow"] = run_task("okx_flow", C2.collect_okx_flow, data_dir, meta, health, now_ms, log)
        files["kalshi"] = run_task("kalshi", lambda: C2.collect_kalshi_fed(now_ms), data_dir, meta, health, now_ms, log)
        tr_inst = list(trump.load_lexicon()["raw"]["instruments"].values())
        mk0 = (files.get("market") or {}).get("data", {}) or {}
        tr_marks = {s: mk0[s]["ctx"]["mark"] for s in tr_inst if mk0.get(s) and mk0[s].get("ctx") and mk0[s]["ctx"].get("mark")}
        files["trump"] = run_task("trump", lambda: trump.collect_trump(now_ms, store_path=os.path.join(data_dir, "trump_events.json"), instruments=tr_inst, marks=tr_marks),
                                  data_dir, meta, health, now_ms, log)
    else:
        yahoo = _load(os.path.join(data_dir, "macro_yahoo.json"), None)
    fred = None
    if force or due(meta, "macro_fred", now_ms, daily=True):
        fred = run_task("macro_fred", C.collect_fred, data_dir, meta, health, now_ms, log)
    else:
        fred = _load(os.path.join(data_dir, "macro_fred.json"), None)
    macro = {"yahoo": (yahoo or {}).get("data"), "fred": (fred or {}).get("data")}
    files["macro"] = {"updated_utc": iso(now_ms), "data": macro}
    _save(os.path.join(data_dir, "macro.json"), files["macro"])
    if daily_new:
        files["sentiment"] = run_task("sentiment", lambda: C.collect_sentiment(now_ms), data_dir, meta, health, now_ms, log)
    if four_h:
        files["smart_money"] = run_task("smart_money", lambda: C.collect_smart_money(syms), data_dir, meta, health, now_ms, log)
    # novi izvori (v2): svaki sa sopstvenim ritmom, greska jednog nikad ne smeta ostalima
    bn_syms = {x: bb.bn_symbol(x) for x in syms if not x.startswith("xyz:") and bb.bn_symbol(x)}
    for name, every, fn in (("llama", 6 * HOUR, lambda: C2.collect_llama_activity(now_ms)),
                            ("bn_daily", 6 * HOUR, lambda: C2.collect_binance_daily(bn_syms, os.path.join(data_dir, "bn_raw.json"), now_ms)),
                            ("cftc", None, lambda: C2.collect_cftc(now_ms)), ("onchain", None, lambda: C2.collect_onchain(now_ms))):  # GDELT izbacen: stalno 429 sa Actions adresa
        tried = meta.setdefault("tried", {})
        if force or ((due(meta, name, now_ms, every) if every else due(meta, name, now_ms, daily=True)) and now_ms - tried.get(name, 0) >= RETRY_MS):
            tried[name] = now_ms  # neuspeh se ponavlja najranije posle 3 h (ne svakih 5 minuta)
            files[name] = run_task(name, fn, data_dir, meta, health, now_ms, log)
    # istorija skalara (jedan red po satu) i z-skorovi
    hist_path = os.path.join(data_dir, "history.json")
    hist = _load(hist_path, [])
    feats, fmeta = featstore.flatten(files, scalars(files), now_ms)
    row = dict(feats, t=(now_ms // HOUR) * HOUR)
    mk = (files.get("market") or {}).get("data", {}) or {}
    # cene (marks) univerzuma po satu: sluze za ocenjivanje AI prognoza bez ikakvog dodatnog poziva
    row["m"] = {s: round(mk[s]["ctx"]["mark"], 6) for s in syms if mk.get(s) and mk[s].get("ctx")}
    prior = [h for h in hist if h.get("t") != row["t"]]
    z = zscores({k: v for k, v in row.items() if k not in ("t", "m")}, prior)
    hist = compact_history(prior + [row], now_ms)
    _save(hist_path, hist)
    _save(os.path.join(data_dir, "features.json"), {"updated_utc": iso(now_ms), "n": len(feats), "features": {k: {"v": v, "z": z.get(k)} for k, v in feats.items()}, "meta": fmeta})
    inst_feats = featstore.instrument_features(mk)
    _save(os.path.join(data_dir, "instrument_features.json"), {"updated_utc": iso(now_ms), "instruments": inst_feats})
    try:  # panel (instrument x sat) za model; greska ovde nikad ne sme da obori skupljanje
        if hourly or force:
            panelstore.append_hour(state_dir, row["t"], feats, inst_feats, row["m"])
        if force or due(meta, "panel_scan", now_ms, 6 * HOUR):
            _save(os.path.join(state_dir, "lab", "panel_scan.json"), panel_scan.run(state_dir))
            meta.setdefault("last", {})["panel_scan"] = now_ms
        health.setdefault("panel", {"last_ok_utc": None, "last_error": None, "consecutive_failures": 0}).update(last_ok_utc=iso(now_ms), last_error=None, consecutive_failures=0)
    except Exception as e:  # noqa: BLE001
        h_ = health.setdefault("panel", {"last_ok_utc": None, "last_error": None, "consecutive_failures": 0})
        h_["last_error"] = "%s: %s" % (type(e).__name__, e)
        h_["consecutive_failures"] = h_.get("consecutive_failures", 0) + 1
        log("panel nije upisan: %s" % h_["last_error"])
    briefing = build_briefing(files, z, now_ms, registry_summary(state_dir), health, n_features=len(feats), evidence=_evidence())
    _save(os.path.join(data_dir, "briefing.json"), briefing)
    _save(os.path.join(data_dir, "health.json"), health)
    _save(os.path.join(data_dir, "meta.json"), meta)
    return {"ok": True, "hourly": hourly, "four_hourly": four_h, "daily": daily_new, "failing": [k for k, v in health.items() if v.get("last_error")]}


def main():
    argv = sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        res = run(state, force="--force" in argv)
    except Exception as e:  # noqa: BLE001  # kolektori nikad ne smeju da obore stražu
        res = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
