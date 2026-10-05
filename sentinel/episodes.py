"""Epizode: jedan dogadjaj = tema + grupa instrumenata. Otvara se na prvom N2+, zatvara posle mira.
Ponovno obavestavanje samo pri eskalaciji nivoa ili novom koraku pomaka, uz hladjenje."""

RANK = {None: 0, "N1": 1, "N2": 2, "N3": 3}


def step(theme, ev, psigs, now, episodes, cfg):
    """episodes = dict 'open' -> {tema: epizoda}. Vraca None ili {'kind','episode'}."""
    ec = cfg["episode"]
    ep = episodes.get(theme)
    alert = RANK[ev["tier"]] >= 2
    if not alert:
        if ep and now - ep["last_active"] >= ec["close_after_min"] * 60:
            del episodes[theme]
            return {"kind": "closed", "episode": ep}
        return None
    cur = {p["key"]: p for p in psigs if p["key"] in ev["instruments"]}
    if not ep:
        ep = {"opened": now, "last_active": now, "last_fire": now, "last_tier": ev["tier"],
              "ref": {k: (p.get("m60") or 0.0) for k, p in cur.items()}, "n": 1}
        episodes[theme] = ep
        return {"kind": "open", "episode": ep}
    ep["last_active"] = now
    escalated = RANK[ev["tier"]] > RANK[ep["last_tier"]]
    stepped = False
    for k, p in cur.items():
        ref = ep["ref"].get(k, 0.0)
        m = p.get("m60") or 0.0
        thr = ec["step_mult"] * p["eff60"]
        if (m >= 0) == (ref >= 0) and abs(m) >= abs(ref) + thr:
            stepped = True
    cooled = now - ep["last_fire"] >= ec["cooldown_min"] * 60
    if escalated or (stepped and cooled):
        ep["last_fire"] = now
        ep["last_tier"] = ev["tier"] if escalated else ep["last_tier"]
        ep["ref"] = {k: (p.get("m60") or 0.0) for k, p in cur.items()}
        ep["n"] = ep.get("n", 1) + 1
        return {"kind": "escalate" if escalated else "step", "episode": ep}
    return None


def fire_allowed(fires, now, cfg):
    """Globalna ogranicenja okidanja mozga (fires = lista vremena). Vraca (ok, razlog)."""
    f = cfg["fire"]
    if not cfg.get("fire_enabled"):
        return False, "fire_enabled=false (senka)"
    if fires and now - fires[-1] < f["min_gap_min"] * 60:
        return False, "razmak manji od %d min" % f["min_gap_min"]
    if sum(1 for t in fires if now - t < 3600) >= f["per_hour"]:
        return False, "limit po satu"
    if sum(1 for t in fires if now - t < 86400) >= f["per_day"]:
        return False, "limit po danu"
    return True, "ok"
