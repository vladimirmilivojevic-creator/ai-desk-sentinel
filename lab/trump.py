"""Trump objave kao izvor podataka: recnik tema (config/trump_tags.json), parsiranje RSS-a trumpstruth.org, brojke za osobine i unapred merenje reakcije cena.
Pravilo ustava (odeljak 3 i 9): tekst objava je NEPOUZDAN podatak. Ovde se tekst koristi samo za odredjivanje tema u ovom modulu; na disk, u briefing i
AI ulaze samo imena tema, brojevi i id-jevi. Nedostupno = None, nikad izmisljeno. Samo stdlib."""
import html
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from . import netutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEED_URL = "https://trumpstruth.org/feed"
HOUR = 3600 * 1000
HORIZONS = (1, 4, 24)          # sati posle ulaza
KEEP_EVENTS = 400              # koliko dogadjaja ostaje u data/trump_events.json
NS_TRUTH = "{https://truthsocial.com/ns}"


def load_lexicon(path=None):
    path = path or os.path.join(ROOT, "config", "trump_tags.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    lex = {"raw": raw, "topics": {k: re.compile(v["re"], re.I) for k, v in raw["topics"].items()},
           "companies": {k: re.compile(v["re"], re.I) for k, v in raw["companies"].items()}, "shout": raw.get("shout") or {}}
    return lex


def clean_html(s):
    s = re.sub(r"<br\s*/?>|</p>", "\n", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def is_repost(text):
    t = (text or "").lstrip()
    return t.startswith("RT ") or t.startswith("RT:") or t.startswith("RT @")


def tag_text(text, lex):
    """Vraca {"topics": [...], "companies": [...], "shout": bool, "rt": bool, "n": duzina}. Repost (RT) nema Trumpove reci pa nema ni tema."""
    text = text or ""
    rt = is_repost(text)
    out = {"topics": [], "companies": [], "shout": False, "rt": rt, "n": len(text)}
    if rt or not text.strip():
        return out
    out["topics"] = [k for k, rx in lex["topics"].items() if rx.search(text)]
    out["companies"] = [k for k, rx in lex["companies"].items() if rx.search(text)]
    sh = lex.get("shout") or {}
    letters = [c for c in text if c.isalpha()]
    if sh and len(letters) >= sh.get("min_letters", 20):
        out["shout"] = sum(1 for c in letters if c.isupper()) / len(letters) >= sh.get("min_upper_ratio", 0.6)
    return out


def parse_feed(xml_text, lex):
    """RSS -> lista dogadjaja {id, ts_ms, topics, companies, shout, rt, n} (BEZ teksta), najnoviji prvi."""
    root = ET.fromstring(xml_text)
    out = []
    for it in root.iter("item"):
        oid = it.findtext(NS_TRUTH + "originalId") or it.findtext("guid") or ""
        pub = it.findtext("pubDate")
        if not oid or not pub:
            continue
        try:
            ts = int(parsedate_to_datetime(pub).astimezone(timezone.utc).timestamp() * 1000)
        except (TypeError, ValueError):
            continue
        tags = tag_text(clean_html(it.findtext("description")), lex)
        tags.update(id=str(oid), ts_ms=ts)
        out.append(tags)
    out.sort(key=lambda e: -e["ts_ms"])
    return out


def summarize(events, now_ms):
    """Brojke za osobine i briefing iz dogadjaja (bez teksta)."""
    def n_since(h, pred=lambda e: True):
        return sum(1 for e in events if e["ts_ms"] >= now_ms - h * HOUR and pred(e))
    own = lambda e: not e.get("rt")  # noqa: E731
    res = {"posts_1h": n_since(1, own), "posts_4h": n_since(4, own), "posts_24h": n_since(24, own), "rt_24h": n_since(24, lambda e: e.get("rt")),
           "shout_24h": n_since(24, lambda e: e.get("shout")), "company_24h": n_since(24, lambda e: bool(e.get("companies")))}
    topics = sorted({t for e in events for t in e.get("topics", [])})
    res["topics_24h"] = {t: n_since(24, lambda e, t=t: t in e.get("topics", [])) for t in topics}
    res["topics_4h"] = {t: n_since(4, lambda e, t=t: t in e.get("topics", [])) for t in topics}
    mine = [e["ts_ms"] for e in events if own(e)]
    res["last_age_min"] = round((now_ms - max(mine)) / 60000.0, 1) if mine else None
    return res


# ---------------------------------------------------------------- unapred merenje reakcije cena (marks iz satnog skupljanja)
def _hour_ceil(ms):
    return -(-ms // HOUR) * HOUR


def update_reactions(store, events, marks, now_ms, instruments):
    """store = {"events": {id: {...}}}. Za svaku NOVU objavu sa temom pamti 'prvu objavu teme u UTC danu' (dogadjaj), belezi cene pri ulazu (prvi pun sat najmanje
    55 min posle objave, jer toliko kasnimo) i popunjava prinose posle 1/4/24 h. Prinos = marks sada / marks pri ulazu - 1, u %.
    marks: {hl_simbol: cena} sa ovog sata; instruments: lista hl simbola koji se mere."""
    ev = store.setdefault("events", {})
    seen_day = {(r["topic"], r["day"]) for r in ev.values()}
    for e in sorted(events, key=lambda x: x["ts_ms"]):
        if e.get("rt"):
            continue
        day = e["ts_ms"] // (24 * HOUR)
        labels = [("t:" + t) for t in e.get("topics", [])] + [("c:" + c) for c in e.get("companies", [])] + (["shout"] if e.get("shout") else [])
        for lab in labels:
            key = "%s|%s" % (e["id"], lab)
            entry_t = _hour_ceil(e["ts_ms"] + 55 * 60000)
            if key in ev or (lab, day) in seen_day or now_ms - entry_t >= 2 * HOUR:  # propusten ulaz (feed ima i starije objave) se ne belezi
                continue
            seen_day.add((lab, day))
            ev[key] = {"topic": lab, "day": day, "ts_ms": e["ts_ms"], "id": e["id"], "entry_t": entry_t, "entry": None, "out": {}}
    for r in ev.values():
        if r["entry"] is None and now_ms >= r["entry_t"] and now_ms - r["entry_t"] < 2 * HOUR:
            r["entry"] = {s: marks[s] for s in instruments if marks.get(s)}
        if not r["entry"]:
            continue
        for h in HORIZONS:
            due = r["entry_t"] + h * HOUR
            if str(h) not in r["out"] and now_ms >= due and now_ms - due < 3 * HOUR + (h // 24) * 3 * HOUR:
                r["out"][str(h)] = {s: round((marks[s] / p - 1.0) * 100.0, 4) for s, p in r["entry"].items() if marks.get(s) and p}
    # stari dogadjaji odlaze (ostaje najnovijih KEEP_EVENTS)
    if len(ev) > KEEP_EVENTS:
        for k in sorted(ev, key=lambda k: ev[k]["ts_ms"])[:len(ev) - KEEP_EVENTS]:
            ev.pop(k)
    return store


def reaction_summary(store, min_n=1):
    """Po temi i horizontu: n i srednji prinos po instrumentu (samo opis; zakljucak daje studija i tek posle n >= 10 dana)."""
    from statistics import mean
    agg = {}
    for r in (store.get("events") or {}).values():
        for h, rets in r["out"].items():
            for s, v in rets.items():
                agg.setdefault((r["topic"], h), {}).setdefault(s, []).append(v)
    out = {}
    for (topic, h), by in sorted(agg.items()):
        out.setdefault(topic, {})[h] = {s: {"n": len(v), "mean": round(mean(v), 3), "pos": round(sum(1 for x in v if x > 0) / len(v), 2)} for s, v in sorted(by.items()) if len(v) >= min_n}
    return out


def collect_trump(now_ms, lex=None, fetch=None, store_path=None, instruments=(), marks=None):
    """Satni zadatak: RSS -> brojke (summary) + unapred reakcije. Vraca recnik koji ide u data/trump.json. Baca NetError ako izvor nije dostupan."""
    lex = lex or load_lexicon()
    fetch = fetch or (lambda: netutil.get_text(FEED_URL, ua=netutil.BROWSER_UA, timeout=25, tries=3))
    events = parse_feed(fetch(), lex)
    if not events:
        raise netutil.NetError("trumpstruth: prazan feed")
    store = {}
    if store_path and os.path.exists(store_path):
        try:
            with open(store_path, encoding="utf-8") as f:
                store = json.load(f)
        except (OSError, ValueError):
            store = {}
    update_reactions(store, events, marks or {}, now_ms, list(instruments))
    if store_path:
        tmp = store_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, store_path)
    out = summarize(events, now_ms)
    out["feed_oldest_utc"] = datetime.fromtimestamp(min(e["ts_ms"] for e in events) / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    out["reactions"] = reaction_summary(store)
    out["n_events"] = len(store.get("events") or {})
    return out
