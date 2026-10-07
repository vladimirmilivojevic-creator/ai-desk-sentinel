"""Studija 'sta je bitno': kako se dnevna pravila (korpe) ponasaju u razlicitim stanjima trzista (makro, raspolozenje, derivati, struktura kripta).
Skup promenljivih stanja je UNAPRED zadat (STATE_VARS), stanje se uzima sa kasnjenjem 1 dan (poznato pre ulaza), tercili se racunaju samo iz proslosti
(klizni prozor od 2 godine), poredi se prosek rezultata u gornjem i donjem tercilu na neprekidnim blokovima od 14 dana (nezavisniji uzorci), a korekcija je BH-FDR.
Nasumicne korpe (placebo) prolaze ISTE testove da se vidi koliko lazno pozitivnih daje sam sum. Samo stdlib.
Upotreba: LAB_CONFIG=config/lab_v3.json python -m lab.regime_study [izlaz.json] [izlaz.md]"""
import datetime as dt
import json
import math
import os
import random
import statistics as st
import sys
import time
import urllib.parse

from . import backtest, collectors2 as C2, netutil, portfolio_sim as ps, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "regime")
DAY = 86400000
BLOCK = 14
MIN_HIST = 250  # najmanje toliko dana proslosti pre nego sto se tercil racuna

YAHOO = {"vix": "^VIX", "vix3m": "^VIX3M", "move": "^MOVE", "vvix": "^VVIX", "dxy": "DX-Y.NYB", "tnx": "^TNX", "spx": "^GSPC", "hyg": "HYG", "lqd": "LQD",
         "gold": "GC=F", "wti": "CL=F", "kre": "KRE", "usdjpy": "JPY=X"}
FRED = {"hy_oas": "BAMLH0A0HYM2", "nfci": "NFCI", "t10y2y": "T10Y2Y", "stlfsi": "STLFSI4", "real10": "DFII10", "t5yie": "T5YIE", "walcl": "WALCL", "tga": "WTREGEN", "rrp": "RRPONTSYD"}
LAG = {"fred_weekly": 2, "cftc": 4}


# ---------------------------------------------------------------- ucitavanje istorije (kes na disku)
def _cached(name, fn, max_age_s=86400):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".json")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age_s:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    data = fn()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    return data


def load_yahoo(ticker, rng="6y"):
    j = netutil.get_json("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=1d" % (urllib.parse.quote(ticker, safe=""), rng), tries=3, pause=0.4,
                         ua=netutil.BROWSER_UA, max_bytes=20_000_000)
    r = j["chart"]["result"][0]
    ts, cl = r["timestamp"], r["indicators"]["quote"][0]["close"]
    return {dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(): c for t, c in zip(ts, cl) if c is not None}


def load_fred(sid, since="2021-01-01"):
    import csv
    import io
    txt = netutil.get_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s&cosd=%s" % (sid, since), tries=3, pause=0.3)
    return {r[0]: float(r[1]) for r in list(csv.reader(io.StringIO(txt)))[1:] if len(r) > 1 and r[1] not in ("", ".")}


def load_fng():
    d = netutil.get_json("https://api.alternative.me/fng/?limit=0&format=json", tries=3, max_bytes=5_000_000)["data"]
    return {dt.datetime.fromtimestamp(int(x["timestamp"]), dt.timezone.utc).date().isoformat(): float(x["value"]) for x in d}


def load_dvol(cur="BTC", start="2021-04-01"):
    t0 = int(dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    out, end = {}, int(time.time() * 1000)
    for _ in range(4):
        j = netutil.get_json("https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=%s&start_timestamp=%d&end_timestamp=%d&resolution=1D" % (cur, t0, end), tries=3)["result"]
        for r in j.get("data", []):
            out[dt.datetime.fromtimestamp(r[0] / 1000, dt.timezone.utc).date().isoformat()] = r[4]
        cont = j.get("continuation")
        if not cont:
            break
        end = cont
    return out


def load_stable():
    arr = netutil.get_json("https://stablecoins.llama.fi/stablecoincharts/all", tries=3, max_bytes=30_000_000)
    return {dt.datetime.fromtimestamp(int(r["date"]), dt.timezone.utc).date().isoformat(): float(r["totalCirculatingUSD"]["peggedUSD"]) for r in arr if r.get("totalCirculatingUSD")}


def load_cftc_net(key):
    ds, name = C2.CFTC_MARKETS[key]
    lf, sf = C2.CFTC_FIELDS[ds]
    params = {"$select": "report_date_as_yyyy_mm_dd,open_interest_all,%s,%s" % (lf, sf), "$where": "market_and_exchange_names='%s'" % name,
              "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": "700"}
    q = "&".join("%s=%s" % (k, urllib.parse.quote(v, safe="")) for k, v in params.items())
    rows = netutil.get_json("%s%s.json?%s" % (C2.CFTC_BASE, ds, q), tries=3, pause=0.2)
    out = {}
    for r in rows:
        oi, lo, sh = C2._f(r.get("open_interest_all")), C2._f(r.get(lf)), C2._f(r.get(sf))
        if oi and lo is not None and sh is not None:
            out[r["report_date_as_yyyy_mm_dd"][:10]] = (lo - sh) / oi * 100.0
    return out


def load_binance_agg(cache_dir=None):
    """Dnevne medijane preko kovanica iz kesa Binance arhiva (lab/cache/binance): odnos dugih/kratkih, promena OI za 7 d, taker."""
    d = cache_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "binance")
    if not os.path.isdir(d):
        return {}
    per = {}
    for fn in os.listdir(d):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            days = json.load(f)
        keys = sorted(k for k, v in days.items() if v)
        idx = {k: i for i, k in enumerate(keys)}
        for k in keys:
            v, i = days[k], idx[k]
            rec = {"glob_ls": v.get("glob_ls"), "taker": v.get("taker")}
            if i >= 7 and days[keys[i - 7]].get("oi_amt") and v.get("oi_amt"):
                rec["oi_c7"] = (v["oi_amt"] / days[keys[i - 7]]["oi_amt"] - 1.0) * 100.0
            per.setdefault(k, []).append(rec)
    out = {}
    for k, rows in per.items():
        if len(rows) < 8:
            continue
        for f_, name in (("glob_ls", "bn_glob_ls"), ("taker", "bn_taker"), ("oi_c7", "bn_oi_c7")):
            vals = [r[f_] for r in rows if r.get(f_) is not None]
            if len(vals) >= 8:
                out.setdefault(name, {})[k] = st.median(vals)
    return out


# ---------------------------------------------------------------- stanja: poravnanje i transformacije
def dates_range(a, b):
    d0, d1 = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range((d1 - d0).days + 1)]


def ffill(series, days, lag=0):
    """Poravna seriju {datum: vrednost} na dane `days`; vrednost postaje poznata `lag` dana posle datuma; prazno = poslednja poznata."""
    shifted = {}
    for d, v in series.items():
        key = (dt.date.fromisoformat(d) + dt.timedelta(days=lag)).isoformat() if lag else d
        shifted[key] = v
    out, last = {}, None
    for d in days:
        if d in shifted and shifted[d] is not None:
            last = shifted[d]
        out[d] = last
    return out


def pct_change(vals, n):
    return [None if i < n or vals[i] is None or vals[i - n] in (None, 0) else (vals[i] / vals[i - n] - 1.0) * 100.0 for i in range(len(vals))]


def diff(vals, n):
    return [None if i < n or vals[i] is None or vals[i - n] is None else vals[i] - vals[i - n] for i in range(len(vals))]


def trend(vals, n):
    out = []
    for i in range(len(vals)):
        w = [x for x in vals[max(0, i - n + 1):i + 1] if x is not None]
        out.append(None if len(w) < n * 0.9 or vals[i] is None else (vals[i] / (sum(w) / len(w)) - 1.0) * 100.0)
    return out


def crypto_states(series, days, group="crypto"):
    """Stanja iz sveca: BTC trend/prinos/volatilnost, sirina tržista, disperzija, prosecna korelacija, ETH/BTC."""
    members = [s for s in series.values() if s.group == group]
    px = {m.sym: {dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).date().isoformat(): m.c[i] for i, t in enumerate(m.t)} for m in members}
    btc = px.get("BTC") or {}
    grid = {s: [px[s].get(d) for d in days] for s in px}
    ret1 = {s: [None] + [None if v[i] is None or v[i - 1] in (None, 0) else v[i] / v[i - 1] - 1.0 for i in range(1, len(v))] for s, v in grid.items()}
    out = {}
    b = [btc.get(d) for d in days]
    out["btc_trend200"] = trend(b, 200)
    out["btc_ret30"] = pct_change(b, 30)
    rv = []
    for i in range(len(days)):
        w = [x for x in (ret1.get("BTC") or [None] * len(days))[max(0, i - 29):i + 1] if x is not None]
        rv.append(st.pstdev(w) * math.sqrt(365) * 100.0 if len(w) >= 25 else None)
    out["btc_rv30"] = rv
    breadth, disp, corr = [], [], []
    ma50 = {s: trend(v, 50) for s, v in grid.items()}
    r30 = {s: pct_change(v, 30) for s, v in grid.items()}
    for i in range(len(days)):
        above = [ma50[s][i] > 0 for s in grid if ma50[s][i] is not None]
        breadth.append(sum(above) / len(above) * 100.0 if len(above) >= 8 else None)
        rs = [r30[s][i] for s in grid if r30[s][i] is not None]
        disp.append(st.pstdev(rs) if len(rs) >= 8 else None)
        if i >= 30 and i % 3 == 0:  # korelacija je skupa: racuna se svaki treci dan, ostalo se prenosi
            names = [s for s in grid if all(x is not None for x in ret1[s][i - 19:i + 1])][:20]
            if len(names) >= 8:
                cs = []
                for a in range(len(names)):
                    for c in range(a + 1, len(names)):
                        x, y = ret1[names[a]][i - 19:i + 1], ret1[names[c]][i - 19:i + 1]
                        sx, sy = st.pstdev(x), st.pstdev(y)
                        if sx > 0 and sy > 0:
                            mx, my = st.mean(x), st.mean(y)
                            cs.append(sum((p - mx) * (q - my) for p, q in zip(x, y)) / len(x) / (sx * sy))
                corr.append(st.mean(cs) if cs else (corr[-1] if corr else None))
            else:
                corr.append(corr[-1] if corr else None)
        else:
            corr.append(corr[-1] if corr else None)
    out["breadth50"], out["dispersion30"], out["avg_corr20"] = breadth, disp, corr
    eth = [(px.get("ETH") or {}).get(d) for d in days]
    out["ethbtc_c30"] = pct_change([None if e is None or bb_ in (None, 0) else e / bb_ for e, bb_ in zip(eth, b)], 30)
    return out


def build_states(series, days, loaders=None):
    """{ime: lista vrednosti po danima}; loaders: {kes_ime: funkcija} (u testu zamenjivo). Greska jednog izvora ga samo izostavlja."""
    L = loaders or {}
    st_ = {}

    def get(name, fn):
        try:
            return (L.get(name) or (lambda: _cached(name, fn)))()
        except Exception as e:  # noqa: BLE001
            print("  izvor %s nije dostupan: %s" % (name, type(e).__name__))
            return None
    yh = {k: get("y_" + k, lambda t=t: load_yahoo(t)) for k, t in YAHOO.items()}
    fr = {k: get("f_" + k, lambda s=s: load_fred(s)) for k, s in FRED.items()}
    al = lambda d, lag=0: [v for v in ffill(d, days, lag).values()] if d else None  # noqa: E731
    y = {k: al(v) for k, v in yh.items()}
    f = {k: al(v, LAG["fred_weekly"] if k in ("nfci", "stlfsi", "walcl", "tga") else 0) for k, v in fr.items()}
    if y.get("vix"):
        st_["vix"], st_["vix_c5"] = y["vix"], pct_change(y["vix"], 5)
    if y.get("vix") and y.get("vix3m"):
        st_["vix_term"] = [None if a is None or b in (None, 0) else a / b for a, b in zip(y["vix"], y["vix3m"])]
    for k in ("move", "vvix"):
        if y.get(k):
            st_[k] = y[k]
    for k in ("dxy", "gold", "wti", "kre", "usdjpy"):
        if y.get(k):
            st_[k + "_c20"] = pct_change(y[k], 20)
    if y.get("tnx"):
        st_["tnx_c20"] = diff(y["tnx"], 20)
    if y.get("spx"):
        st_["spx_trend200"] = trend(y["spx"], 200)
    if y.get("hyg") and y.get("lqd"):
        ratio = [None if a is None or b in (None, 0) else a / b for a, b in zip(y["hyg"], y["lqd"])]
        st_["hyg_lqd_c20"] = pct_change(ratio, 20)
    for k in ("hy_oas", "nfci", "t10y2y", "stlfsi", "real10", "t5yie"):
        if f.get(k):
            st_[k] = f[k]
    if f.get("hy_oas"):
        st_["hy_oas_c20"] = diff(f["hy_oas"], 20)
    if f.get("walcl") and f.get("tga") and f.get("rrp"):
        nl = [None if None in (a, b, c) else (a - b) / 1e6 - c / 1e3 for a, b, c in zip(f["walcl"], f["tga"], f["rrp"])]
        st_["net_liq_c28"] = [None if i < 28 or nl[i] is None or nl[i - 28] is None else (nl[i] - nl[i - 28]) * 1000.0 for i in range(len(nl))]  # mlrd $
    fng = get("fng", load_fng)
    if fng:
        a = al(fng)
        st_["fng"], st_["fng_c7"] = a, diff(a, 7)
    dv = get("dvol", load_dvol)
    if dv:
        a = al(dv)
        st_["dvol"], st_["dvol_c7"] = a, diff(a, 7)
    stb = get("stable", load_stable)
    if stb:
        st_["stable_c30"] = pct_change(al(stb), 30)
    for k in ("btc", "gold", "es"):
        cf_ = get("cftc_" + k, lambda k=k: load_cftc_net(k))
        if cf_:
            st_["cftc_%s_net" % k] = al(cf_, LAG["cftc"])
    bn = get("bn_agg", load_binance_agg) if "bn_agg" not in L else L["bn_agg"]()
    for name, d in (bn or {}).items():
        st_[name] = al(d)
    st_.update(crypto_states(series, days))
    return st_


# ---------------------------------------------------------------- statistika uslovljenosti
def rank_labels(x, min_hist=MIN_HIST, window=730):
    """Za svaki dan: 'low' / 'mid' / 'high' prema tercilu vrednosti medju PRETHODNIH `window` dana (bez gledanja unapred); None dok nema istorije.
    Klizni prozor (2 godine) umesto celokupne proslosti: serije sa trendom (npr. DVOL koji pada vec godinama) inace ostanu zauvek u jednom tercilu."""
    out, hist = [], []
    for v in x:
        if v is None:
            out.append(None)
            continue
        if len(hist) >= min_hist:
            recent = hist[-window:]
            below = sum(1 for h in recent if h < v) / len(recent)
            out.append("low" if below < 1 / 3 else ("high" if below > 2 / 3 else "mid"))
        else:
            out.append(None)
        hist.append(v)
    return out


def blocks(returns, labels, block=BLOCK):
    """Neprekidni blokovi od `block` dana: (oznaka stanja na pocetku bloka, prosecan dnevni prinos u bloku). Stanje se uzima sa kasnjenjem 1 dan."""
    rows = []
    for i in range(1, len(returns) - block + 1, block):
        lab = labels[i - 1]
        w = [r for r in returns[i:i + block] if r is not None]
        if lab and len(w) >= block * 0.8:
            rows.append((lab, sum(w) / len(w)))
    return rows


def welch(a, b):
    if len(a) < 5 or len(b) < 5:
        return None
    va, vb = st.pvariance(a) * len(a) / (len(a) - 1), st.pvariance(b) * len(b) / (len(b) - 1)
    se = math.sqrt(va / len(a) + vb / len(b))
    return None if se == 0 else (st.mean(a) - st.mean(b)) / se


def condition(returns, x):
    """Rezultat pravila u gornjem i donjem tercilu stanja x: {n_high, n_low, mean_high, mean_low, diff, t}."""
    bl = blocks(returns, rank_labels(x))
    hi = [m for lab, m in bl if lab == "high"]
    lo = [m for lab, m in bl if lab == "low"]
    t = welch(hi, lo)
    if t is None:
        return None
    return {"n_high": len(hi), "n_low": len(lo), "mean_high": round(st.mean(hi), 4), "mean_low": round(st.mean(lo), 4), "diff": round(st.mean(hi) - st.mean(lo), 4), "t": round(t, 2)}


def strategy_returns(series, days, group="crypto", cost=0.23):
    """Dnevni prinosi (%) korpi, poravnati na `days` (None gde nema). Prebijanje pozicija, jedna pozicija po simbolu."""
    members = [s for s in series.values() if s.group == group]
    idx = {d: i for i, d in enumerate(days)}

    def mom(L):
        return lambda mi, i, t: members[mi].c[i] / members[mi].c[i - L] - 1.0 if i >= L else None
    spec = {"csm_mom14": (mom(14), 7, 1), "csm_mom7": (mom(7), 14, 1), "csm_rev14": (mom(14), 7, -1)}
    for seed in (1, 2, 3):
        spec["placebo%d" % seed] = (lambda mi, i, t, _s=seed: int.from_bytes(__import__("hashlib").md5(("%s:%d:%d" % (_s, mi, t)).encode()).digest()[:6], "big") / 2.0 ** 48, 7, 1)
    out = {}
    for name, (score, H, sign) in spec.items():
        rows, _, _ = ps.basket_netted(members, score, H, 5, sign, cost, 8)
        arr = [None] * len(days)
        for t, x in rows:
            d = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).date().isoformat()
            if d in idx:
                arr[idx[d]] = x
        out[name] = arr
    return out


def run_study(returns, states, q=0.10):
    results = []
    for sname, r in returns.items():
        for vname, x in states.items():
            c = condition(r, x)
            if c:
                results.append(dict(c, strategy=sname, var=vname, placebo=sname.startswith("placebo")))
    real = [r for r in results if not r["placebo"]]
    pv = [((r["strategy"], r["var"]), stats.t_to_p(r["t"])) for r in real]
    ok = stats.bh_fdr(pv, q)
    for r in results:
        r["fdr_pass"] = (r["strategy"], r["var"]) in ok
    pl = [abs(r["t"]) for r in results if r["placebo"]]
    null = {"n_tests": len(pl), "max_abs_t": max(pl) if pl else None, "share_abs_t_gt_2": round(sum(1 for t in pl if t > 2) / len(pl), 3) if pl else None}
    real.sort(key=lambda r: -abs(r["t"]))
    return {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tests_real": len(real), "fdr_q": q, "fdr_pass": sum(1 for r in real if r["fdr_pass"]),
            "null": null, "results": real, "placebo_results": [r for r in results if r["placebo"]]}


def to_markdown(res, top=25):
    n = res["null"]
    L = ["# Studija stanja trzista: sta menja rezultat dnevnih pravila", "",
         "Generisano %s. Testova (pravila x stanja): %d. BH-FDR %.0f%%: prolazi %d. Sum sam po sebi (nasumicne korpe, isti testovi): %s testova, najveci |t| %s, udeo |t| > 2: %s." % (
             res["generated_utc"], res["tests_real"], res["fdr_q"] * 100, res["fdr_pass"], n["n_tests"], n["max_abs_t"], n["share_abs_t_gt_2"]), "",
         "Postupak: stanje se uzima sa kasnjenjem 1 dan, tercili iz proslosti, blokovi od 14 dana, razlika proseka gornji minus donji tercil (Welch t).", "",
         "| pravilo | stanje | n gore | n dole | prosek gore %/dan | prosek dole %/dan | razlika | t | FDR |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res["results"][:top]:
        L.append("| %s | %s | %d | %d | %.3f | %.3f | %+.3f | %.2f | %s |" % (r["strategy"], r["var"], r["n_high"], r["n_low"], r["mean_high"], r["mean_low"], r["diff"], r["t"], "da" if r["fdr_pass"] else "ne"))
    return "\n".join(L) + "\n"


def evidence(res, states_latest=None, t_min=2.0):
    """Kompaktan zapis za AI i panel: broj testova, sum, i nalazi koji prolaze FDR ili imaju |t| >= t_min (bez obecanja)."""
    # csm_rev14 je ogledalo csm_mom14 (isti signal, suprotna strana): u zapis ide samo jednom
    keep = [r for r in res["results"] if (r["fdr_pass"] or abs(r["t"]) >= t_min) and r["strategy"] != "csm_rev14"][:12]
    return {"generated_utc": res["generated_utc"], "tests": res["tests_real"], "fdr_pass": res["fdr_pass"], "null_max_abs_t": res["null"]["max_abs_t"],
            "null_share_gt2": res["null"]["share_abs_t_gt_2"],
            "findings": [{"strategy": r["strategy"], "var": r["var"], "diff": r["diff"], "t": r["t"], "fdr": r["fdr_pass"], "high_better": r["diff"] > 0} for r in keep],
            "note": "Nalaz nije dokaz: sum sam daje |t|>2 u udelu null_share_gt2 testova."}


def main():
    out_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "calibration", "regime_study.json")
    out_md = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "calibration", "regime_study.md")
    cfg, _ = backtest.load_config()
    series = backtest.build_series(cfg, 1500, with_funding=False, interval="1d", log=lambda *a: None)
    members = [s for s in series.values() if s.group == "crypto"]
    first = min(dt.datetime.fromtimestamp(m.t[0] / 1000, dt.timezone.utc).date() for m in members)
    last = max(dt.datetime.fromtimestamp(m.t[-1] / 1000, dt.timezone.utc).date() for m in members)
    days = dates_range("2021-06-01", last.isoformat())  # spoljne serije imaju istoriju pre sveca: tercili imaju dovoljno proslosti
    print("dana: %d (%s .. %s), kripto instrumenata: %d, prve svece %s" % (len(days), days[0], days[-1], len(members), first))
    states = build_states(series, days)
    print("stanja: %d" % len(states), sorted(states))
    returns = strategy_returns(series, days)
    res = run_study(returns, states)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res))
    ev = evidence(res)
    with open(os.path.join(ROOT, "config", "evidence.json"), "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
