"""Adapteri izvora. Svaki vraca obicne podatke ili baca SourceError."""
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from .util import BROWSER_UA, SourceError, http

HL = "https://api.hyperliquid.xyz/info"


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def hl_ctx(dex):
    """Zive cene sa Hyperliquid-a (isto tržište kao Liquid). dex='xyz' ili '' za glavni."""
    body = {"type": "metaAndAssetCtxs"}
    if dex:
        body["dex"] = dex
    _, raw = http("POST", HL, body)
    meta, ctxs = json.loads(raw)
    out = {}
    for u, c in zip(meta["universe"], ctxs):
        px = _f(c.get("markPx"))
        if px:
            out[u["name"]] = {"mark": px, "prev_day": _f(c.get("prevDayPx")), "funding": _f(c.get("funding")),
                              "oi": _f(c.get("openInterest"))}
    if not out:
        raise SourceError("empty ctx")
    return out


def hl_candles(coin, interval, minutes_back):
    now = int(time.time() * 1000)
    body = {"type": "candleSnapshot",
            "req": {"coin": coin, "interval": interval, "startTime": now - minutes_back * 60000, "endTime": now}}
    _, raw = http("POST", HL, body)
    rows = json.loads(raw)
    # (kraj sveće u sekundama, close)
    return [(r["T"] / 1000.0, float(r["c"])) for r in rows]


def yahoo_series(symbol, interval="5m", rng="1d"):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=%s&range=%s" % (
        urllib.parse.quote(symbol), interval, rng)
    _, raw = http("GET", url, ua=BROWSER_UA)
    r = json.loads(raw)["chart"]["result"][0]
    step = 300 if interval == "5m" else 3600
    out = [(t + step, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None]
    if not out:
        raise SourceError("empty yahoo")
    return out


def _rss_items(raw, default_source):
    root = ET.fromstring(raw)
    items = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        pub = it.findtext("pubDate")
        if not title or not pub:
            continue
        try:
            ts = parsedate_to_datetime(pub).timestamp()
        except (TypeError, ValueError):
            continue
        src = it.find("source")
        source = (src.text or "").strip() if src is not None and src.text else default_source
        if src is not None and title.endswith(" - " + source):
            title = title[: -(len(source) + 3)]
        items.append({"title": title, "source": source or default_source, "ts": ts})
    return items


def gnews(query):
    url = "https://news.google.com/rss/search?q=%s&hl=en-US&gl=US&ceid=US:en" % urllib.parse.quote_plus(query)
    _, raw = http("GET", url, ua=BROWSER_UA)
    return _rss_items(raw, "Google News")


def rss(url, name):
    _, raw = http("GET", url, ua=BROWSER_UA)
    return _rss_items(raw, name)


def polymarket(limit=120):
    url = ("https://gamma-api.polymarket.com/markets?active=true&closed=false&order=volume24hr&ascending=false&limit=%d"
           % limit)
    _, raw = http("GET", url)
    out = []
    for m in json.loads(raw):
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
            p = float(prices[0])
        except (ValueError, IndexError, TypeError):
            continue
        out.append({"id": str(m.get("id")), "q": m.get("question") or "", "p": p,
                    "vol24": _f(m.get("volume24hr")) or 0.0})
    if not out:
        raise SourceError("empty polymarket")
    return out


def gdelt_timeline(query, timespan="3d"):
    url = ("https://api.gdeltproject.org/api/v2/doc/doc?query=%s&mode=timelinevol&timespan=%s&format=json"
           % (urllib.parse.quote(query), timespan))
    _, raw = http("GET", url, retries=1, timeout=20)
    data = json.loads(raw)["timeline"][0]["data"]
    return [(d["date"], float(d["value"])) for d in data]
