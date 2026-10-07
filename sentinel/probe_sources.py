"""Provera dostupnosti novih izvora podataka IZ GitHub Actions okruzenja (US/Azure IP): sta radi, koliko traje, sta je blokirano.
Rezultat: probe_results.json (workflow ga objavljuje na granu `probe`) i tabela na stdout. Ne trguje, ne cuva tajne, ne stampa kljuceve.
Upotreba: python -m sentinel.probe_sources [izlaz.json]"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
MAX_READ = 400_000


def _day(offset=0):
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() + offset * 86400))


def endpoints(now=None):
    """Lista izvora: id, metod, url, telo, zaglavlja, opcioni kljuc (env), provera odgovora."""
    now = now or int(time.time())
    ms = now * 1000

    def js(t):
        return json.loads(t)

    return [
        {"id": "hl_predicted_fundings", "method": "POST", "url": "https://api.hyperliquid.xyz/info", "body": {"type": "predictedFundings"},
         "check": lambda t: len(js(t)) > 50},
        {"id": "hl_l2book", "method": "POST", "url": "https://api.hyperliquid.xyz/info", "body": {"type": "l2Book", "coin": "BTC"},
         "check": lambda t: len(js(t)["levels"]) == 2},
        {"id": "hl_meta_ctx_xyz", "method": "POST", "url": "https://api.hyperliquid.xyz/info", "body": {"type": "metaAndAssetCtxs", "dex": "xyz"},
         "check": lambda t: len(js(t)[0]["universe"]) > 50},
        {"id": "hl_leaderboard", "method": "GET", "url": "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard", "partial": True,
         "check": lambda t: '"leaderboardRows"' in t},
        {"id": "deribit_dvol", "method": "GET", "url": "https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp=%d&end_timestamp=%d&resolution=3600" % (ms - 6 * 3600000, ms),
         "check": lambda t: len(js(t)["result"]["data"]) >= 2},
        {"id": "deribit_options_summary", "method": "GET", "url": "https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option", "partial": True,
         "check": lambda t: '"open_interest"' in t},
        {"id": "binance_fapi_oi_hist", "method": "GET", "url": "https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=1h&limit=3",
         "check": lambda t: len(js(t)) >= 2},
        {"id": "binance_fapi_top_lsr", "method": "GET", "url": "https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=1h&limit=3",
         "check": lambda t: len(js(t)) >= 2},
        {"id": "bybit_oi", "method": "GET", "url": "https://api.bybit.com/v5/market/open-interest?category=linear&symbol=BTCUSDT&intervalTime=1h&limit=3",
         "check": lambda t: js(t)["retCode"] == 0},
        {"id": "okx_lsr", "method": "GET", "url": "https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio?ccy=BTC&period=1H",
         "check": lambda t: js(t)["code"] == "0"},
        {"id": "binance_vision_metrics", "method": "GET", "url": "https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-%s.zip" % _day(-2),
         "headers": {"Range": "bytes=0-512"}, "check": lambda t: len(t) > 100},
        {"id": "fred_csv", "method": "GET", "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y2Y&cosd=%s" % _day(-10),
         "check": lambda t: t.startswith("observation_date")},
        {"id": "defillama_stablecoins", "method": "GET", "url": "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1", "partial": True,
         "check": lambda t: t.startswith("[{")},
        {"id": "fear_greed", "method": "GET", "url": "https://api.alternative.me/fng/?limit=2", "check": lambda t: len(js(t)["data"]) == 2},
        {"id": "kalshi_markets", "method": "GET", "url": "https://api.elections.kalshi.com/trade-api/v2/markets?limit=1&status=open",
         "check": lambda t: "markets" in js(t)},
        {"id": "wikipedia_pageviews", "method": "GET",
         "url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Bitcoin/daily/%s/%s" % (_day(-6).replace("-", ""), _day(-2).replace("-", "")),
         "check": lambda t: len(js(t)["items"]) >= 2},
        {"id": "forexfactory_week", "method": "GET", "url": "https://nfs.faireconomy.media/ff_calendar_thisweek.json", "ua": BROWSER_UA,
         "check": lambda t: len(js(t)) > 5},
        {"id": "nasdaq_earnings", "method": "GET", "url": "https://api.nasdaq.com/api/calendar/earnings?date=%s" % _day(1), "ua": BROWSER_UA,
         "check": lambda t: "rows" in t},
        {"id": "yahoo_vix3m", "method": "GET", "url": "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX3M?range=5d&interval=1d", "ua": BROWSER_UA,
         "check": lambda t: js(t)["chart"]["result"] is not None},
        {"id": "coingecko_global", "method": "GET", "url": "https://api.coingecko.com/api/v3/global", "check": lambda t: "data" in js(t)},
        {"id": "coinalyze_exchanges", "method": "GET", "url": "https://api.coinalyze.net/v1/exchanges", "key_env": "COINALYZE_API_KEY", "key_header": "api_key",
         "check": lambda t: len(js(t)) > 3},
        {"id": "finnhub_earnings", "method": "GET", "url": "https://finnhub.io/api/v1/calendar/earnings?from=%s&to=%s" % (_day(0), _day(5)), "key_env": "FINNHUB_API_KEY",
         "key_query": "token", "check": lambda t: "earningsCalendar" in js(t)},
    ]


def fetch(ep, timeout=15):
    """Vraca (status, telo ili None, greska ili None). Kljuc se dodaje samo u zahtev, nikad u izlaz."""
    url = ep["url"]
    headers = {"User-Agent": ep.get("ua", "ai-desk-sentinel/0.2 (public research bot, no trading)")}
    headers.update(ep.get("headers", {}))
    key = os.environ.get(ep["key_env"]) if ep.get("key_env") else None
    if ep.get("key_env"):
        if not key:
            return None, None, "no_key"
        if ep.get("key_header"):
            headers[ep["key_header"]] = key
        if ep.get("key_query"):
            url += ("&" if "?" in url else "?") + "%s=%s" % (ep["key_query"], key)
    data = None
    if ep.get("body") is not None:
        data = json.dumps(ep["body"]).encode()
        headers["Content-Type"] = "application/json"
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=ep["method"])
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(MAX_READ if ep.get("partial") else 5_000_000)
            return r.status, raw.decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        return e.code, None, "HTTP %s" % e.code
    except Exception as e:  # noqa: BLE001
        return None, None, type(e).__name__


def probe_one(ep, timeout=15):
    t0 = time.time()
    status, body, err = fetch(ep, timeout)
    ms = int((time.time() - t0) * 1000)
    out = {"id": ep["id"], "status": status, "ms": ms}
    if err == "no_key":
        out.update(ok=None, note="preskoceno: nema kljuca u secrets")
    elif err:
        out.update(ok=False, note=err)
    else:
        try:
            ok = bool(ep["check"](body))
            out.update(ok=ok, note="radi" if ok else "odgovor nije u ocekivanom obliku")
        except Exception as e:  # noqa: BLE001
            out.update(ok=False, note="neocekivan oblik: %s" % type(e).__name__)
    return out


def run(timeout=15):
    results = []
    for ep in endpoints():
        results.append(probe_one(ep, timeout))
        time.sleep(0.3)
    return {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runner": os.environ.get("RUNNER_NAME", "local"),
            "ok": sum(1 for r in results if r["ok"]), "failed": sum(1 for r in results if r["ok"] is False),
            "skipped": sum(1 for r in results if r["ok"] is None), "results": results}


def main():
    res = run()
    for r in res["results"]:
        mark = {True: "OK  ", False: "FAIL", None: "SKIP"}[r["ok"]]
        print("%s %-26s %5s %6d ms  %s" % (mark, r["id"], r["status"], r["ms"], r["note"]))
    print("ukupno: ok %d, neuspelo %d, preskoceno %d" % (res["ok"], res["failed"], res["skipped"]))
    out = sys.argv[1] if len(sys.argv) > 1 else "probe_results.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
