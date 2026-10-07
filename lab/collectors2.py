"""Kolektori podataka v2 (data lake): CFTC pozicioniranje, DefiLlama aktivnost, Kalshi verovatnoce Fed odluke, OKX tok naloga, Binance javni arhiv (dnevno),
on-chain (CoinMetrics community) i GDELT ton vesti. Svi su bez kljuca, svaki je odvojena funkcija koja vraca mali recnik ili baca gresku.
Nedostupno = None, nikad izmisljeno. Samo stdlib."""
import concurrent.futures as cf
import datetime as dt
import json
import os
import statistics as st
import time
import urllib.parse

from . import binance_backfill as bb, netutil

CFTC_BASE = "https://publicreporting.cftc.gov/resource/"
TFF, DIS = "gpe5-46if", "72hh-3qpy"
# kljuc: (skup podataka, tacno ime trzista, duga polja, kratka polja). TFF = finansijski fjuceri (lev_money), DIS = robni (managed money).
CFTC_MARKETS = {
    "btc": (TFF, "BITCOIN - CHICAGO MERCANTILE EXCHANGE"), "eth": (TFF, "ETHER CASH SETTLED - CHICAGO MERCANTILE EXCHANGE"),
    "es": (TFF, "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE"), "nq": (TFF, "NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE"),
    "usd": (TFF, "USD INDEX - ICE FUTURES U.S."), "ust10": (TFF, "UST 10Y NOTE - CHICAGO BOARD OF TRADE"),
    "jpy": (TFF, "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE"),
    "gold": (DIS, "GOLD - COMMODITY EXCHANGE INC."), "silver": (DIS, "SILVER - COMMODITY EXCHANGE INC."),
    "copper": (DIS, "COPPER- #1 - COMMODITY EXCHANGE INC."), "wti": (DIS, "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE"),
    "natgas": (DIS, "NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE"),
}
CFTC_FIELDS = {TFF: ("lev_money_positions_long", "lev_money_positions_short"), DIS: ("m_money_positions_long_all", "m_money_positions_short_all")}
OKX_FLOW_COINS = ("BTC", "ETH", "SOL", "XRP", "DOGE")
GDELT_QUERIES = {"oil": "oil prices OR OPEC", "war": "war OR sanctions OR missile", "crypto": "bitcoin OR crypto regulation"}


def _f(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- CFTC: pozicioniranje velikih igraca (nedeljno)
def collect_cftc(now_ms=None, weeks=156, markets=CFTC_MARKETS):
    """Neto pozicija spekulanata kao % otvorenog interesa, promena za nedelju dana i percentil u poslednje 3 godine."""
    out = {}
    for key, (ds, name) in markets.items():
        lf, sf = CFTC_FIELDS[ds]
        try:
            params = {"$select": "report_date_as_yyyy_mm_dd,open_interest_all,%s,%s" % (lf, sf), "$where": "market_and_exchange_names='%s'" % name,
                      "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": str(weeks)}
            q = "&".join("%s=%s" % (k, urllib.parse.quote(v, safe="")) for k, v in params.items())
            rows = netutil.get_json("%s%s.json?%s" % (CFTC_BASE, ds, q), tries=3, pause=0.2)
            net = []
            for r in rows:
                oi, lo, sh = _f(r.get("open_interest_all")), _f(r.get(lf)), _f(r.get(sf))
                if oi and lo is not None and sh is not None:
                    net.append((r["report_date_as_yyyy_mm_dd"][:10], (lo - sh) / oi * 100.0))
            if len(net) < 2:
                out[key] = None
                continue
            last = net[0][1]
            out[key] = {"date": net[0][0], "net_pct_oi": round(last, 2), "chg_1w": round(last - net[1][1], 2),
                        "pctl": round(100.0 * sum(1 for _, v in net if v <= last) / len(net), 1), "n_weeks": len(net)}
        except Exception:  # noqa: BLE001
            out[key] = None
    if not any(out.values()):
        raise netutil.NetError("CFTC: nijedno trziste nije vraceno")
    return out


# ---------------------------------------------------------------- DefiLlama: aktivnost (DEX obim, naknade)
def collect_llama_activity(now_ms=None):
    out = {}
    for name, key in (("dexs", "dex"), ("fees", "fees")):
        j = netutil.get_json("https://api.llama.fi/overview/%s?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true" % name, tries=3, max_bytes=30_000_000)
        out[key] = {"total24h": _f(j.get("total24h")), "chg_1d": _f(j.get("change_1d")), "chg_7d": _f(j.get("change_7d")), "chg_1m": _f(j.get("change_1m"))}
        hl = [p for p in j.get("protocols", []) if (p.get("name") or "") in ("Hyperliquid Perps", "Hyperliquid Spot Orderbook")]
        out[key]["hyperliquid_24h"] = round(sum(_f(p.get("total24h")) or 0.0 for p in hl), 0) if hl else None
    if out["dex"]["total24h"] is None and out["fees"]["total24h"] is None:
        raise netutil.NetError("DefiLlama: prazan odgovor")
    return out


# ---------------------------------------------------------------- Kalshi: verovatnoce odluke Fed-a
def fed_summary(markets, now_ms):
    """Iz tržišta praga 'iznad X%' racuna najverovatniji nivo, verovatnoce iznad/ispod njega i ocekivanu stopu.
    markets: lista sa floor_strike i yes cenom (bid/ask u dolarima ili last)."""
    pts = []
    for m in markets:
        k = _f(m.get("floor_strike"))
        bid, ask, last = _f(m.get("yes_bid_dollars")), _f(m.get("yes_ask_dollars")), _f(m.get("last_price_dollars"))
        p = (bid + ask) / 2.0 if bid is not None and ask is not None and ask >= bid else last
        if k is not None and p is not None:
            pts.append((k, min(max(p, 0.0), 1.0)))
    pts.sort()
    if len(pts) < 3:
        return None
    probs = [p for _, p in pts]
    for i in range(1, len(probs)):  # monotono nerastuce: popravi sum
        probs[i] = min(probs[i], probs[i - 1])
    modal_i = max((i for i, p in enumerate(probs) if p >= 0.5), default=None)
    step = pts[1][0] - pts[0][0]
    exp_rate = pts[0][0] + step * sum(probs)
    if modal_i is None:
        return {"modal_level": None, "p_up": None, "p_down": None, "expected_rate": round(exp_rate, 3)}
    up = probs[modal_i + 1] if modal_i + 1 < len(probs) else 0.0
    return {"modal_level": pts[modal_i][0], "p_up": round(up, 3), "p_down": round(1.0 - probs[modal_i], 3), "expected_rate": round(exp_rate, 3)}


def collect_kalshi_fed(now_ms):
    ev = netutil.get_json("https://api.elections.kalshi.com/trade-api/v2/events?series_ticker=KXFED&status=open&limit=50", tries=3)["events"]
    ev = [e for e in ev if e.get("strike_date")]
    ev.sort(key=lambda e: e["strike_date"])
    if not ev:
        raise netutil.NetError("Kalshi: nema otvorenih Fed dogadjaja")
    nxt = ev[0]
    ms = netutil.get_json("https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker=%s&limit=100" % nxt["event_ticker"], tries=3)["markets"]
    res = fed_summary(ms, now_ms) or {}
    t = dt.datetime.fromisoformat(nxt["strike_date"].replace("Z", "+00:00")).timestamp() * 1000
    res.update({"event": nxt["event_ticker"], "meeting_utc": nxt["strike_date"], "days_to_meeting": round((t - now_ms) / 86400000.0, 2)})
    return res


# ---------------------------------------------------------------- OKX: tok naloga (javno, radi iz Actions-a)
def collect_okx_flow(coins=OKX_FLOW_COINS):
    out = {}
    for c in coins:
        row = {}
        try:
            tk = netutil.get_json("https://www.okx.com/api/v5/rubik/stat/taker-volume?ccy=%s&instType=CONTRACTS&period=1H" % c, tries=3, pause=0.15)["data"]
            sell = [float(r[1]) for r in tk]
            buy = [float(r[2]) for r in tk]
            if len(buy) >= 48:
                row["taker_ratio_24h"] = round(sum(buy[:24]) / max(sum(sell[:24]), 1e-9), 4)
                row["taker_ratio_prev24h"] = round(sum(buy[24:48]) / max(sum(sell[24:48]), 1e-9), 4)
            elif buy:
                row["taker_ratio_24h"] = round(sum(buy) / max(sum(sell), 1e-9), 4)
            oi = netutil.get_json("https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-volume?ccy=%s&period=1H" % c, tries=3, pause=0.15)["data"]
            ois = [float(r[1]) for r in oi]
            vol = [float(r[2]) for r in oi]
            if len(ois) > 24 and ois[24]:
                row["oi_chg_24h_pct"] = round((ois[0] / ois[24] - 1.0) * 100.0, 3)
            if len(vol) >= 24:
                row["volume_24h"] = round(sum(vol[:24]), 0)
            fr = netutil.get_json("https://www.okx.com/api/v5/public/funding-rate?instId=%s-USDT-SWAP" % c, tries=3, pause=0.15)["data"]
            if fr:
                row["funding_8h"] = float(fr[0]["fundingRate"])
        except Exception as e:  # noqa: BLE001
            row["error"] = str(e)[:80]
        out[c] = row or None
    if not any(r and not r.get("error") for r in out.values()):
        raise netutil.NetError("OKX tok: nijedna kovanica nije uspela")
    return out


# ---------------------------------------------------------------- Binance javni arhiv: dnevne derivatske osobine po kovanici
def _zscore(vals, x, min_n=15):
    h = [v for v in vals if v is not None]
    if x is None or len(h) < min_n or st.pstdev(h) <= 0:
        return None
    return round((x - st.mean(h)) / st.pstdev(h), 2)


def bn_features(days):
    """days: {datum: osobine|None} -> osobine poslednjeg dana + z-skorovi (30 d). None kad nema podataka."""
    keys = sorted(d for d, v in days.items() if v)
    if len(keys) < 3:
        return None
    last = days[keys[-1]]
    prev = lambda n: days[keys[-1 - n]] if len(keys) > n else None  # noqa: E731
    out = {"date": keys[-1]}
    for n in (1, 3, 7):
        p = prev(n)
        out["oi_chg_%d" % n] = round((last["oi_amt"] / p["oi_amt"] - 1.0) * 100.0, 3) if p and p.get("oi_amt") and last.get("oi_amt") else None
    for k in ("top_acc_ls", "top_pos_ls", "glob_ls", "taker"):
        out[k] = last.get(k)
        out[k + "_z"] = _zscore([days[d].get(k) for d in keys[-31:-1]], last.get(k))
    return out


def collect_binance_daily(symbols, path, now_ms, days=45, workers=10, fetch=bb.fetch_day, today=None, budget_s=150.0, chunk=120):
    """Dopunjava lokalni kes (path) dnevnim fajlovima sa data.binance.vision za zadate Binance simbole i racuna osobine.
    symbols: {HL simbol: Binance simbol}. Prvi put vuce `days` dana, posle samo nedostajuce."""
    today = today or dt.datetime.fromtimestamp(now_ms / 1000, dt.timezone.utc).date()
    want = [(today - dt.timedelta(days=i)).isoformat() for i in range(days, 0, -1)]
    store = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                store = json.load(f)
        except (OSError, ValueError):
            store = {}
    cutoff = (today - dt.timedelta(days=3)).isoformat()
    jobs = [(b, d) for b in set(symbols.values()) for d in want if d not in store.get(b, {})]
    stats = {"jobs": len(jobs), "ok": 0, "missing": 0, "error": 0, "deferred": 0}
    keep = set(want)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def save():
        pruned = {b: {d: v for d, v in days_.items() if d in keep} for b, days_ in store.items()}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(pruned, f, separators=(",", ":"), sort_keys=True)
        os.replace(tmp, path)
    deadline = time.time() + budget_s
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i in range(0, len(jobs), chunk):
            if time.time() > deadline:  # vremenski budzet: sutra/sledeci krug nastavlja (prvi put vuce dosta fajlova)
                stats["deferred"] = len(jobs) - i
                break
            part = jobs[i:i + chunk]
            for (b, d), (status, feats) in zip(part, ex.map(lambda j: fetch(j[0], j[1]), part)):
                if status == "ok" and feats:
                    store.setdefault(b, {})[d] = {k: feats.get(k) for k in ("oi_amt", "oi_val", "top_acc_ls", "top_pos_ls", "glob_ls", "taker")}
                    stats["ok"] += 1
                elif status == "missing" or (status == "ok" and not feats):
                    if d < cutoff:
                        store.setdefault(b, {})[d] = None
                    stats["missing"] += 1
                else:
                    stats["error"] += 1
            save()
    save()
    coins = {}
    for hl, b in symbols.items():
        ft = bn_features(store.get(b, {}))
        if ft:
            coins[hl] = ft
    if not coins:
        raise netutil.NetError("Binance dnevni: nema podataka (%s)" % json.dumps(stats))

    def med(k):
        v = [c[k] for c in coins.values() if c.get(k) is not None]
        return round(st.median(v), 4) if v else None
    glob = [c["glob_ls"] for c in coins.values() if c.get("glob_ls") is not None]
    agg = {"n_coins": len(coins), "oi_chg_1_med": med("oi_chg_1"), "oi_chg_3_med": med("oi_chg_3"), "oi_chg_7_med": med("oi_chg_7"), "glob_ls_med": med("glob_ls"),
           "top_acc_ls_med": med("top_acc_ls"), "top_pos_ls_med": med("top_pos_ls"), "taker_med": med("taker"),
           "glob_ls_hi_share": round(sum(1 for g in glob if g > 1.5) / len(glob), 3) if glob else None,
           "oi_up_share_7d": round(sum(1 for c in coins.values() if (c.get("oi_chg_7") or 0) > 0) / len(coins), 3)}
    return {"asof": max(c["date"] for c in coins.values()), "fetch": stats, "agg": agg, "coins": coins}


# ---------------------------------------------------------------- on-chain (CoinMetrics community, BTC)
def collect_onchain(now_ms):
    rows = netutil.get_json("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=AdrActCnt,TxCnt&frequency=1d&page_size=45&paging_from=end",
                            tries=3)["data"]
    today = dt.datetime.fromtimestamp(now_ms / 1000, dt.timezone.utc).date().isoformat()
    rows = sorted((r for r in rows if r["time"][:10] < today), key=lambda r: r["time"])  # tekuci dan je nepotpun
    adr = [float(r["AdrActCnt"]) for r in rows if r.get("AdrActCnt")]
    tx = [float(r["TxCnt"]) for r in rows if r.get("TxCnt")]
    if len(adr) < 10:
        raise netutil.NetError("CoinMetrics: premalo dana")
    return {"asof": rows[-1]["time"][:10], "btc_adr_last": adr[-1], "btc_adr_z": _zscore(adr[:-1], adr[-1]), "btc_adr_chg_7d_pct": round((adr[-1] / adr[-8] - 1.0) * 100.0, 2) if len(adr) > 8 else None,
            "btc_tx_last": tx[-1] if tx else None, "btc_tx_z": _zscore(tx[:-1], tx[-1]) if tx else None}


# ---------------------------------------------------------------- GDELT: ton svetskih vesti (dnevno, jedan upit na 6 s)
def collect_gdelt(now_ms, queries=GDELT_QUERIES, pause=6.5):
    out = {}
    for i, (name, q) in enumerate(queries.items()):
        if i:
            time.sleep(pause)
        try:
            j = netutil.get_json("https://api.gdeltproject.org/api/v2/doc/doc?query=%s&mode=timelinetone&format=json&timespan=7d" % urllib.parse.quote(q), tries=2, pause=0)
            data = j["timeline"][0]["data"]
            vals = [float(p["value"]) for p in data if p.get("value") is not None]
            if len(vals) < 20:
                out[name] = None
                continue
            last24 = vals[-96:] if len(vals) >= 96 else vals[-len(vals) // 2:]
            base = vals[:-len(last24)] or vals
            out[name] = {"tone_24h": round(sum(last24) / len(last24), 3), "tone_prev": round(sum(base) / len(base), 3), "n": len(vals)}
            out[name]["tone_chg"] = round(out[name]["tone_24h"] - out[name]["tone_prev"], 3)
        except Exception:  # noqa: BLE001
            out[name] = None
    if not any(out.values()):
        raise netutil.NetError("GDELT: nijedan upit nije uspeo (limit?)")
    return out
