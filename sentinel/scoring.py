"""Cista logika ocenjivanja: bez mreze, bez upisa, lako se testira.

Porodice signala (nezavisni izvori):
  P  cena (1, a 2 ako druga cena potvrdi)      PX izuzetno veliki pomak (>= 2x prag)
  X  unakrsna imovina                           M  prediction markets (Polymarket)
  H  naslovi iz >= 2 izdavaca                   O  zvanicni izvori (Fed, EIA)
  V  GDELT (iskljuceno dok se ne proveri)
Nivoi: N1 jedna porodica (samo beleška) | N2 ocena >= 3,0 i P | N3 ocena >= 4,5, P >= 2x prag, >= 3 porodice.
Vest bez cenovnog pomaka nikad ne prelazi N1.
"""
import re
import statistics

from .util import pct


# ---------- cene ----------
def clamp_series(series, now):
    out = []
    for t, p in series:
        out.append((min(t, now), p))
    return out


def ref_price(series, now, minutes):
    target = now - minutes * 60
    ref = None
    for t, p in series:
        if t <= target:
            ref = p
        else:
            break
    return ref


def sigma_from_hourly(closes):
    """Standardna devijacija jednocasovnih promena (u procentima)."""
    if len(closes) < 24:
        return None
    rets = [pct(b, a) for a, b in zip(closes, closes[1:]) if a]
    if len(rets) < 20:
        return None
    return statistics.pstdev(rets)


def price_signal(inst, series, provider, second_series, sigma60, cfg, now):
    base = {"key": inst["key"], "name": inst["name"], "class": inst["class"], "theme": inst["theme"],
            "provider": provider, "tradable": inst.get("tradable", True)}
    if not series:
        return dict(base, stale=True, reason="nema serije")
    series = clamp_series(series, now)
    last_t, last = series[-1]
    age = (now - last_t) / 60.0
    if age > cfg["stale_minutes"]:
        return dict(base, stale=True, px=last, age_min=round(age, 1), reason="stara cena")
    r60 = ref_price(series, now, 60)
    r240 = ref_price(series, now, 240)
    m60 = pct(last, r60) if r60 else None
    m240 = pct(last, r240) if r240 else None
    thr60, thr240 = inst["thr60"], inst["thr240"]
    sm = cfg["sigma_mult"]
    eff60 = max(thr60, sm * sigma60) if sigma60 else thr60
    eff240 = max(thr240, sm * sigma60 * 2.0) if sigma60 else thr240
    trig60 = m60 is not None and abs(m60) >= eff60
    trig240 = m240 is not None and abs(m240) >= eff240
    rel60 = abs(m60) / thr60 if m60 is not None else 0.0
    rel240 = abs(m240) / thr240 if m240 is not None else 0.0
    rel = max(rel60, rel240)
    mv = m60 if rel60 >= rel240 else m240
    direction = "up" if (mv or 0) > 0 else "down"
    confirmed = False
    if (trig60 or trig240) and second_series:
        s2 = clamp_series(second_series, now)
        use60 = trig60
        r2 = ref_price(s2, now, 60 if use60 else 240)
        if r2:
            m2 = pct(s2[-1][1], r2)
            need = 0.6 * (thr60 if use60 else thr240)
            confirmed = (m2 > 0) == ((m60 if use60 else m240) > 0) and abs(m2) >= need
    return dict(base, stale=False, px=last, age_min=round(age, 1), m60=m60, m240=m240, rel=rel,
                trig=bool(trig60 or trig240), dir=direction, confirmed=confirmed,
                eff60=eff60, sigma60=sigma60)


def cross_signal(psigs, cfg, vix_px=None):
    c = cfg["cross"]
    near = [p for p in psigs if not p.get("stale") and p.get("rel", 0) >= c["min_strength"]]
    classes = {p["class"] for p in near}
    reasons = []
    if len(near) >= c["min_instruments"] and len(classes) >= c["min_classes"]:
        reasons.append("%d instrumenata u %d klase se pomera" % (len(near), len(classes)))
    if vix_px and vix_px >= c["vix_level"]:
        reasons.append("VIX %.1f >= %.0f" % (vix_px, c["vix_level"]))
    return {"fired": bool(reasons), "reasons": reasons, "instruments": [p["key"] for p in near]}


# ---------- vesti ----------
def _norm(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def _kw_regex(words):
    return {w: re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in words}


def tag_themes(text, theme_words):
    tl = text.lower()
    return [th for th, ws in theme_words.items() if any(re.search(r"\b" + re.escape(w) + r"\b", tl) for w in ws)]


def headline_signal(items, now, cfg, q):
    h = cfg["headlines"]
    kw = _kw_regex(q["keywords"])
    seen, scored = set(), []
    for it in items:
        age = (now - it["ts"]) / 60.0
        if age > h["window_min"] or age < -5:
            continue
        key = _norm(it["title"])[:80]
        if key in seen:
            continue
        seen.add(key)
        s = sum(q["keywords"][w] for w, rx in kw.items() if rx.search(it["title"]))
        if s <= 0:
            continue
        themes = tag_themes(it["title"], q["theme_words"]) or ["GEO"]
        scored.append({"title": it["title"], "source": it["source"], "age_min": round(age, 1), "score": s,
                       "themes": themes})
    per = {}
    geo_themes = ("OIL", "GOLD", "EQUITY")
    for th in ("OIL", "GOLD", "EQUITY", "CRYPTO", "MACRO"):
        own = [x for x in scored if th in x["themes"]]
        geo = [x for x in scored if "GEO" in x["themes"]] if th in geo_themes else []
        use = own + geo
        pubs = {x["source"].lower() for x in use}
        sc = sum(x["score"] for x in use)
        per[th] = {"fired": sc >= h["min_score"] * 0.5 and len(pubs) >= h["min_publishers"] and
                   sum(x["score"] for x in scored) >= h["min_score"],
                   "score": sc, "publishers": sorted(pubs),
                   "items": sorted(use, key=lambda x: -x["score"])[:5]}
    return {"themes": per, "n": len(scored), "top": sorted(scored, key=lambda x: -x["score"])[:5]}


def official_signal(items, now, cfg, q):
    win = cfg["official"]["window_min"]
    hits = []
    for it in items:
        age = (now - it["ts"]) / 60.0
        if age > win or age < -5:
            continue
        tl = it["title"].lower()
        if any(k in tl for k in q["official_keywords"]):
            hits.append({"title": it["title"], "source": it["source"], "age_min": round(age, 1),
                         "themes": tag_themes(it["title"], q["theme_words"]) or ["MACRO"]})
    return hits


def prediction_signal(markets, hist, now, cfg, q):
    """Azurira istoriju (hist se menja) i vraca trzista sa pomakom >= min_delta za ~ref_min minuta."""
    pc = cfg["prediction"]
    kws = q["prediction_keywords"]
    movers = []
    for m in markets:
        ql = m["q"].lower() + " "
        if not any(k in ql for k in kws):
            continue
        h = hist.setdefault(m["id"], [])
        h.append([now, m["p"]])
        h[:] = [x for x in h if now - x[0] <= pc["keep_min"] * 60]
        ref = None
        for t, p in h:
            if now - t >= pc["ref_min"] * 60:
                ref = p
        if ref is not None and m["vol24"] >= pc["min_volume24h"] and abs(m["p"] - ref) >= pc["min_delta"]:
            movers.append({"id": m["id"], "q": m["q"], "p": m["p"], "ref": ref, "delta": m["p"] - ref,
                           "themes": tag_themes(m["q"], q["theme_words"]) or ["GEO"]})
    # cistimo istoriju trzista koja vise ne dolaze
    live = {m["id"] for m in markets}
    for k in list(hist):
        if k not in live:
            del hist[k]
    return movers


def gdelt_signal(timeline, cfg):
    """timeline: [(datum 'YYYYMMDDTHHMMSSZ', vrednost)]. Poredi poslednju tacku sa medijanom istog termina ranijih dana."""
    if len(timeline) < 50:
        return {"fired": False, "ratio": None}
    last_d, last_v = timeline[-1]
    slot = last_d[9:13]
    prev = [v for d, v in timeline[:-1] if d[9:13] == slot and d[:8] != last_d[:8]]
    if len(prev) < 2:
        return {"fired": False, "ratio": None}
    base = statistics.median(prev)
    ratio = last_v / base if base > 0 else None
    return {"fired": bool(ratio and ratio >= cfg["gdelt"]["ratio"]), "ratio": ratio}


# ---------- ocena po temi ----------
def tier_for(fams, p_rel, cfg):
    t = cfg["tiers"]
    score = sum(fams.values())
    p_present = "P" in fams
    if p_present and score >= t["n3_score"] and p_rel >= t["n3_p_mult"] and len(fams) >= t["n3_min_families"]:
        return "N3", score
    if p_present and score >= t["n2_score"]:
        return "N2", score
    if fams:
        return "N1", score
    return None, score


def evaluate_themes(psigs, cross, head, offi, movers, gdelt, cfg):
    w = cfg["weights"]
    themes = sorted({p["theme"] for p in psigs if p["theme"] != "MACRO"})
    out = {}
    for th in themes:
        mine = [p for p in psigs if p["theme"] == th and not p.get("stale") and p.get("trig")]
        fams, why = {}, {}
        p_rel = 0.0
        if mine:
            p_rel = max(p["rel"] for p in mine)
            fams["P"] = w["P2"] if any(p["confirmed"] for p in mine) else w["P1"]
            why["P"] = ", ".join("%s %+.1f%%/60m" % (p["name"], p["m60"] if p["m60"] is not None else 0) for p in mine)
            if p_rel >= 2.0:
                fams["PX"] = w["P1"]
                why["PX"] = "pomak %.1fx preko praga" % p_rel
        if cross["fired"]:
            fams["X"] = w["X"]
            why["X"] = "; ".join(cross["reasons"])
        hh = head["themes"].get(th)
        if hh and hh["fired"]:
            fams["H"] = w["H"]
            why["H"] = "%d naslova, izdavaci: %s" % (len(hh["items"]), ", ".join(hh["publishers"][:4]))
        om = [o for o in offi if th in o["themes"] or (th in ("OIL", "GOLD", "EQUITY") and "MACRO" in o["themes"])]
        if om:
            fams["O"] = w["O"]
            why["O"] = om[0]["title"][:80]
        mm = [m for m in movers if th in m["themes"] or (m["themes"] == ["GEO"] and th in ("OIL", "GOLD", "EQUITY"))]
        if mm:
            fams["M"] = w["M"]
            why["M"] = "%s %+.0f p.p." % (mm[0]["q"][:60], mm[0]["delta"] * 100)
        if gdelt.get("fired"):
            fams["V"] = w["V"]
            why["V"] = "GDELT obim %.1fx" % gdelt["ratio"]
        tier, score = tier_for(fams, p_rel, cfg)
        d = [p for p in mine]
        direction = None
        if d:
            top = max(d, key=lambda p: p["rel"])
            direction = top["dir"]
        out[th] = {"tier": tier, "score": round(score, 2), "families": fams, "why": why, "p_rel": round(p_rel, 2),
                   "direction": direction, "instruments": [p["key"] for p in mine]}
    return out
