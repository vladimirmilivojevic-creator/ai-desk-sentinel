"""Hodanje unapred: svaki sat, istim motorom kao istorijska provera, beleži signale i njihove ishode u realnom vremenu.
Bez AI-ja i bez novca. Nema ruckog stanja: sve se racuna iznova iz svezih svecnih podataka (ishodi su tacne cene zatvaranja),
a pamti se samo T0 (trenutak od kog signal racuna kao 'unapred', ne kao istorija). Radi unutar workflow-a straze.
Izlaz u <state>/lab/: stats.json (sve za panel), triggers.json (signali poslednje zatvorene svece za Istrazivaca), meta.json, daily.json.
Upotreba: python -m lab.forward --state _state [--force]"""
import json
import os
import sys
import time

from . import backtest, data, features, rules, sim, stats
from .indicators import Series

HOUR = 3600000
DAY = 86400000
WARM = 205
REV = 8  # povecaj kad se promeni izlaz/logika: laboratorija se tada odmah ponovo racuna u istom satu
HOLD_HOURS_1H = 24
HOLD_HOURS_1D = 168
PROOF_TARGET = 300  # unapred upisano 2026-10-14: najmanje 300 simuliranih trejdova po pravilu pre nego sto se rezultat smatra dokazom (simulacija: 280-700 za t=2 pri prednosti 0,3%)
SHADOW_BUDGET_S = 120  # senka (dodatni instrumenti) sme najvise toliko da traje; zivi deo se tada vec zavrsio i sacuvao


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


def live_config(cfg):
    """Dozvoljene (zive) varijante za Istrazivaca: {id: hold_hours}. Menja se samo u config/lab.json."""
    return {x["id"]: int(x.get("hold_hours", HOLD_HOURS_1H)) for x in cfg.get("live_variants", []) if not x.get("paused")}


def build_forward_series(cfg, days, interval, with_funding, log, deadline=None):
    series = {}
    for u in cfg["universe"]:
        if deadline is not None and time.monotonic() > deadline:
            log("vremenski budzet potrosen posle %d instrumenata" % len(series))
            break
        try:
            cs = data.fetch_candles(u["hl"], days, interval=interval)
        except Exception as e:  # noqa: BLE001
            log("preskacem %s: %s" % (u["sym"], type(e).__name__))
            continue
        if len(cs) < WARM + 5:
            continue
        fund = None
        if with_funding and u.get("funding", True):
            try:
                fund = data.fetch_funding(u["hl"], days)
            except Exception:  # noqa: BLE001
                fund = None
        series[u["sym"]] = Series(cs, fund, sym=u["sym"], group=u["group"], cls=u["cls"])
    return series


def signals_since(series, ctx, fam, params, t0, last_only=False):
    """Signali (sym, i, t, side) od T0 pa nadalje, ukljucujuci poslednju zatvorenu svecu."""
    fn = rules.FAMILIES[fam]
    out = []
    for sym, S in sorted(series.items()):
        start = max(WARM, 1)
        for i in range(start, S.n):
            if S.t[i] < t0:
                continue
            if last_only and i != S.n - 1:
                continue
            side = fn(S, i, ctx, **params)
            if side:
                out.append((sym, i, S.t[i], side))
    return out


def evaluate_forward(series, ctx, sigs, horizons, with_x, x_daily=False):
    """Isti testovi kao u backtest-u, samo nad signalima posle T0. Vraca {test: lista (t, ret%, sym)}."""
    return backtest.evaluate(series, sigs, horizons, with_x, ctx["bench"], x_daily=x_daily)


def summarize_rows(rows):
    """n, srednja, pobede; t po danima samo kad ima bar 10 dana (inace None, jer je premalo nezavisnih dana);
    t_naive racuna svaki trejd kao nezavisan (ZANEMARUJE korelaciju instrumenata, pa PRECENJUJE sigurnost: samo okvirno)."""
    if not rows:
        return {"n": 0}
    rets = [r for _, r, _ in rows]
    n = len(rets)
    mean = sum(rets) / n
    d = stats.daily_t([(t, r) for t, r, _ in rows])
    t_naive = None
    if n >= 3:
        var = sum((x - mean) ** 2 for x in rets) / (n - 1)
        if var > 0:
            t_naive = round(mean / ((var / n) ** 0.5), 2)
    return {"n": n, "mean": round(mean, 4), "win": round(100.0 * sum(1 for x in rets if x > 0) / n, 1), "days": d["days"],
            "t": d["t"] if d["days"] >= 10 else None, "t_naive": t_naive}


def trigger_row(S, i, vid, fam, side, hold, daily):
    sp = sim.stop_pct_for(S, i, S.cls)
    if daily:
        a = S.atr_pct[i]
        sp = None if a is None else round(min(max(2.5 * a * 100.0, 3.0), 12.0), 2)
    tpm = 3.0 if daily else sim.TP_MULT
    return {"variant": vid, "family": fam, "sym": S.sym, "group": S.group, "cls": S.cls, "side": side,
            "px": S.c[i], "bar_utc": iso(S.t[i]), "stop_pct": sp, "tp_pct": None if sp is None else round(sp * tpm, 2),
            "hold_hours": hold, "interval": "1d" if daily else "1h"}


def run_interval(cfg, cands, t0, now_ms, interval, log):
    daily = interval == "1d"
    days = 420 if daily else int(min(60, max(14, (now_ms - t0) / DAY + 12)))
    series = build_forward_series(cfg, days, interval, with_funding=not daily, log=log)
    if len(series) < 5:
        raise RuntimeError("premalo instrumenata (%d)" % len(series))
    horizons = (1, 3, 7) if daily else backtest.HORIZONS
    ctx = backtest.make_ctx(series, horizons)
    variants = rules.daily_variants() if daily else rules.default_variants() + rules.candidate_variants(cands)
    live = live_config(cfg)
    out_vars, triggers = {}, []
    for vid, fam, params in variants:
        sigs = signals_since(series, ctx, fam, params, t0)
        ev = evaluate_forward(series, ctx, sigs, horizons, not daily, x_daily=daily)
        tests = {name: summarize_rows(rows) for name, rows in ev.items() if rows}
        out_vars[vid] = {"family": fam, "params": params, "interval": interval, "signals": len(sigs), "tests": tests,
                         "live": vid in live}
        for sym, i, t, side in signals_since(series, ctx, fam, params, 0, last_only=True):
            S = series[sym]
            hold = live.get(vid, HOLD_HOURS_1D if daily else HOLD_HOURS_1H)
            triggers.append(dict(trigger_row(S, i, vid, fam, side, hold, daily), live=vid in live))
    last_bar = max(S.t[-1] for S in series.values())
    marks = {sym: S.c[-1] for sym, S in series.items()}
    return out_vars, triggers, last_bar, len(series), marks


def shadow_instruments(cfg, root):
    """Dodatni instrumenti koji NISU u zivom univerzumu (config/lab.json 'shadow_universe': {file, max} ili {instruments}): za njih se samo
    belezi sta bi pravila radila (signali i ishodi), a Istrazivac ih ne trguje dok se ne dodaju i u njegovu tabelu."""
    sh = cfg.get("shadow_universe")
    if not sh:
        return []
    items = sh.get("instruments")
    if items is None:
        items = _load(os.path.join(root, sh.get("file", "config/lab_v3.json")), {}).get("universe", [])
    live = {u["sym"] for u in cfg["universe"]}
    return [u for u in items if u["sym"] not in live][:int(sh.get("max", 80))]


def run_shadow(cfg, cands, root, t0, now_ms, log, deadline):
    """Satna pravila na dodatnim instrumentima: isti motor, samo senka. BTC se uzima zbog konteksta (BTCLEAD), a njegovi signali se ne racunaju.
    Vraca {instruments, syms, variants} ili None kad nema dodatnih instrumenata. Nikad ne dira zive fajlove."""
    extra = shadow_instruments(cfg, root)
    if not extra:
        return None
    days = int(min(60, max(14, (now_ms - t0) / DAY + 12)))
    series = build_forward_series(dict(cfg, universe=extra), days, "1h", with_funding=False, log=log, deadline=deadline)
    ext_syms = set(series)
    if len(ext_syms) < 5:
        return {"instruments": len(ext_syms), "syms": sorted(ext_syms), "variants": {}}
    btc = [u for u in cfg["universe"] if u["sym"] == "BTC"]
    if btc and "BTC" not in series:
        series.update(build_forward_series(dict(cfg, universe=btc), days, "1h", with_funding=False, log=log))
    ctx = backtest.make_ctx(series, backtest.HORIZONS)
    out = {}
    for vid, fam, params in rules.default_variants() + rules.candidate_variants(cands):
        try:
            sigs = [x for x in signals_since(series, ctx, fam, params, t0) if x[0] in ext_syms]
            ev = evaluate_forward(series, ctx, sigs, backtest.HORIZONS, True)
            out[vid] = {"signals": len(sigs), "tests": {name: summarize_rows([r for r in rows if r[2] in ext_syms]) for name, rows in ev.items() if rows}}
        except Exception as e:  # noqa: BLE001  # jedna varijanta bez konteksta (npr. fonding) ne sme da obori ostale
            log("senka: varijanta %s preskocena (%s)" % (vid, type(e).__name__))
    return {"instruments": len(ext_syms), "syms": sorted(ext_syms), "variants": out}


def governor(cfg, all_vars):
    """Automatsko gasenje zivih varijanti: (1) istorijski gubitnik (t preko korpe <= bt_t_known_loser): trgovanje njime ne daje novu
    informaciju; (2) unapred jasno gubi (bar min_n ishoda, naivno t <= t_naive_max, negativna sredina). Samo smanjuje rizik;
    ukljucivanje ide iskljucivo kroz config/lab.json."""
    g = cfg.get("governor", {})
    min_n, tmax = int(g.get("min_n", 30)), float(g.get("t_naive_max", -2.0))
    loser = g.get("bt_t_known_loser")
    out = {}
    for x in cfg.get("live_variants", []):
        if x.get("paused"):
            continue
        v = all_vars.get(x["id"])
        if not v:
            continue
        key = "E7" if v.get("interval") == "1d" else "E24"
        b = v.get("backtest", {}).get(key, {})
        if loser is not None and b.get("t") is not None and b["t"] <= float(loser):
            out[x["id"]] = {"reason": "istorija jasno gubi", "bt_t": b["t"], "test": key}
            continue
        s = v.get("tests", {}).get(key, {})
        if s.get("n", 0) >= min_n and s.get("t_naive") is not None and s["t_naive"] <= tmax and s.get("mean", 0) < 0:
            out[x["id"]] = {"reason": "unapred jasno gubi", "n": s["n"], "mean": s["mean"], "t_naive": s["t_naive"], "test": key}
    return out


def history_point(bar_ms, all_vars, live_ids):
    """Tacka za grafik napretka: [vreme, signala, ishoda +24h, n zivih pravila, tezinska srednja zivih %, srednja placeba %]."""
    n_tot, w = 0, 0.0
    for vid in live_ids:
        v = all_vars.get(vid, {})
        s = v.get("tests", {}).get("E7" if v.get("interval") == "1d" else "E24", {})
        if s.get("n"):
            n_tot += s["n"]
            w += s["n"] * s["mean"]
    pl = all_vars.get("PLACEBO_p2", {}).get("tests", {}).get("E24", {})
    tot = sum(v["signals"] for v in all_vars.values())
    out24 = sum(v["tests"].get("H24", {}).get("n", 0) for v in all_vars.values() if v.get("interval") == "1h")
    return [bar_ms, tot, out24, n_tot, round(w / n_tot, 4) if n_tot else None, pl.get("mean")]


def proof_rows(cfg, all_vars, hours_running, limit=16):
    """Napredak ka dokazu po pravilu: koliko je simuliranih trejdova (sa stopom, ciljem i troskom: X24 satna, X7 dnevna pravila) vec izmereno unapred
    prema cilju PROOF_TARGET, srednji rezultat, t (po danima kad ima bar 10 dana, inace naivno) i procena dana do cilja pri sadasnjem tempu.
    Zivi i pauzirana pravila prvo, pa ostala po n; placebo ostaje kao poredjenje. Simulirani trejdovi istog dana nisu nezavisni: zato se broji t po danima.
    Visak prema korpi (E24 satna, E7 dnevna pravila, ista duzina drzanja): srednji rezultat bez smera trzista. `beta` = sirovi rezultat pozitivan a visak nula ili
    negativan, to jest dobit je samo smer trzista (2026-10-14: BB_follow X24 +0,58% a E24 -0,02% jer je trziste padalo)."""
    target = int(cfg.get("proof_target", PROOF_TARGET))
    live = set(live_config(cfg))
    paused = {x["id"] for x in cfg.get("live_variants", []) if x.get("paused")}
    days = max(hours_running / 24.0, 1e-9)
    rows = []
    for vid, v in all_vars.items():
        key = "X7" if v.get("interval") == "1d" else "X24"
        s = (v.get("tests") or {}).get(key) or {}
        n = s.get("n", 0)
        if not n:
            continue
        rate = n / days
        eta = None if n >= target or rate <= 0 else int(-(-(target - n) // rate))
        e = (v.get("tests") or {}).get("E7" if v.get("interval") == "1d" else "E24") or {}
        em = e.get("mean") if e.get("n") else None
        rows.append({"id": vid, "test": key, "n": n, "mean": s.get("mean"), "t": s.get("t") if s.get("t") is not None else s.get("t_naive"),
                     "t_days": s.get("t") is not None, "days": s.get("days"), "pct": round(100.0 * min(1.0, n / target), 1), "eta_days": eta,
                     "e_mean": em, "e_t": (e.get("t") if e.get("t") is not None else e.get("t_naive")) if em is not None else None, "e_t_days": e.get("t") is not None,
                     "beta": bool(em is not None and (s.get("mean") or 0) > 0 and em <= 0),
                     "status": "ziva" if vid in live else ("pauzirana" if vid in paused else ("placebo" if "PLACEBO" in vid else "merena"))})
    order = {"ziva": 0, "pauzirana": 1, "placebo": 2, "merena": 3}
    rows.sort(key=lambda r: (order[r["status"]], -r["n"]))
    return {"target": target, "rows": rows[:limit]}


def panel_summary(cfg, stats_obj, bt, history=None, registry=None):
    """Mali sazetak (nekoliko KB) za panel: zive varijante, najbolji istorijski dokazi, placebo, grafik napretka i brojke unapred."""
    why = {x["id"]: x.get("why", "") for x in cfg.get("live_variants", [])}
    all_vars = stats_obj["variants"]
    live = []
    for vid, hold in sorted(live_config(cfg).items()):
        v = all_vars.get(vid, {})
        key = "E7" if v.get("interval") == "1d" else "E24"
        live.append({"id": vid, "hold_hours": hold, "why": why.get(vid, ""), "bt": v.get("backtest", {}).get(key, {}),
                     "fwd": v.get("tests", {}).get(key, {}), "signals": v.get("signals", 0), "test": key})
    ranked = []
    for vid, tests in bt.items():
        if "PLACEBO" in vid:
            continue
        for test, r in tests.items():
            if test.startswith("E") and r.get("t") is not None and r.get("n", 0) >= 30:
                ranked.append({"id": vid, "test": test, "n": r["n"], "mean": r["mean"], "t": r["t"], "t_train": r.get("t_train"),
                               "t_test": r.get("t_test"), "verdict": r["verdict"]})
    ranked.sort(key=lambda x: -x["t"])
    counts = {}
    for r in ranked:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    placebo = {"hourly_bt": bt.get("PLACEBO_p2", {}).get("E24"), "hourly_fwd": all_vars.get("PLACEBO_p2", {}).get("tests", {}).get("E24"),
               "daily_bt": bt.get("D_PLACEBO_p5", {}).get("E7")}
    return {"updated_utc": stats_obj["updated_utc"], "t0_utc": stats_obj["t0_utc"], "hours_running": stats_obj["hours_running"],
            "universe_n": stats_obj["universe_n"], "totals": stats_obj["totals"], "cost_pct": stats_obj["cost_pct"], "live": live,
            "top_backtest": ranked[:10], "backtest_counts": counts, "demoted": stats_obj.get("demoted", {}), "placebo": placebo,
            "history": (history or [])[-168:], "features_rows": stats_obj.get("features_rows"), "registry": registry,
            "proof": proof_rows(cfg, all_vars, stats_obj.get("hours_running") or 0.0)}


def load_backtest_summary(root):
    """Sazetak istorijskih rezultata (calibration/lab_backtest_*.json) po varijanti i testu, za panel i Istrazivaca."""
    out = {}
    for name in ("1h", "1d"):
        res = _load(os.path.join(root, "calibration", "lab_backtest_%s.json" % name), None)
        if not res:
            continue
        for r in res.get("results", []):
            s = r["stats"]
            if s.get("n", 0) < 1:
                continue
            out.setdefault(r["id"], {})[r["test"]] = {"n": s["n"], "mean": s["mean"], "t": s["all"].get("t"),
                                                       "t_train": s["train"].get("t"), "t_test": s["test"].get("t"),
                                                       "verdict": r["verdict"]}
    return out


def run(state_dir, root=None, now_ms=None, force=False, log=print):
    root = root or backtest.ROOT
    now_ms = now_ms or int(time.time() * 1000)
    cfg, cands = backtest.load_config()
    lab_dir = os.path.join(state_dir, "lab")
    meta = _load(os.path.join(lab_dir, "meta.json"), {})
    bar_now = (now_ms // HOUR) * HOUR - HOUR  # otvaranje poslednje zatvorene satne svece
    if not meta.get("t0_ms"):
        meta["t0_ms"] = (now_ms // HOUR) * HOUR
        meta["t0_utc"] = iso(meta["t0_ms"])
    if meta.get("last_bar") == bar_now and meta.get("rev") == REV and not force:
        return {"ok": True, "skipped": "nova svecu jos nema"}
    t0 = meta["t0_ms"]
    variants, triggers, last_bar, n_sym, marks = run_interval(cfg, cands, t0, now_ms, "1h", log)
    # dnevna pravila: jednom po UTC danu (posle zatvaranja dnevne svece u 00:00)
    day_key = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000.0))
    daily = _load(os.path.join(lab_dir, "daily.json"), {})
    if daily.get("asof") != day_key or daily.get("rev") != REV or force:
        try:
            dv, dt, dlast, dn, _ = run_interval(cfg, cands, t0, now_ms, "1d", log)
            daily = {"asof": day_key, "rev": REV, "variants": dv, "triggers": dt, "last_bar": dlast, "n": dn}
            _save(os.path.join(lab_dir, "daily.json"), daily)
        except Exception as e:  # noqa: BLE001
            log("dnevna pravila nisu uspela: %s" % type(e).__name__)
    all_vars = dict(variants)
    all_vars.update(daily.get("variants", {}))
    bt = load_backtest_summary(root)
    for vid, v in all_vars.items():
        v["backtest"] = bt.get(vid, {})
    live = live_config(cfg)
    demoted = governor(cfg, all_vars)
    for vid in demoted:
        live.pop(vid, None)
        all_vars[vid]["live"] = False
    all_triggers = triggers + daily.get("triggers", [])
    for x in all_triggers:
        v = all_vars.get(x["variant"], {})
        key = "E7" if x["interval"] == "1d" else "E24"
        fw, bt_s = v.get("tests", {}).get(key, {}), v.get("backtest", {}).get(key, {})
        x["live"] = x["live"] and x["variant"] not in demoted
        x["bt_t"], x["bt_mean"], x["bt_verdict"] = bt_s.get("t"), bt_s.get("mean"), bt_s.get("verdict")
        x["fwd_n"], x["fwd_mean"] = fw.get("n", 0), fw.get("mean")
    totals = {"signals": sum(v["signals"] for v in all_vars.values()),
              "outcomes_h24": sum(v["tests"].get("H24", {}).get("n", 0) for v in variants.values()),
              "variants": len(all_vars)}
    stats_obj = {"updated_utc": iso(now_ms), "t0_utc": meta["t0_utc"], "hours_running": round((now_ms - t0) / HOUR, 1),
                 "universe_n": n_sym, "last_bar_utc": iso(last_bar), "variants": all_vars, "totals": totals,
                 "cost_pct": sim.COST_PCT, "live_variants": sorted(live), "demoted": demoted}
    feat_rows = None
    try:
        feat_rows = features.append(os.path.join(lab_dir, "features.jsonl"), features.collect(cfg["universe"], bar_now))
    except Exception as e:  # noqa: BLE001  # dodatni podaci nikad ne smeju da obore laboratoriju
        log("osobine nisu prikupljene: %s" % type(e).__name__)
    stats_obj["features_rows"] = feat_rows
    hist = _load(os.path.join(lab_dir, "history.json"), [])
    if not hist or hist[-1][0] != bar_now:
        hist.append(history_point(bar_now, all_vars, list(live)))
    else:
        hist[-1] = history_point(bar_now, all_vars, list(live))
    hist = hist[-336:]
    _save(os.path.join(lab_dir, "history.json"), hist)
    _save(os.path.join(lab_dir, "stats.json"), stats_obj)
    reg = None
    try:  # registar dokaza je pasivan izlaz: nikad ne menja zive varijante i nikad ne sme da obori laboratoriju
        from . import registry
        cal = os.path.join(root, "calibration")
        reg_rows = registry.load_results([os.path.join(cal, "lab_v3_1d.json"), os.path.join(cal, "lab_v3_1h.json")])
        if reg_rows:
            reg = registry.compact(registry.build(reg_rows, stats_obj), live_ids=set(live))
            _save(os.path.join(lab_dir, "registry.json"), reg)
    except Exception as e:  # noqa: BLE001
        log("registar nije izracunat: %s" % type(e).__name__)
    _save(os.path.join(lab_dir, "panel.json"), panel_summary(cfg, stats_obj, bt, hist, reg))
    live_triggers = [x for x in all_triggers if x.get("live")]
    _save(os.path.join(lab_dir, "triggers.json"), {"updated_utc": iso(now_ms), "bar_utc": iso(last_bar), "triggers": live_triggers,
                                                   "other_triggers": len(all_triggers) - len(live_triggers), "live_variants": live,
                                                   "marks": marks, "marks_bar_utc": iso(last_bar)})
    meta["last_bar"] = bar_now
    meta["rev"] = REV
    meta["updated_utc"] = iso(now_ms)
    _save(os.path.join(lab_dir, "meta.json"), meta)
    n_shadow = None
    try:  # senka dolazi POSLE svega zivog (to je vec sacuvano) i nikad ne sme da obori laboratoriju ni da je uspori preko budzeta
        sh = run_shadow(cfg, cands, root, t0, now_ms, log, time.monotonic() + SHADOW_BUDGET_S)
        if sh is not None:
            sh.update(updated_utc=iso(now_ms), t0_utc=meta["t0_utc"], bar_utc=iso(last_bar))
            _save(os.path.join(lab_dir, "extended.json"), sh)
            n_shadow = sh["instruments"]
    except Exception as e:  # noqa: BLE001
        log("senka nije izracunata: %s" % type(e).__name__)
    return {"ok": True, "shadow_instruments": n_shadow, "signals": totals["signals"], "triggers": len(all_triggers), "live_triggers": len(live_triggers),
            "instruments": n_sym}


def main():
    argv = sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        res = run(state, force="--force" in argv)
    except Exception as e:  # noqa: BLE001  # laboratorija nikad ne sme da obori stražu
        res = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
