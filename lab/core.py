"""Jezgro (senka): sistematski trend-ansambl na velikim kovanicama (config/core.json, pravila upisana unapred).
Za svaku kovanicu i svaki horizont L (14, 28, 56, 112 dana): dugo ako je cena danas iznad cene pre L dana, inace gotovina. Rizik jednak po kovanici
(1 / volatilnost 30 d), ceo portfolio skaliran na ciljanu godisnju volatilnost 20% (procena iz poslednjih 60 dana) i bruto izlozenost najvise 1x kapitala.
Tezine se menjaju jednom nedeljno (svece nedelje, izvrsenje ponedeljkom u 00:00 UTC), signal na zatvaranju svece, prinos od sledeceg dana (bez gledanja unapred).
Konacan portfolio je prosek cetiri horizonta. Trosak: cost_per_side_pct po jedinici prometa.
NE TRGUJE I NE BUDI MOZAK: racuna sta bi drzao i meri unapred od T0 (virtuelno). Cisto stdlib, bez stanja (ceo tok se racuna iz istorije dnevnih sveca),
pa je rezultat ponovljiv. Izlaz: <state>/core/core.json. Upotreba: python -m lab.core --state _state"""
import datetime as dt
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANN = 365


def load_cfg(path=None):
    with open(path or os.path.join(ROOT, "config", "core.json"), encoding="utf-8") as f:
        return json.load(f)


def _std(vals):
    """Uzoracka standardna devijacija (ddof=1); None ako ima manje od 2 vrednosti."""
    n = len(vals)
    if n < 2:
        return None
    m = sum(vals) / n
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))


def build_matrix(rows_by_sym):
    """rows_by_sym: {sym: [(datum 'YYYY-MM-DD', zatvaranje)]} -> (datumi, {sym: lista zatvaranja po datumima, None gde nema svece})."""
    dates = sorted({d for rows in rows_by_sym.values() for d, _ in rows})
    pos = {d: i for i, d in enumerate(dates)}
    px = {}
    for s, rows in rows_by_sym.items():
        col = [None] * len(dates)
        for d, c in rows:
            if c is not None and c > 0:
                col[pos[d]] = float(c)
        px[s] = col
    return dates, px


def pit_eligibility(dates, closes, vols, top_n, win=30, min_hist=120):
    """Univerzum kakav je bio tog dana (bez gledanja unapred): kovanica je 'elig' ako ima bar min_hist dana istorije i spada u top_n po prosecnom dolarskom
    prometu (cena x obim) poslednjih win dana. closes/vols: {sym: lista po datumima, None gde nema}. Ugasene kovanice ostaju do gasenja."""
    n = len(dates)
    syms = list(closes)
    dv = {}
    for s in syms:
        c, v = closes[s], vols[s]
        dv[s] = [(c[i] * v[i]) if (c[i] is not None and v[i] is not None) else None for i in range(n)]
    first = {s: next((i for i, x in enumerate(closes[s]) if x is not None), None) for s in syms}
    elig = {s: [False] * n for s in syms}
    for i in range(n):
        cand = []
        for s in syms:
            if first[s] is None or i - first[s] < min_hist or closes[s][i] is None:
                continue
            w = [x for x in dv[s][max(0, i - win + 1):i + 1] if x is not None]
            if len(w) >= int(win * 0.8):
                cand.append((sum(w) / len(w), s))
        cand.sort(reverse=True)
        for _, s in cand[:top_n]:
            elig[s][i] = True
    return elig


def align_funding(dates, fund_rows):
    """fund_rows: {sym: [(datum 'YYYY-MM-DD', zbir stopa fondinga tog dana kao razlomak)]} -> {sym: lista po datumima, None gde nema}."""
    pos = {d: i for i, d in enumerate(dates)}
    out = {}
    for s, rows in fund_rows.items():
        col = [None] * len(dates)
        for d, v in rows:
            if d in pos and v is not None:
                col[pos[d]] = float(v)
        out[s] = col
    return out


def daily_funding(points):
    """points: [(t_ms, stopa)] -> [(datum UTC, zbir stopa tog dana)]."""
    acc = {}
    for t, v in points:
        d = time.strftime("%Y-%m-%d", time.gmtime(t / 1000.0))
        acc[d] = acc.get(d, 0.0) + float(v)
    return sorted(acc.items())


def _returns(px, n):
    out = {}
    for s, col in px.items():
        r = [None] * n
        for i in range(1, n):
            a, b = col[i - 1], col[i]
            if a is not None and b is not None:
                r[i] = b / a - 1.0
        out[s] = r
    return out


def _raw_weights(px, r, i, L, cfg, long_only, rng=None, elig=None):
    """Neskalirane tezine na zatvaranju dana i: znak(momentum L) / vol30 / broj kovanica sa cenom. Nedostaje li podatak, tezina je 0."""
    syms = list(px)
    ok = (lambda s: px[s][i] is not None and (elig is None or elig[s][i]))
    n_now = sum(1 for s in syms if ok(s))
    out = {s: 0.0 for s in syms}
    if n_now < cfg.get("min_names", 1):
        return out
    vl = cfg["vol_lookback"]
    for s in syms:
        c = px[s]
        if isinstance(L, tuple):  # presek proseka (brzi, spori): signal = brzi prosek iznad sporog
            f_, s_ = L
            wf, ws = c[i - f_ + 1:i + 1] if i >= s_ else [], c[i - s_ + 1:i + 1] if i >= s_ else []
            if not ok(s) or len(ws) < s_ or any(x is None for x in ws):
                continue
            mom = sum(wf) / f_ - sum(ws) / s_
        else:
            if not ok(s) or i < L or c[i - L] is None:
                continue
            mom = c[i] / c[i - L] - 1.0
        if rng is not None:  # placebo: nasumican znak umesto momentuma (samo za kalibraciju studije)
            mom = rng.random() - 0.5
        sig = 1.0 if mom > 0 else (-1.0 if (mom < 0 and not long_only) else 0.0)
        if sig == 0.0 or i - vl + 1 < 1:
            continue
        win = r[s][i - vl + 1:i + 1]
        if any(v is None for v in win):
            continue
        sd = _std(win)
        if not sd:
            continue
        out[s] = sig / (sd * math.sqrt(cfg.get("ann_days", ANN))) / n_now
    return out


def _csm_raw(px, r, i, L, cfg, elig=None):
    """Poredak unutar grupe (market-neutralno): dugo k sa najjacim, kratko k sa najslabijim momentumom L dana, jednake tezine +-0.5/k. Treba bar min_names ponudjenih."""
    syms = list(px)
    vals = []
    for s in syms:
        c = px[s]
        if c[i] is None or i < L or c[i - L] is None or (elig is not None and not elig[s][i]):
            continue
        vals.append((c[i] / c[i - L] - 1.0, s))
    out = {s: 0.0 for s in syms}
    k = cfg.get("csm_k", 6)
    if len(vals) < max(cfg.get("min_names", 1), 2 * k):
        return out
    vals.sort()
    for _, s in vals[:k]:
        out[s] = -0.5 / k
    for _, s in vals[-k:]:
        out[s] = 0.5 / k
    return out


def strategy(px, dates, cfg, L, force=(), cost=None, long_only=None, rng=None, fund=None, elig=None, mode="trend"):
    """Jedan horizont. Vraca dict: net (dnevni neto prinos po danima, razlomak), w (tezine koje se drze posle poslednjeg dana), w_date, sig, gross."""
    n = len(dates)
    syms = list(px)
    cost = cfg["cost_per_side_pct"] / 100.0 if cost is None else cost
    lo = cfg.get("long_only", True) if long_only is None else long_only
    r = _returns(px, n)
    wd = cfg["rebalance_candle_weekday"]
    raw_held = {s: 0.0 for s in syms}
    w_held = {s: 0.0 for s in syms}
    w_prev = dict(w_held)
    g0, net = [], []
    last_rb, sig_now = None, {}
    pvl = cfg["port_vol_lookback"]
    for i in range(n):
        turn = sum(abs(w_held[s] - w_prev[s]) for s in syms)
        fnd = sum(w_held[s] * (fund[s][i] or 0.0) for s in syms if s in fund) if fund else 0.0  # perpetual: duga noga placa fonding, kratka prima
        net.append(sum(w_held[s] * (r[s][i] or 0.0) for s in syms) - turn * cost - fnd)
        g0.append(sum(raw_held[s] * (r[s][i] or 0.0) for s in syms))
        w_prev = dict(w_held)
        d = dates[i]
        if dt.date.fromisoformat(d).weekday() == wd or d in force:
            raw = _raw_weights(px, r, i, L, cfg, lo, rng, elig) if mode == "trend" else _csm_raw(px, r, i, L, cfg, elig)
            sc = 0.0
            if i + 1 >= pvl:
                sd = _std(g0[i - pvl + 1:i + 1])
                sc = cfg["scale_cap"] if not sd else min(cfg["scale_cap"], cfg["target_vol"] / (sd * math.sqrt(cfg.get("ann_days", ANN))))
            w = {s: raw[s] * sc for s in syms}
            gross = sum(abs(v) for v in w.values())
            if gross > cfg["max_gross"]:
                w = {s: v * cfg["max_gross"] / gross for s, v in w.items()}
            raw_held, w_held, last_rb = raw, w, d
            sig_now = {s: (1 if raw[s] > 0 else (-1 if raw[s] < 0 else 0)) for s in syms}
    return {"net": net, "w": w_held, "w_date": last_rb, "sig": sig_now, "gross": sum(abs(v) for v in w_held.values())}


def ensemble(px, dates, cfg, force=(), cost=None, long_only=None, lookbacks=None, rng=None, fund=None, elig=None, mode="trend"):
    """Prosek horizonata (neto prinos i tezine)."""
    Ls = lookbacks or cfg["lookbacks"]
    runs = [strategy(px, dates, cfg, L, force, cost, long_only, rng, fund, elig, mode) for L in Ls]
    n = len(dates)
    net = [sum(x["net"][i] for x in runs) / len(runs) for i in range(n)]
    syms = list(px)
    w = {s: sum(x["w"][s] for x in runs) / len(runs) for s in syms}
    sig = {s: {("L%d" % L if not isinstance(L, tuple) else "MA%d_%d" % L): x["sig"].get(s, 0) for L, x in zip(Ls, runs)} for s in syms}
    return {"net": net, "w": w, "w_date": max((x["w_date"] for x in runs if x["w_date"]), default=None), "sig": sig,
            "gross": sum(abs(v) for v in w.values()), "runs": runs}


def metrics(dates, rets, d_from=None, d_to=None, ann=ANN):
    """Sharpe (godisnji), t, godisnji prinos %, volatilnost %, najveci pad % i ukupan prinos % za prozor [d_from, d_to] (datumi 'YYYY-MM-DD')."""
    xs = [x for d, x in zip(dates, rets) if (d_from is None or d >= d_from) and (d_to is None or d <= d_to)]
    if len(xs) < 30:
        return {"n_days": len(xs)}
    mu, sd = sum(xs) / len(xs), _std(xs)
    eq, peak, mdd = 1.0, 1.0, 0.0
    for x in xs:
        eq *= 1.0 + x
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1.0)
    return {"n_days": len(xs), "sharpe": round(mu / sd * math.sqrt(ann), 2) if sd else None, "t": round(mu / sd * math.sqrt(len(xs)), 2) if sd else None,
            "ann_pct": round(mu * ann * 100, 1), "vol_pct": round(sd * math.sqrt(ann) * 100, 1), "maxdd_pct": round(mdd * 100, 1), "total_pct": round((eq - 1.0) * 100, 1)}


def yearly(dates, rets):
    by = {}
    for d, x in zip(dates, rets):
        y = d[:4]
        by[y] = by.get(y, 1.0) * (1.0 + x)
    return {y: round((v - 1.0) * 100, 1) for y, v in sorted(by.items())}


def iso(ms):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ms / 1000.0))


def fetch_rows(cfg, now_ms=None, fetch=None, log=print):
    """Dnevne svece sa Hyperliquid-a: {sym: [(datum otvaranja svece UTC, zatvaranje)]}. Kovanica koja ne uspe se preskace."""
    from . import data
    fetch = fetch or (lambda coin, days, now: data.fetch_candles(coin, days, interval="1d", now_ms=now))
    now_ms = now_ms or int(time.time() * 1000)
    out = {}
    for s in cfg["universe"]:
        try:
            cs = fetch(s, cfg["history_days"], now_ms)
        except Exception as e:  # noqa: BLE001
            log("core: %s preskocen (%s)" % (s, str(e)[:80]))
            continue
        rows = [(time.strftime("%Y-%m-%d", time.gmtime(c["t"] / 1000.0)), c["c"]) for c in cs if c.get("c")]
        if rows:
            out[s] = rows
    return out


def fetch_fund_rows(cfg, now_ms=None, fetch=None, log=print):
    """Fonding sa Hyperliquid-a (satne stope) za dane od T0: {sym: [(datum, zbir stopa dana)]}. Kovanica koja ne uspe se preskace; ako nista ne uspe, vraca None."""
    from . import data
    fetch = fetch or (lambda coin, days, now: data.fetch_funding(coin, days, now_ms=now))
    now_ms = now_ms or int(time.time() * 1000)
    t0 = dt.datetime.fromisoformat(cfg["t0_candle"]).replace(tzinfo=dt.timezone.utc).timestamp()
    days = int((now_ms / 1000.0 - t0) / 86400) + 5
    out = {}
    for s in cfg["universe"]:
        try:
            pts = [(x["t"], x["rate"]) for x in fetch(s, days, now_ms)]
        except Exception as e:  # noqa: BLE001
            log("core: fonding %s preskocen (%s)" % (s, str(e)[:80]))
            continue
        if pts:
            out[s] = daily_funding(pts)
    return out or None


def _bench(dates, px, i0):
    """Prinos od zatvaranja svece i0: BTC i jednako ponderisan portfolio (dnevno prebalansiran), u %."""
    btc = px.get("BTC")
    btc_pct = None
    if btc and btc[i0] is not None and btc[-1] is not None:
        btc_pct = round((btc[-1] / btc[i0] - 1.0) * 100, 2)
    r = _returns(px, len(dates))
    eq = 1.0
    for i in range(i0 + 1, len(dates)):
        xs = [r[s][i] for s in px if r[s][i] is not None]
        if xs:
            eq *= 1.0 + sum(xs) / len(xs)
    return btc_pct, round((eq - 1.0) * 100, 2)


def compute(cfg, rows, now_ms=None, backtest=None, fund_rows=None):
    """Ceo izlaz jezgra iz dnevnih sveca. rows: {sym: [(datum, zatvaranje)]}. Vraca recnik za <state>/core/core.json."""
    now_ms = now_ms or int(time.time() * 1000)
    dates, px = build_matrix(rows)
    if len(dates) < cfg["port_vol_lookback"] + max(cfg["lookbacks"]) + 10 or len(px) < cfg.get("min_names", 1):
        return {"schema": 1, "updated_utc": iso(now_ms), "config_version": cfg["version"], "error": "premalo istorije ili kovanica"}
    t0 = cfg["t0_candle"]
    if t0 not in dates:
        return {"schema": 1, "updated_utc": iso(now_ms), "config_version": cfg["version"], "last_candle": dates[-1], "error": "T0 sveca nije u podacima"}
    i0 = dates.index(t0)
    fund = align_funding(dates, fund_rows) if fund_rows else None
    sched = ensemble(px, dates, cfg, fund=fund)  # cist raspored (kao u istorijskoj proveri)
    live = ensemble(px, dates, cfg, force=(t0,), fund=fund)  # od T0 drzi izlozenost odmah, zatim nedeljno
    eq, curve, peak, mdd = 1.0, [], 1.0, 0.0
    for i in range(i0 + 1, len(dates)):
        eq *= 1.0 + live["net"][i]
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1.0)
        curve.append([dates[i], round(eq * 100, 3)])
    btc_pct, ew_pct = _bench(dates, px, i0)
    last = dates[-1]
    nxt = dt.date.fromisoformat(last)
    while nxt.weekday() != cfg["rebalance_candle_weekday"] or nxt <= dt.date.fromisoformat(last):
        nxt += dt.timedelta(days=1)
    w = {s: round(v, 4) for s, v in live["w"].items() if abs(v) > 1e-9}
    out = {"schema": 1, "updated_utc": iso(now_ms), "config_version": cfg["version"], "t0_candle": t0, "last_candle": last,
           "universe": sorted(px), "weights": w, "gross": round(live["gross"], 3), "cash": round(max(0.0, 1.0 - live["gross"]), 3),
           "weights_date": live["w_date"], "next_rebalance_candle": nxt.isoformat(), "signals": live["sig"],
           "shadow": {"days": len(curve), "ret_pct": round(eq * 100 - 100, 2), "maxdd_pct": round(mdd * 100, 2), "curve": curve[-400:],
                      "btc_pct": btc_pct, "ew_pct": ew_pct, "cost_per_side_pct": cfg["cost_per_side_pct"], "funding_included": bool(fund)},
           "schedule_only_ret_pct": round(((lambda xs: math.prod(1.0 + x for x in xs))(sched["net"][i0 + 1:]) - 1.0) * 100, 2),
           "backtest": backtest, "backtest_utc": (backtest or {}).get("generated_utc")}
    return out


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


def run(state_dir, cfg=None, now_ms=None, fetch=None, log=print, force=False, fetch_fund=None):
    """Jednom dnevno (posle 00:05 UTC, kad je svece prethodnog dana zatvorena). Pada tiho: nikad ne obara stražu."""
    cfg = cfg or load_cfg()
    now_ms = now_ms or int(time.time() * 1000)
    path = os.path.join(state_dir, "core", "core.json")
    prev = _load(path, {})
    bt = _load(os.path.join(ROOT, "calibration", "core_study.json"), None)
    yday = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000.0 - 86400))
    if (not force and prev.get("last_candle") == yday and prev.get("config_version") == cfg["version"] and not prev.get("error")
            and prev.get("backtest_utc") == (bt or {}).get("generated_utc")):
        return {"skipped": "vec racunato za " + yday}
    if not force and time.gmtime(now_ms / 1000.0).tm_hour == 0 and time.gmtime(now_ms / 1000.0).tm_min < 5:
        return {"skipped": "svece se tek zatvara"}
    rows = fetch_rows(cfg, now_ms, fetch, log)
    fund_rows = None
    if fetch_fund is not None or fetch is None:  # sa tudjom funkcijom cena (testovi) mreza za fonding se ne dira
        try:
            fund_rows = fetch_fund_rows(cfg, now_ms, fetch_fund, log)
        except Exception as e:  # noqa: BLE001
            log("core: fonding nije dostupan (%s)" % str(e)[:80])
    out = compute(cfg, rows, now_ms, bt, fund_rows)
    if out.get("error"):
        log("core: " + out["error"])
        return {"error": out["error"]}
    _save(path, out)
    return {"ok": out["last_candle"], "ret_pct": out["shadow"]["ret_pct"], "gross": out["gross"]}


def main(argv=None):
    argv = argv or sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        print("core:", json.dumps(run(state, force="--force" in argv), ensure_ascii=False))
    except Exception as e:  # noqa: BLE001 - nikad ne obara stražu
        print("core: greska (ignorisano):", str(e)[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
