"""Kolektori podataka (data lake): svaki izvor je odvojena funkcija koja vraca mali recnik ili baca gresku; orkestrator izoluje greske,
vodi zdravlje izvora i NIKAD ne izmislja vrednost (nedostupno = None). Samo stdlib. Bez AI-ja, bez novca.
Izlaz u <state>/data/: market.json, derivs.json, macro.json, sentiment.json, calendar.json, smart_money.json, universe.json,
health.json, history.jsonl, briefing.json (kompaktan sazetak za AI, do 12 KB)."""
import concurrent.futures as cf
import csv
import io
import json
import math
import os
import statistics as st
import time

from . import netutil

HL = "https://api.hyperliquid.xyz/info"
NOTIONALS = (120, 500, 2500)
STOCK_PREFIX = "xyz:"
FRED_SERIES = {
    "DGS2": "prinos 2g", "DGS10": "prinos 10g", "T10Y2Y": "krivulja 10g-2g", "T10Y3M": "krivulja 10g-3m",
    "BAMLH0A0HYM2": "kreditni raspon HY", "NFCI": "finansijski uslovi", "WALCL": "bilans Fed", "RRPONTSYD": "reverse repo",
    "VIXCLS": "VIX", "VXVCLS": "VIX 3m", "DTWEXBGS": "dolar (siroki)", "T5YIE": "ocekivana inflacija 5g",
}
YAHOO = {"^VIX": "VIX", "^VIX3M": "VIX3M", "^SKEW": "SKEW", "DX-Y.NYB": "DXY", "^TNX": "prinos 10g", "^GSPC": "SP500",
         "^NDX": "Nasdaq100", "GC=F": "zlato", "CL=F": "WTI", "HG=F": "bakar", "HYG": "HYG", "LQD": "LQD", "TLT": "TLT"}
WIKI = ("Bitcoin", "Ethereum", "Recession", "Inflation", "Stock_market_crash")
OKX_COINS = ("BTC", "ETH", "SOL", "XRP", "DOGE")
COINALYZE_COINS = ("BTC", "ETH", "SOL", "XRP", "HYPE", "DOGE", "BNB", "SUI")


def hl_post(body, **kw):
    return netutil.post_json(HL, body, tries=4, pause=0.25, **kw)


# ---------------------------------------------------------------- Hyperliquid: knjiga naloga, kontekst, fonding izmedju berzi
def book_metrics(book, notionals=NOTIONALS):
    """Spread (bps), prosecno proklizavanje za kupovinu/prodaju zadate vrednosti (bps) i dubina u $ u okviru 1% od sredine."""
    bids, asks = book["levels"]
    if not bids or not asks:
        return None
    bb, ba = float(bids[0]["px"]), float(asks[0]["px"])
    mid = (bb + ba) / 2.0
    if mid <= 0:
        return None

    def slip(levels, notional, sign):
        rem, cost, qty = float(notional), 0.0, 0.0
        for lv in levels:
            px, sz = float(lv["px"]), float(lv["sz"])
            take = min(rem, px * sz)
            cost += take
            qty += take / px
            rem -= take
            if rem <= 1e-9:
                break
        if rem > 1e-6 or qty <= 0:
            return None  # knjiga je plitka za tu vrednost
        return round(sign * (cost / qty / mid - 1.0) * 1e4, 3)

    def depth(levels, sign):
        tot = 0.0
        for lv in levels:
            px = float(lv["px"])
            if sign * (px / mid - 1.0) > 0.01:
                break
            tot += px * float(lv["sz"])
        return tot

    return {"mid": mid, "spread_bps": round((ba - bb) / mid * 1e4, 3),
            "slip_buy_bps": {str(n): slip(asks, n, 1) for n in notionals},
            "slip_sell_bps": {str(n): slip(bids, n, -1) for n in notionals},
            "depth_usd_1pct": round(min(depth(asks, 1), depth(bids, -1)), 0)}


def hl_contexts():
    """Kontekst svih instrumenata sa glavnog dex-a i xyz: {sym: {mark, funding_h, oi_usd, premium, vol24}}."""
    out = {}
    for dex in (None, "xyz"):
        body = {"type": "metaAndAssetCtxs"}
        if dex:
            body["dex"] = dex
        meta, ctxs = hl_post(body)
        for a, c in zip(meta["universe"], ctxs):
            if a.get("isDelisted"):
                continue
            try:
                mark = float(c["markPx"])
                out[a["name"]] = {"mark": mark, "funding_h": float(c.get("funding") or 0.0),
                                  "oi_usd": round(float(c.get("openInterest") or 0.0) * mark, 0),
                                  "premium": float(c.get("premium") or 0.0), "vol24": round(float(c.get("dayNtlVlm") or 0.0), 0)}
            except (KeyError, TypeError, ValueError):
                continue
    return out


def liquid_universe(ctx, min_vol=2e6, min_oi=10e6):
    """Likvidni instrumenti (tacka u vremenu): vrati poredjano po obimu. Cuva se dnevno za 'point-in-time' univerzum."""
    rows = [{"sym": s, "vol24": c["vol24"], "oi_usd": c["oi_usd"]} for s, c in ctx.items() if c["vol24"] >= min_vol and c["oi_usd"] >= min_oi]
    rows.sort(key=lambda r: -r["vol24"])
    return rows


def predicted_fundings(syms):
    """Fonding po satu na HL, Binance i Bybit (normalizovano na sat) i razlika izmedju berzi, za zadate simbole glavnog dex-a."""
    res = {}
    want = set(syms)
    for coin, venues in hl_post({"type": "predictedFundings"}):
        if coin not in want:
            continue
        d = {}
        for name, v in venues:
            if not v:
                continue
            try:
                d[name] = float(v["fundingRate"]) / float(v.get("fundingIntervalHours") or 1)
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
        res[coin] = {"hl_h": d.get("HlPerp"), "bin_h": d.get("BinPerp"), "byb_h": d.get("BybPerp"),
                     "bin_minus_hl_h": None if (d.get("BinPerp") is None or d.get("HlPerp") is None) else d["BinPerp"] - d["HlPerp"]}
    return res


def collect_market(syms, ctx=None):
    ctx = ctx if ctx is not None else hl_contexts()

    def one(s):
        try:
            return s, book_metrics(hl_post({"type": "l2Book", "coin": s}))
        except Exception:  # noqa: BLE001
            return s, None
    with cf.ThreadPoolExecutor(max_workers=6) as ex:  # javni limit je 1200 tezine/min, a l2Book vredi 2
        books = dict(ex.map(one, syms))
    try:
        xv = predicted_fundings([s for s in syms if not s.startswith(STOCK_PREFIX)])
    except Exception:  # noqa: BLE001
        xv = {}
    out = {}
    for s in syms:
        c = ctx.get(s)
        out[s] = {"ctx": c, "book": books.get(s), "fund_xv": xv.get(s)}
    return out


# ---------------------------------------------------------------- derivati: Deribit, OKX, Coinalyze
def collect_deribit(now_ms):
    out = {}
    for cur in ("BTC", "ETH"):
        d = netutil.get_json("https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=%s&start_timestamp=%d&end_timestamp=%d&resolution=3600"
                             % (cur, now_ms - 30 * 3600000, now_ms), tries=3)["result"]["data"]
        closes = [r[4] for r in d if len(r) >= 5]
        out["dvol_" + cur.lower()] = {"last": closes[-1], "chg_24h": None if len(closes) < 25 else round(closes[-1] - closes[-25], 3)} if closes else None
    summ = netutil.get_json("https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option", tries=3, max_bytes=20_000_000)["result"]
    puts = sum(r.get("open_interest", 0.0) for r in summ if r.get("instrument_name", "").endswith("-P"))
    calls = sum(r.get("open_interest", 0.0) for r in summ if r.get("instrument_name", "").endswith("-C"))
    out["btc_put_call_oi"] = round(puts / calls, 4) if calls else None
    return out


def collect_okx_lsr(coins=OKX_COINS):
    out = {}
    for c in coins:
        try:
            rows = netutil.get_json("https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio?ccy=%s&period=1H" % c, tries=3, pause=0.3)["data"]
            vals = [float(r[1]) for r in rows]
            out[c] = {"last": vals[0], "chg_24h": None if len(vals) < 25 else round(vals[0] - vals[24], 4)} if vals else None
        except Exception:  # noqa: BLE001
            out[c] = None
    return out


def collect_coinalyze(key, now_ms, coins=COINALYZE_COINS, pause=2.2):
    """Agregirani OI, fonding, likvidacije i long/short (40 poziva/min). Oblik odgovora je po dokumentaciji; proverava se kad stigne kljuc."""
    if not key:
        raise netutil.NetError("nema kljuca")
    hdr = {"api_key": key}
    base = "https://api.coinalyze.net/v1"
    markets = netutil.get_json(base + "/future-markets", headers=hdr, tries=3, pause=pause)
    by_base = {}
    for m in markets:
        if m.get("is_perpetual") and m.get("quote_asset") in ("USDT", "USD") and m.get("base_asset") in coins:
            by_base.setdefault(m["base_asset"], []).append(m["symbol"])
    out = {}
    t1 = int(now_ms / 1000)
    t0 = t1 - 26 * 3600
    for coin in coins:
        allsyms = by_base.get(coin, [])
        chosen = [x for x in allsyms if x.endswith(".A")] or allsyms  # agregirani simboli (.A) vec sabiraju sve berze: nema dvostrukog racunanja
        syms = ",".join(chosen[:3])  # manje simbola po pozivu: limit od 40 poziva u minuti se racuna i po simbolu (429 sa 6)
        if not syms:
            out[coin] = None
            continue
        row = {"symbols": chosen[:3]}
        try:
            oi = netutil.get_json(base + "/open-interest?symbols=%s&convert_to_usd=true" % syms, headers=hdr, tries=3, pause=pause)
            row["oi_usd"] = round(sum(float(x.get("value") or 0.0) for x in oi), 0)
            fr = netutil.get_json(base + "/funding-rate?symbols=%s" % syms, headers=hdr, tries=3, pause=pause)
            vals = [float(x["value"]) for x in fr if x.get("value") is not None]
            row["funding_mean"] = round(sum(vals) / len(vals), 6) if vals else None
            liq = netutil.get_json(base + "/liquidation-history?symbols=%s&interval=1hour&from=%d&to=%d&convert_to_usd=true" % (syms, t0, t1), headers=hdr, tries=3, pause=pause)
            ll = ls = 0.0
            for x in liq:
                for h in x.get("history", [])[-24:]:
                    ll += float(h.get("l") or 0.0)
                    ls += float(h.get("s") or 0.0)
            row["liq_long_24h"], row["liq_short_24h"] = round(ll, 0), round(ls, 0)
            lsr = netutil.get_json(base + "/long-short-ratio-history?symbols=%s&interval=1hour&from=%d&to=%d" % (syms, t0, t1), headers=hdr, tries=3, pause=pause)
            rs = [float(h["r"]) for x in lsr for h in x.get("history", [])[-1:] if h.get("r") is not None]
            row["lsr_last"] = round(sum(rs) / len(rs), 4) if rs else None
        except Exception as e:  # noqa: BLE001
            row["error"] = getattr(e, "args", ["greska"])[0] if e.args else "greska"
        out[coin] = row
    errs = [r["error"] for r in out.values() if r and r.get("error")]
    if out and not any(r and r.get("oi_usd") is not None for r in out.values()):
        # nijedna kovanica nije uspela: to je greska izvora (kljuc, oblik odgovora), a ne prazan odgovor; poruka nikad ne sadrzi kljuc
        raise netutil.NetError("sve kovanice neuspele: %s" % (errs[0] if errs else "nema trzista"))
    return out


# ---------------------------------------------------------------- makro i sentiment
def _chg(vals, n):
    return None if len(vals) <= n or not vals[-1 - n] else round((vals[-1] / vals[-1 - n] - 1.0) * 100.0, 3)


def collect_yahoo(tickers=YAHOO, pause=1.2):
    out = {}
    fails = 0
    for t, name in tickers.items():
        if fails >= 3:  # izvor nas ogranicava: ne gubimo vreme na ostale
            out[name] = None
            continue
        try:
            j = netutil.get_json("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1mo&interval=1d" % t.replace("^", "%5E"),
                                 tries=2, pause=pause, ua=netutil.BROWSER_UA)
            fails = 0
            closes = [c for c in j["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c is not None]
            out[name] = {"last": round(closes[-1], 4), "chg_1d_pct": _chg(closes, 1), "chg_5d_pct": _chg(closes, 5), "chg_20d_pct": _chg(closes, 20)} if closes else None
        except Exception:  # noqa: BLE001
            out[name] = None
            fails += 1
    return out


def collect_fred(series=FRED_SERIES, since="2025-01-01"):
    out = {}
    for sid, name in series.items():
        try:
            txt = netutil.get_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s&cosd=%s" % (sid, since), tries=3, pause=0.3)
            rows = [r for r in csv.reader(io.StringIO(txt))][1:]
            vals = [(r[0], float(r[1])) for r in rows if len(r) > 1 and r[1] not in ("", ".")]
            if not vals:
                out[sid] = None
                continue
            v = [x[1] for x in vals]
            out[sid] = {"name": name, "date": vals[-1][0], "last": v[-1], "chg_1": None if len(v) < 2 else round(v[-1] - v[-2], 4),
                        "chg_5": None if len(v) < 6 else round(v[-1] - v[-6], 4), "chg_20": None if len(v) < 21 else round(v[-1] - v[-21], 4)}
        except Exception:  # noqa: BLE001
            out[sid] = None
    return out


def collect_sentiment(now_ms):
    out = {}
    try:
        fg = netutil.get_json("https://api.alternative.me/fng/?limit=30", tries=3)["data"]
        vals = [int(x["value"]) for x in fg]
        out["fear_greed"] = {"last": vals[0], "label": fg[0].get("value_classification"), "avg7": round(sum(vals[:7]) / len(vals[:7]), 1),
                             "avg30": round(sum(vals) / len(vals), 1)}
    except Exception:  # noqa: BLE001
        out["fear_greed"] = None
    try:
        cg = netutil.get_json("https://api.coingecko.com/api/v3/global", tries=3)["data"]
        out["crypto_global"] = {"btc_dominance": round(cg["market_cap_percentage"]["btc"], 2), "mcap_chg_24h_pct": round(cg["market_cap_change_percentage_24h_usd"], 3)}
    except Exception:  # noqa: BLE001
        out["crypto_global"] = None
    try:
        arr = netutil.get_json("https://stablecoins.llama.fi/stablecoincharts/all", tries=3, max_bytes=20_000_000)
        tot = [float(r["totalCirculatingUSD"]["peggedUSD"]) for r in arr if r.get("totalCirculatingUSD")]
        out["stablecoins"] = {"total_usd": round(tot[-1], 0), "chg_7d_pct": _chg(tot, 7), "chg_30d_pct": _chg(tot, 30)}
    except Exception:  # noqa: BLE001
        out["stablecoins"] = None
    day = lambda off: time.strftime("%Y%m%d", time.gmtime(now_ms / 1000 + off * 86400))  # noqa: E731
    wiki = {}
    for art in WIKI:
        try:
            items = netutil.get_json("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/%s/daily/%s/%s" % (art, day(-22), day(-1)),
                                     tries=2, pause=0.2)["items"]
            v = [x["views"] for x in items]
            z = None
            if len(v) >= 8 and st.pstdev(v[:-1]) > 0:
                z = round((v[-1] - st.mean(v[:-1])) / st.pstdev(v[:-1]), 2)
            wiki[art] = {"last": v[-1], "z": z} if v else None
        except Exception:  # noqa: BLE001
            wiki[art] = None
    out["wiki_attention"] = wiki
    return out


# ---------------------------------------------------------------- kalendari
def collect_calendar(now_ms, stock_syms, finnhub_key=None):
    out = {"events": [], "earnings": {}}
    ff = netutil.get_json("https://nfs.faireconomy.media/ff_calendar_thisweek.json", tries=3, ua=netutil.BROWSER_UA)
    lo, hi = now_ms - 2 * 3600000, now_ms + 72 * 3600000
    for e in ff:
        if e.get("impact") not in ("High", "Medium"):
            continue
        try:
            t = _parse_ff_time(e["date"])
        except Exception:  # noqa: BLE001
            continue
        if lo <= t <= hi:
            out["events"].append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t / 1000)), "title": e.get("title"), "country": e.get("country"),
                                  "impact": e.get("impact"), "forecast": e.get("forecast"), "previous": e.get("previous"), "actual": e.get("actual")})
    out["events"].sort(key=lambda x: x["ts"])
    tickers = {s[len(STOCK_PREFIX):]: s for s in stock_syms if s.startswith(STOCK_PREFIX)}
    day = lambda off: time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000 + off * 86400))  # noqa: E731
    out["finnhub"] = "nema kljuca"
    try:
        if finnhub_key:
            j = netutil.get_json("https://finnhub.io/api/v1/calendar/earnings?from=%s&to=%s&token=%s" % (day(0), day(14), finnhub_key), tries=3, pause=0.3)
            rows = j.get("earningsCalendar") if isinstance(j, dict) else None
            if rows is None:
                raise netutil.NetError("neocekivan oblik odgovora")
            for r in rows:
                s = tickers.get(r.get("symbol"))
                if s:
                    out["earnings"][s] = {"date": r.get("date"), "hour": r.get("hour"), "eps_est": r.get("epsEstimate"), "source": "finnhub"}
            out["finnhub"] = "ok, %d redova za 14 dana, %d nasih" % (len(rows), len(out["earnings"]))
        else:
            raise netutil.NetError("nema kljuca")
    except Exception as e:  # noqa: BLE001
        out["finnhub"] = "%s: %s" % (type(e).__name__, e)
        for off in range(0, 6):  # rezerva: Nasdaq (neslužbeno), jedan poziv po danu
            try:
                j = netutil.get_json("https://api.nasdaq.com/api/calendar/earnings?date=%s" % day(off), tries=2, pause=0.8, ua=netutil.BROWSER_UA)
                for r in (j.get("data") or {}).get("rows") or []:
                    s = tickers.get(r.get("symbol"))
                    if s and s not in out["earnings"]:
                        out["earnings"][s] = {"date": day(off), "hour": r.get("time"), "eps_est": r.get("epsForecast"), "source": "nasdaq"}
            except Exception:  # noqa: BLE001
                continue
    return out


def _parse_ff_time(s):
    """ISO sa pomerajem, npr. 2026-10-08T14:30:00-04:00 -> ms."""
    import datetime as dt
    return int(dt.datetime.fromisoformat(s).timestamp() * 1000)


# ---------------------------------------------------------------- pametan novac
def collect_smart_money(syms, n=60, min_value=2e5):
    """Agregirano pozicioniranje najboljih naloga (po mesecnom ROI) po kovanici; adrese se NE cuvaju."""
    raw = netutil.get_text("https://stats-data.hyperliquid.xyz/Mainnet/leaderboard", tries=2, max_bytes=60_000_000)
    rows = json.loads(raw)["leaderboardRows"]
    cand = []
    for r in rows:
        try:
            av = float(r["accountValue"])
            perf = dict(r["windowPerformances"])
            m, w = perf["month"], perf["week"]
            if av >= min_value and float(m["pnl"]) > 0 and float(w["pnl"]) > 0:
                cand.append((float(m["roi"]), r["ethAddress"]))
        except (KeyError, TypeError, ValueError):
            continue
    cand.sort(reverse=True)
    agg = {}
    used = 0

    def wallet(addr):
        rows = []
        for dex in (None, "xyz"):
            body = {"type": "clearinghouseState", "user": addr}
            if dex:
                body["dex"] = dex
            try:
                stt = hl_post(body)
            except Exception:  # noqa: BLE001
                continue
            for ap in stt.get("assetPositions", []):
                p = ap.get("position", {})
                try:
                    usd = float(p["szi"]) * float(p.get("markPx") or p.get("entryPx") or 0.0)
                except (KeyError, TypeError, ValueError):
                    continue
                if usd:
                    rows.append((p["coin"], usd))
        return rows
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(wallet, [a for _, a in cand[:n]]))
    for rows in results:
        for coin, usd in rows:
            a = agg.setdefault(coin, {"long_usd": 0.0, "short_usd": 0.0, "wallets": 0})
            a["long_usd" if usd > 0 else "short_usd"] += abs(usd)
            a["wallets"] += 1
        used += 1 if rows else 0
    want = set(syms)
    out = {"wallets_with_positions": used, "wallets_selected": min(n, len(cand)), "coins": {}}
    for coin, a in sorted(agg.items(), key=lambda kv: -(kv[1]["long_usd"] + kv[1]["short_usd"]))[:25] + [(c, agg[c]) for c in want if c in agg]:
        tot = a["long_usd"] + a["short_usd"]
        out["coins"][coin] = {"net_usd": round(a["long_usd"] - a["short_usd"], 0), "gross_usd": round(tot, 0), "net_share": round((a["long_usd"] - a["short_usd"]) / tot, 3) if tot else None,
                              "wallets": a["wallets"]}
    return out
