"""Hodanje unapred: svaki sat, istim motorom kao istorijska provera, beleži signale i njihove ishode u realnom vremenu.
Bez AI-ja i bez novca. Nema ruckog stanja: sve se racuna iznova iz svezih svecnih podataka (ishodi su tacne cene zatvaranja),
a pamti se samo T0 (trenutak od kog signal racuna kao 'unapred', ne kao istorija). Radi unutar workflow-a straze.
Izlaz u <state>/lab/: stats.json (sve za panel), triggers.json (signali poslednje zatvorene svece za Istrazivaca), meta.json, daily.json.
Upotreba: python -m lab.forward --state _state [--force]"""
import json
import os
import sys
import time

from . import backtest, data, rules, sim, stats
from .indicators import Series

HOUR = 3600000
DAY = 86400000
WARM = 205
HOLD_HOURS_1H = 24
HOLD_HOURS_1D = 168


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
    return {x["id"]: int(x.get("hold_hours", HOLD_HOURS_1H)) for x in cfg.get("live_variants", [])}


def build_forward_series(cfg, days, interval, with_funding, log):
    series = {}
    for u in cfg["universe"]:
        try:
            cs = data.fetch_candles(u["hl"], days, interval=interval)
        except Exception as e:  # noqa: BLE001
            log("preskacem %s: %s" % (u["sym"], type(e).__name__))
            continue
        if len(cs) < WARM + 5:
            continue
        fund = None
        if with_funding:
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


def evaluate_forward(series, ctx, sigs, horizons, with_x):
    """Isti testovi kao u backtest-u, samo nad signalima posle T0. Vraca {test: lista (t, ret%, sym)}."""
    return backtest.evaluate(series, sigs, horizons, with_x, ctx["bench"])


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
        ev = evaluate_forward(series, ctx, sigs, horizons, not daily)
        tests = {name: summarize_rows(rows) for name, rows in ev.items() if rows}
        out_vars[vid] = {"family": fam, "params": params, "interval": interval, "signals": len(sigs), "tests": tests,
                         "live": vid in live}
        for sym, i, t, side in signals_since(series, ctx, fam, params, t0, last_only=True):
            S = series[sym]
            hold = live.get(vid, HOLD_HOURS_1D if daily else HOLD_HOURS_1H)
            triggers.append(dict(trigger_row(S, i, vid, fam, side, hold, daily), live=vid in live))
    last_bar = max(S.t[-1] for S in series.values())
    return out_vars, triggers, last_bar, len(series)


def governor(cfg, all_vars):
    """Automatsko gasenje zivih varijanti koje unapred jasno gube. Samo smanjuje rizik; ukljucivanje ide iskljucivo kroz config/lab.json."""
    g = cfg.get("governor", {})
    min_n, tmax = int(g.get("min_n", 30)), float(g.get("t_naive_max", -2.0))
    out = {}
    for x in cfg.get("live_variants", []):
        v = all_vars.get(x["id"])
        if not v:
            continue
        key = "E7" if v.get("interval") == "1d" else "E24"
        s = v.get("tests", {}).get(key, {})
        if s.get("n", 0) >= min_n and s.get("t_naive") is not None and s["t_naive"] <= tmax and s.get("mean", 0) < 0:
            out[x["id"]] = {"n": s["n"], "mean": s["mean"], "t_naive": s["t_naive"], "test": key}
    return out


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
    if meta.get("last_bar") == bar_now and not force:
        return {"ok": True, "skipped": "nova svecu jos nema"}
    t0 = meta["t0_ms"]
    variants, triggers, last_bar, n_sym = run_interval(cfg, cands, t0, now_ms, "1h", log)
    # dnevna pravila: jednom po UTC danu (posle zatvaranja dnevne svece u 00:00)
    day_key = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000.0))
    daily = _load(os.path.join(lab_dir, "daily.json"), {})
    if daily.get("asof") != day_key or force:
        try:
            dv, dt, dlast, dn = run_interval(cfg, cands, t0, now_ms, "1d", log)
            daily = {"asof": day_key, "variants": dv, "triggers": dt, "last_bar": dlast, "n": dn}
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
    _save(os.path.join(lab_dir, "stats.json"), stats_obj)
    live_triggers = [x for x in all_triggers if x.get("live")]
    _save(os.path.join(lab_dir, "triggers.json"), {"updated_utc": iso(now_ms), "bar_utc": iso(last_bar), "triggers": live_triggers,
                                                   "other_triggers": len(all_triggers) - len(live_triggers), "live_variants": live})
    meta["last_bar"] = bar_now
    meta["updated_utc"] = iso(now_ms)
    _save(os.path.join(lab_dir, "meta.json"), meta)
    return {"ok": True, "signals": totals["signals"], "triggers": len(all_triggers), "live_triggers": len(live_triggers),
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
