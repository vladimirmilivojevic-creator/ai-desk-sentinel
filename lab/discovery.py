"""Lovac: stalno trazenje pravila na SIREM univerzumu (akcije sa Liquid-a), bez AI-ja i bez novca.
Dve vrste pravila: RANG (nedeljni izbor najboljeg/najgoreg dela univerzuma po oceni) i DOGADJAJ (nagli skok obima: GME-slicna eksplozija pazni).
Nedeljno: istorijska studija (porodice i granice su unapred upisane u config/discovery.json), FDR preko svih testova, provera na zadnjem delu vremena.
Dnevno: pravilima koja su nagovestaj ili kandidat belezi se izbor unapred (zamrznut u trenutku signala), meri ishod, i tek posle
unapred zadatih kapija pravilo postaje 'potvrdjen'. Samo 'potvrdjen' sme da ode Istrazivacu (desk), i to samo ako to vlasnik dozvoli.
Izlaz: calibration/discovery.{json,md}, discovery/{rules.json, forward.jsonl, radar.json, universe.json}.
Upotreba: python -m lab.discovery weekly|daily [--cache DIR] [--no-write]"""
import datetime as dt
import json
import math
import os
import statistics as st
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from . import stats as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (ai-desk research)"}
ANCHOR = dt.date(1970, 1, 5).toordinal()  # ponedeljak: nedelja = (dan - ANCHOR) // 7 poklapa se sa ISO nedeljom
FAMILIES = ("MOM12_1", "HIGH52", "REV5", "VOLUP", "BRK20", "LOWVOL", "ATTN")
EVENTS = ("SPIKE_UP", "SPIKE_DN", "HIGH_BRK")
TRACKED = ("nagovestaj", "kandidat", "potvrdjen")
CASES = (("GME", "2026-10-03"),)  # opisni slucaj: vlasnikov rucni ulaz (ne ulazi ni u kakav test)
STOCK_OPEN_UTC = (14, 30)  # konzervativno: otvaranje berze (13:30 leti, 14:30 zimi)


def load_cfg(path=None):
    with open(path or os.path.join(ROOT, "config", "discovery.json"), encoding="utf-8") as f:
        return json.load(f)


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _save(path, obj, indent=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, path)


# ------------------------------------------------------------------ cene
def fetch_yahoo(sym, tries=3):
    """Dnevne svece (ispravljene za splitove/dividende) kao dict nizova, ili None."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=6y&interval=1d" % urllib.request.quote(sym, safe="")
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                j = json.load(r)
            res = j["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose")
            b = {"d": [], "o": [], "h": [], "l": [], "c": [], "v": [], "rc": []}
            for i, ts in enumerate(res.get("timestamp") or []):
                o, h, lo, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
                if not (o and h and lo and c) or min(o, h, lo, c) <= 0:
                    continue
                f = (adj[i] / c) if adj and adj[i] else 1.0
                b["d"].append(dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat())
                b["o"].append(o * f)
                b["h"].append(h * f)
                b["l"].append(lo * f)
                b["c"].append(c * f)
                b["v"].append(float(v or 0))
                b["rc"].append(c)
            return b
        except Exception:  # noqa: BLE001  mreza, 404 (nema simbola), 429
            time.sleep(1.5 * (k + 1))
    return None


def load_prices(syms, cache=None, max_age_h=12):
    """{sym: bars}. Keš na disku samo kad je zadat (lokalni rad); u workflow-u se uvek povlaci sveze."""
    def one(sym):
        p = os.path.join(cache, "dy_%s.json" % sym.replace("/", "_").replace("^", "")) if cache else None
        if p and os.path.exists(p) and time.time() - os.path.getmtime(p) < max_age_h * 3600:
            return sym, _load(p, None)
        b = fetch_yahoo(sym)
        if p and b:
            os.makedirs(cache, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(b, f, separators=(",", ":"))
        return sym, b

    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for sym, b in ex.map(one, sorted(set(syms))):
            if b and len(b["c"]) > 0:
                out[sym] = b
    return out


def trim_incomplete(b, now, bars_per_week):
    """Odbacuje poslednju svecu ako dan jos traje: kripto uvek za danasnji UTC dan, akcije pre 22:00 UTC."""
    if not b["d"]:
        return b
    today = now.date().isoformat()
    if b["d"][-1] == today and (bars_per_week == 7 or now.hour < 22):
        return {k: v[:-1] for k, v in b.items()}
    return b


# ------------------------------------------------------------------ osobine i dogadjaji
def features(b, cfg):
    """{porodica: lista ocena po svecama (None gde nema dovoljno istorije)}. Ocena u danu i koristi samo podatke do zatvaranja dana i."""
    f = cfg["families"]
    c, v, n = b["c"], b["v"], len(b["c"])
    out = {k: [None] * n for k in FAMILIES}
    ret = [None] * n
    for i in range(1, n):
        ret[i] = c[i] / c[i - 1] - 1.0
    lb, sk = f["MOM12_1"]["lookback"], f["MOM12_1"]["skip"]
    w52, d5 = f["HIGH52"]["window"], f["REV5"]["days"]
    wv, cap = f["VOLUP"]["window"], f["VOLUP"]["cap"]
    wb, wl = f["BRK20"]["window"], f["LOWVOL"]["window"]
    sa, la = f["ATTN"]["short"], f["ATTN"]["long"]
    for i in range(n):
        if i >= lb:
            out["MOM12_1"][i] = c[i - sk] / c[i - lb] - 1.0
        if i >= w52 - 1:
            out["HIGH52"][i] = c[i] / max(c[i - w52 + 1:i + 1])
        if i >= d5:
            out["REV5"][i] = -(c[i] / c[i - d5] - 1.0)
        if i >= wv and ret[i] is not None:
            avg = sum(v[i - wv:i]) / wv
            if avg > 0:
                out["VOLUP"][i] = ret[i] * min(v[i] / avg, cap)
        if i >= wb:
            out["BRK20"][i] = c[i] / max(c[i - wb:i]) - 1.0
        if i >= wl:
            out["LOWVOL"][i] = -st.pstdev(ret[i - wl + 1:i + 1])
        if i >= la - 1:
            lv = sum(v[i - la + 1:i + 1]) / la
            if lv > 0:
                out["ATTN"][i] = (sum(v[i - sa + 1:i + 1]) / sa) / lv
    return out


def event_flags(b, cfg):
    """{dogadjaj: lista (None ili jacina = odnos obima) po svecama}. Posle pogotka isti simbol miruje event_cooldown_bars svecâ."""
    e, cool = cfg["events"], cfg["event_cooldown_bars"]
    c, v, n = b["c"], b["v"], len(b["c"])
    out = {k: [None] * n for k in EVENTS}
    last = {k: -10 ** 9 for k in EVENTS}
    for i in range(1, n):
        ret = c[i] / c[i - 1] - 1.0
        for k in EVENTS:
            p = e[k]
            w = p["vol_window"]
            if i < w:
                continue
            avg = sum(v[i - w:i]) / w
            if avg <= 0:
                continue
            vr = v[i] / avg
            if vr < p["vol_ratio_min"]:
                continue
            if k == "SPIKE_UP":
                hit = ret >= p["ret_min"]
            elif k == "SPIKE_DN":
                hit = ret <= p["ret_max"]
            else:
                hit = i >= p["window"] and c[i] > max(c[i - p["window"]:i])
            if hit and i - last[k] >= cool:
                out[k][i] = round(vr, 4)
                last[k] = i
    return out


def atr_pct(b, i, n=14):
    """Prosecan pravi raspon poslednjih n dana u % od zatvaranja (ili None)."""
    if i < n:
        return None
    tr = []
    for k in range(i - n + 1, i + 1):
        tr.append(max(b["h"][k] - b["l"][k], abs(b["h"][k] - b["c"][k - 1]), abs(b["l"][k] - b["c"][k - 1])))
    return sum(tr) / n / b["c"][i] * 100.0


# ------------------------------------------------------------------ univerzum i kalendar
def week_index(day_iso):
    return (dt.date.fromisoformat(day_iso).toordinal() - ANCHOR) // 7


def rebalance_dates(cal, weeks, bars_per_week, latest=None):
    """Poslednja sveca svake ISO nedelje u kalendaru (svake `weeks`-te nedelje). Nedelja je 'zavrsena' tek kad je poslednja sveca
    petak (akcije) ili nedelja (kripto), ili je kalendar vec otisao u sledecu nedelju."""
    last = {}
    for d in cal:
        last[week_index(d)] = d
    latest = latest or (cal[-1] if cal else None)
    out = []
    for wi, d in sorted(last.items()):
        if wi % weeks:
            continue
        if latest is not None and week_index(latest) == wi and dt.date.fromisoformat(d).weekday() != (4 if bars_per_week == 5 else 6):
            continue
        out.append(d)
    return out


class Universe:
    """Cene, osobine, dogadjaji i kalendar jednog univerzuma."""

    def __init__(self, name, px, bench, ucfg, cfg):
        self.name, self.px, self.cfg = name, px, cfg
        self.bpw = int(ucfg["bars_per_week"])
        self.cal = list(bench["d"])
        self.idx = {s: {d: i for i, d in enumerate(b["d"])} for s, b in px.items()}
        self.feat = {s: features(b, cfg) for s, b in px.items()}
        self.ev = {s: event_flags(b, cfg) for s, b in px.items()}
        self._um = {}

    def outcome(self, sym, d, H):
        """Prinos u % od otvaranja sledece svece posle d do zatvaranja H svece, ili None. Ulaz je uvek POSLE signala."""
        i = self.idx[sym].get(d)
        if i is None:
            return None
        b, e = self.px[sym], i + 1
        if e + H - 1 >= len(b["c"]) or not b["o"][e]:
            return None
        return (b["c"][e + H - 1] / b["o"][e] - 1.0) * 100.0

    def members(self, fam, d):
        """[(sym, ocena)] za rang-porodicu na datum d, sortirano opadajuce po oceni (ravnopravno po imenu)."""
        rows = []
        for s in self.px:
            i = self.idx[s].get(d)
            if i is None:
                continue
            x = self.feat[s][fam][i]
            if x is not None:
                rows.append((s, x))
        rows.sort(key=lambda r: (-r[1], r[0]))
        return rows

    def flagged(self, fam, d):
        """[(sym, jacina)] simboli sa dogadjajem na datum d, najjaci prvi."""
        rows = []
        for s in self.px:
            i = self.idx[s].get(d)
            if i is None:
                continue
            x = self.ev[s][fam][i]
            if x is not None:
                rows.append((s, x))
        rows.sort(key=lambda r: (-r[1], r[0]))
        return rows

    def universe_mean(self, d, H):
        """Prosecan ishod svih clanova koji imaju svecu na d (ili None ako ih je premalo)."""
        key = (d, H)
        if key not in self._um:
            rs = [self.outcome(s, d, H) for s in self.px]
            rs = [r for r in rs if r is not None]
            self._um[key] = sum(rs) / len(rs) if len(rs) >= self.cfg["min_universe"] else None
        return self._um[key]


def group_size(n, cfg):
    return max(cfg["min_group"], int(round(cfg["quantile"] * n)))


# ------------------------------------------------------------------ istorijska studija
def tstat(vals):
    n = len(vals)
    if n < 3:
        return None
    sd = st.stdev(vals)
    return None if sd == 0 else round(st.mean(vals) / (sd / math.sqrt(n)), 2)


def run_periods(U, cfg, fam, weeks):
    """RANG: lista perioda (datum, long_excess, long_abs, short_excess, short_abs), svi u % posle troska."""
    H, cost, out = weeks * U.bpw, cfg["cost_pct"], []
    for d in rebalance_dates(U.cal, weeks, U.bpw):
        mem = U.members(fam, d)
        rets = {}
        for s, _ in mem:
            r = U.outcome(s, d, H)
            if r is not None:
                rets[s] = r
        mem = [(s, x) for s, x in mem if s in rets]
        n = len(mem)
        if n < cfg["min_universe"]:
            continue
        g = group_size(n, cfg)
        if 2 * g > n:
            continue
        u = sum(rets[s] for s, _ in mem) / n
        top = sum(rets[s] for s, _ in mem[:g]) / g
        bot = sum(rets[s] for s, _ in mem[-g:]) / g
        out.append((d, top - u - cost, top - cost, u - bot - cost, -bot - cost))
    return out


def thin_weeks(rows, H, bpw):
    """rows: lista (datum, a, b, ...). Jedna vrednost po nedelji (prosek), pa samo svaka ceil(H/bpw)-ta nedelja da se periodi ne preklapaju."""
    step = math.ceil(H / bpw)
    byw = {}
    for r in rows:
        byw.setdefault(week_index(r[0]), []).append(r)
    out = []
    for wi in sorted(byw):
        if wi % step:
            continue
        g = byw[wi]
        cols = []
        for k in range(1, len(g[0])):
            v = [x[k] for x in g if x[k] is not None]
            cols.append(sum(v) / len(v) if v else None)
        out.append((g[-1][0],) + tuple(cols))
    return out


def event_periods(U, cfg, fam, H):
    """DOGADJAJ: po danu srednji prinos svih simbola sa dogadjajem minus prosek univerzuma, pa po nedelji i bez preklapanja."""
    cost, daily = cfg["cost_pct"], []
    for d in U.cal:
        fl = U.flagged(fam, d)
        if not fl:
            continue
        rets = [r for r in (U.outcome(s, d, H) for s, _ in fl) if r is not None]
        u = U.universe_mean(d, H) if rets else None
        if not rets or u is None:
            continue
        m = sum(rets) / len(rets)
        daily.append((d, m - u - cost, m - cost, u - m - cost, -m - cost))
    return thin_weeks(daily, H, U.bpw)


def test_stats(periods, col, cfg, today_iso):
    """Statistika jedne noge (col 1..4): n, srednja, t, p, delovi vremena, poslednjih 270 dana, srednja pri strogom trosku."""
    vals = [p[col] for p in periods]
    n = len(vals)
    out = {"n": n}
    if n < 3:
        return dict(out, mean=None, t=None, p=None)
    cut = int(n * cfg["split_train"])
    tt = tstat(vals)
    since = (dt.date.fromisoformat(today_iso) - dt.timedelta(days=cfg["gates"]["candidate"]["recent_days"])).isoformat()
    recent = [p[col] for p in periods if p[0] >= since]
    shift = cfg["cost_pct"] - cfg["stress_cost_pct"]
    out.update({"mean": round(st.mean(vals), 4), "median": round(st.median(vals), 4),
                "mean_ex_best": round((sum(vals) - max(vals)) / (n - 1), 4) if n >= 5 else None, "t": tt, "p": None if (tt is None or n < 30) else round(S.t_to_p(tt), 5),
                "t_train": tstat(vals[:cut]), "t_test": tstat(vals[cut:]), "n_recent": len(recent),
                "recent_mean": round(st.mean(recent), 4) if recent else None,
                "stress_mean": round(st.mean(vals) + shift, 4), "win_pct": round(100.0 * sum(1 for x in vals if x > 0) / n, 1)})
    return out


def classify(r, fdr_pass, cfg):
    g = cfg["gates"]
    c, h = g["candidate"], g["hint"]
    if r["n"] < h["min_periods"] or r.get("t") is None:
        return "premalo"
    ok = (fdr_pass and r["n"] >= c["min_periods"] and r["mean"] > c["mean_net_gt"] and r["abs_mean"] > c["abs_mean_net_gt"]
          and (r.get("t_train") if r.get("t_train") is not None else -9) > c["train_t_min"]
          and (r.get("t_test") if r.get("t_test") is not None else -9) >= c["test_t_min"]
          and r.get("recent_mean") is not None and r["recent_mean"] > c["recent_mean_gt"]
          and r.get("mean_ex_best") is not None and r["mean_ex_best"] > c["mean_ex_best_gt"])
    if ok:
        return "kandidat"
    if r.get("p") is not None and r["p"] <= h["p_raw_max"] and r["mean"] > h["mean_net_gt"]:
        return "nagovestaj"
    return "odbaceno"


def rule_id(universe, fam, kind, step_or_h, leg):
    return "%s:%s:%d%s:%s" % (universe, fam, step_or_h, "w" if kind == "rank" else "d", leg)


def run_study(unis, cfg, today_iso):
    """unis: {ime: Universe}. Vraca listu testova sa statusom (FDR preko SVIH testova svih univerzuma i obe vrste)."""
    rows = []
    for name, U in unis.items():
        jobs = [("rank", fam, w, w * U.bpw, run_periods(U, cfg, fam, w)) for fam in FAMILIES for w in cfg["weeks"]]
        jobs += [("event", fam, h, h, event_periods(U, cfg, fam, h)) for fam in EVENTS for h in cfg["event_horizons"]]
        for kind, fam, step, H, per in jobs:
            for leg, ce, ca in (("long", 1, 2), ("short", 3, 4)):
                r = test_stats(per, ce, cfg, today_iso)
                ab = test_stats(per, ca, cfg, today_iso)
                r.update({"id": rule_id(name, fam, kind, step, leg), "universe": name, "family": fam, "kind": kind, "step": step, "H": H,
                          "leg": leg, "abs_mean": ab.get("mean"), "abs_t": ab.get("t")})
                rows.append(r)
    pv = [(r["id"], r["p"]) for r in rows if r.get("p") is not None]
    passed = S.bh_fdr(pv, cfg["gates"]["candidate"]["fdr_q"])
    for r in rows:
        r["fdr"] = r["id"] in passed
        r["status"] = classify(r, r["fdr"], cfg) if r.get("abs_mean") is not None else "premalo"
    return rows


# ------------------------------------------------------------------ opisni slucaj (npr. GME)
def profile(U, sym, day_iso):
    """Gde je simbol po svakoj rang-porodici na poslednjoj sveci <= dan: ocena i percentil medju clanovima (0 = najnize, 1 = najvise),
    i koji su se dogadjaji dogodili u poslednjih 10 svecâ."""
    cands = [d for d in U.cal if d <= day_iso]
    if not cands or sym not in U.px:
        return None
    d = cands[-1]
    out = {"date": d, "families": {}, "events": []}
    for fam in FAMILIES:
        mem = U.members(fam, d)
        me = [x for s, x in mem if s == sym]
        if not me or len(mem) < 3:
            continue
        below = sum(1 for _, x in mem if x < me[0])
        out["families"][fam] = {"score": round(me[0], 4), "pct": round(below / (len(mem) - 1), 3), "n": len(mem)}
    i = U.idx[sym].get(d)
    if i is not None:
        for fam in EVENTS:
            for k in range(max(0, i - 9), i + 1):
                if U.ev[sym][fam][k] is not None:
                    out["events"].append({"event": fam, "date": U.px[sym]["d"][k], "vol_ratio": U.ev[sym][fam][k]})
    return out


# ------------------------------------------------------------------ pravila i izbor unapred
def make_rule(r):
    return {k: r[k] for k in ("universe", "family", "kind", "step", "H", "leg")}


def signal_dates(U, r):
    if r["kind"] == "rank":
        return rebalance_dates(U.cal, r["step"], U.bpw)
    return [d for d in U.cal if U.flagged(r["family"], d)]


def pick_for(U, r, d, k, cfg):
    """Izbor za trgovanje, zamrznut u trenutku signala. RANG: k najvisih (long) ili k najnizih (short) po oceni; DOGADJAJ: k najjacih dogadjaja."""
    if r["kind"] == "rank":
        mem = U.members(r["family"], d)
        if len(mem) < cfg["min_universe"]:
            return []
        chosen = mem[:k] if r["leg"] == "long" else mem[-k:][::-1]
    else:
        chosen = U.flagged(r["family"], d)[:k]
    return [{"sym": s, "score": round(x, 6), "rc": U.px[s]["rc"][U.idx[s][d]]} for s, x in chosen]


def sim_trade(b, e, H, side, sp, tp):
    """Prinos u % jednog trgovanja kakvo je uzivo: ulaz otvaranje svece e, stop sp% i cilj tp%, najvise H svecâ (izlaz zatvaranje poslednje).
    Ako stop i cilj padnu iste svece racuna se stop; ako se otvori iza stopa/cilja, izlaz je po otvaranju. None dok nema svih svecâ."""
    last = e + H - 1
    if last >= len(b["c"]) or not b["o"][e]:
        return None
    entry = b["o"][e]
    long = side == "long"
    stop = entry * (1 - sp / 100.0) if long else entry * (1 + sp / 100.0)
    target = entry * (1 + tp / 100.0) if long else entry * (1 - tp / 100.0)
    ex = b["c"][last]
    for k in range(e, last + 1):
        o, h, lo = b["o"][k], b["h"][k], b["l"][k]
        if long:
            if lo <= stop:
                ex = min(o, stop)
                break
            if h >= target:
                ex = max(o, target)
                break
        else:
            if h >= stop:
                ex = max(o, stop)
                break
            if lo <= target:
                ex = min(o, target)
                break
    return ((ex / entry - 1.0) if long else ((entry - ex) / entry)) * 100.0


def pick_sim(U, p, d, H, leg):
    """Ishod trgovanja (stop 2.5 x ATR u opsegu 3-12%, cilj 3 x stop) za jedan izbor, ili None."""
    b, i = U.px[p["sym"]], U.idx[p["sym"]].get(d)
    if i is None:
        return None
    a = atr_pct(b, i)
    if a is None:
        return None
    sp = min(max(2.5 * a, 3.0), 12.0)
    return sim_trade(b, i + 1, H, leg, sp, 3.0 * sp)


def realized(U, cfg, r, d, picks):
    """Ostvaren neto prinos izbora: (iznad proseka univerzuma, apsolutni, trgovanje sa stopom i ciljem ili None), u %; None dok ishod nije potpun."""
    H, cost = r["H"], cfg["cost_pct"]
    rp = [U.outcome(p["sym"], d, H) for p in picks]
    if not picks or any(x is None for x in rp):
        return None
    if r["kind"] == "rank":
        ru = [U.outcome(s, d, H) for s, _ in U.members(r["family"], d)]
        ru = [x for x in ru if x is not None]
        u = sum(ru) / len(ru) if len(ru) >= cfg["min_universe"] else None
    else:
        u = U.universe_mean(d, H)
    if u is None:
        return None
    m = sum(rp) / len(rp)
    sims = [pick_sim(U, p, d, H, r["leg"]) for p in picks]
    sim = None if any(x is None for x in sims) else sum(sims) / len(sims) - cost
    return (m - u - cost, m - cost, sim) if r["leg"] == "long" else (u - m - cost, -m - cost, sim)


def forward_stats(rows, cfg):
    """rows: lista (datum, excess, abs, sim). n, srednja, t (neto posle troska), srednja pri strogom trosku, bez najboljeg, simulirano trgovanje."""
    ex = [r[1] for r in rows]
    n = len(ex)
    if n == 0:
        return {"n": 0, "mean": None, "t": None, "stress_mean": None}
    shift = cfg["cost_pct"] - cfg["stress_cost_pct"]
    sims = [r[3] for r in rows if len(r) > 3 and r[3] is not None]
    return {"n": n, "mean": round(st.mean(ex), 4), "t": tstat(ex), "abs_mean": round(st.mean(r[2] for r in rows), 4),
            "stress_mean": round(st.mean(ex) + shift, 4), "median": round(st.median(ex), 4),
            "mean_ex_best": round((sum(ex) - max(ex)) / (n - 1), 4) if n >= 5 else None,
            "sim_n": len(sims), "sim_mean": round(st.mean(sims), 4) if sims else None}


def forward_gate(fs, cfg):
    p = cfg["gates"]["promote"]
    return (fs["n"] >= p["min_fwd_periods"] and fs["mean"] is not None and fs["mean"] > p["fwd_mean_gt"]
            and (fs["t"] if fs["t"] is not None else -9) >= p["fwd_t_min"] and fs["stress_mean"] > p["stress_mean_gt"]
            and fs.get("mean_ex_best") is not None and fs["mean_ex_best"] > p["fwd_mean_ex_best_gt"]
            and fs.get("sim_mean") is not None and fs["sim_mean"] > p["sim_mean_gt"])


def demote_gate(fs, cfg):
    d = cfg["gates"]["demote"]
    return fs["n"] >= d["min_fwd_periods"] and fs["t"] is not None and fs["t"] <= d["fwd_t_max"]


def forward_start(U, r):
    """Prvi datum signala ciji ishod u trenutku studije NIJE potpun: tek on je pravo 'unapred' (studija ga nije videla)."""
    pos = {d: i for i, d in enumerate(U.cal)}
    if r["kind"] == "event":
        return U.cal[max(0, len(U.cal) - r["H"])] if U.cal else None
    for d in rebalance_dates(U.cal, r["step"], U.bpw):
        if pos[d] + r["H"] >= len(U.cal):
            return d
    return None


def apply_study(rules, tests, now_iso, unis=None):
    """Spaja nedeljnu studiju u registar pravila. Nikad ne preskace status: 'potvrdjen' se dobija samo iz apply_forward."""
    today = now_iso[:10]

    def fstart(r):
        U = (unis or {}).get(r["universe"])
        return (forward_start(U, r) if U else None) or today

    for r in tests:
        rid, new = r["id"], r["status"]
        cur = rules.get(rid)
        snap = {k: r.get(k) for k in ("n", "mean", "median", "mean_ex_best", "t", "p", "t_train", "t_test", "recent_mean", "stress_mean", "abs_mean", "fdr")}
        if cur is None:
            if new in ("nagovestaj", "kandidat"):
                rules[rid] = dict(make_rule(r), status=new, first_seen_utc=now_iso, forward_start=fstart(r), study=snap, history=[[now_iso, new]])
            continue
        cur["study"] = snap
        old = cur["status"]
        if old == "potvrdjen":
            if new == "kandidat":
                continue
            cur["status"] = new if new != "premalo" else "nagovestaj"
        else:
            if new == "premalo":
                continue
            cur["status"] = new
            if old == "odbaceno" and new in ("nagovestaj", "kandidat"):
                cur["forward_start"] = fstart(r)
        if cur["status"] != old:
            cur["history"].append([now_iso, cur["status"]])
    return rules


def apply_forward(rules, fstats, cfg, now_iso):
    """Napredovanje i povlacenje po kapijama unapred. Potvrdjuje se samo 'kandidat'; kapije su u config/discovery.json."""
    for rid, r in rules.items():
        fs = fstats.get(rid)
        if not fs:
            continue
        r["forward"] = fs
        if r["status"] == "kandidat" and forward_gate(fs, cfg):
            r["status"] = "potvrdjen"
            r["promoted_utc"] = now_iso
            r["history"].append([now_iso, "potvrdjen"])
        elif r["status"] == "potvrdjen" and demote_gate(fs, cfg):
            r["status"] = "nagovestaj"
            r["demoted_utc"] = now_iso
            r["history"].append([now_iso, "nagovestaj"])
    return rules


def log_signals(rules, unis, cfg, log, now_iso):
    """Dopisuje izbore za sve datume signala (posle pocetka pracenja) koji jos nisu u dnevniku. Izbor se zamrzava u trenutku upisa."""
    have = {(x["rule"], x["signal_date"]) for x in log}
    new = []
    for rid, r in sorted(rules.items()):
        if r["status"] not in TRACKED or r["universe"] not in unis:
            continue
        U = unis[r["universe"]]
        for d in signal_dates(U, r):
            if d < r["forward_start"] or (rid, d) in have:
                continue
            picks = pick_for(U, r, d, cfg["pick_k"], cfg)
            if not picks:
                continue
            new.append({"rule": rid, "signal_date": d, "universe": r["universe"], "family": r["family"], "kind": r["kind"], "step": r["step"],
                        "H": r["H"], "leg": r["leg"], "picks": picks, "logged_utc": now_iso, "status_at_log": r["status"]})
            have.add((rid, d))
    return new


def evaluate_log(log, unis, cfg):
    """{rule_id: forward_stats} iz zamrznutih izbora i sadasnjih cena; 'pending' = izbori koji jos cekaju ishod.
    Dogadjaji se sazimaju po nedelji i proredjuju (isti postupak kao u studiji) da se periodi ne preklapaju."""
    per, pending, meta = {}, {}, {}
    for x in log:
        U = unis.get(x["universe"])
        if U is None:
            continue
        meta[x["rule"]] = (x["kind"], x["H"], U.bpw)
        res = realized(U, cfg, x, x["signal_date"], x["picks"])
        if res is None:
            pending[x["rule"]] = pending.get(x["rule"], 0) + 1
            continue
        per.setdefault(x["rule"], []).append((x["signal_date"],) + tuple(res))
    out = {}
    for rid in set(per) | set(pending):
        rows = sorted(per.get(rid, []))
        kind, H, bpw = meta[rid]
        if kind == "event":
            rows = thin_weeks(rows, H, bpw)
        out[rid] = dict(forward_stats(rows, cfg), pending=pending.get(rid, 0))
    return out


# ------------------------------------------------------------------ radar
def entry_window(U, signal_date, cfg):
    """(od, do) kad izbor sme da se uzme: otvaranje sledece trgovacke sesije + valid_hours. Kripto: sledece 00:00 UTC."""
    d = dt.date.fromisoformat(signal_date) + dt.timedelta(days=1)
    if U.bpw == 5:
        while d.weekday() >= 5:
            d += dt.timedelta(days=1)
        start = dt.datetime(d.year, d.month, d.day, STOCK_OPEN_UTC[0], STOCK_OPEN_UTC[1], tzinfo=dt.timezone.utc)
    else:
        start = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(hours=cfg["radar"]["valid_hours_after_open"])
    f = "%Y-%m-%dT%H:%M:%SZ"
    return start.strftime(f), end.strftime(f)


def explorer_symbol(universe, sym):
    return "xyz:" + sym if universe == "stocks" else sym.replace("-USD", "")


def build_radar(rules, unis, cfg, now_iso):
    """Najnoviji izbor svakog pracenog pravila sa stopom i ciljem po pravilu Istrazivaca za dnevna drzanja.
    RANG: poslednji zavrseni datum signala; DOGADJAJ: samo ako se dogadjaj desio na poslednjoj sveci."""
    out = []
    for rid, r in sorted(rules.items()):
        if r["status"] not in TRACKED or r["universe"] not in unis:
            continue
        U = unis[r["universe"]]
        ds = signal_dates(U, r)
        if not ds or (r["kind"] == "event" and ds[-1] != U.cal[-1]):
            continue
        d = ds[-1]
        picks = pick_for(U, r, d, cfg["radar"]["pick_k"], cfg)
        if not picks:
            continue
        frm, to = entry_window(U, d, cfg)
        rows = []
        for p in picks:
            b, i = U.px[p["sym"]], U.idx[p["sym"]][d]
            a = atr_pct(b, i)
            sp = None if a is None else round(min(max(2.5 * a, 3.0), 12.0), 2)
            rows.append({"ticker": p["sym"], "symbol": explorer_symbol(r["universe"], p["sym"]), "score": p["score"], "px": round(p["rc"], 4),
                         "atr_pct": None if a is None else round(a, 2), "stop_pct": sp, "tp_pct": None if sp is None else round(3.0 * sp, 2)})
        out.append({"rule": rid, "status": r["status"], "universe": r["universe"], "family": r["family"], "kind": r["kind"],
                    "side": "long" if r["leg"] == "long" else "short", "signal_date": d, "valid_from_utc": frm, "valid_until_utc": to,
                    "hold_hours": int(round(r["H"] / U.bpw * 168)), "picks": rows, "forward": r.get("forward"), "study": r.get("study")})
    return {"generated_utc": now_iso, "rules": out}


# ------------------------------------------------------------------ univerzum sa Hyperliquid-a
def hl_candidates(cfg):
    """{ime univerzuma: [{sym, yahoo, mark, vol24}]} sa Hyperliquid-a (isto trziste kao Liquid), pre provere cena na Yahoo-u."""
    from . import collectors as C
    ctx = C.hl_contexts()
    cats = {c[0]: c[1] for c in C.hl_post({"type": "perpCategories"})}
    out = {}
    for name, u in cfg["universes"].items():
        rows = []
        for s, c in ctx.items():
            if c["vol24"] < u["min_vol24_usd"]:
                continue
            if u["source"] == "hl_xyz_stocks" and s.startswith("xyz:") and (cats.get(s) or "").lower() in ("stocks", "stock"):
                rows.append({"sym": s, "yahoo": s[4:], "mark": c["mark"], "vol24": c["vol24"]})
            elif u["source"] == "hl_main_crypto" and ":" not in s:
                rows.append({"sym": s, "yahoo": s + "-USD", "mark": c["mark"], "vol24": c["vol24"]})
        out[name] = rows
    return out


def build_universe_prices(cands, ucfg, now, cache=None, log=print):
    """Cene za kandidate; prihvata samo simbole cija se poslednja cena slaze sa HL oznakom (+-12%), sa dovoljno istorije i bez zastarelosti."""
    px = load_prices([c["yahoo"] for c in cands] + [ucfg["benchmark"]], cache)
    bench = px.get(ucfg["benchmark"])
    if not bench:
        return None, None, []
    bench = trim_incomplete(bench, now, ucfg["bars_per_week"])
    keep, used = {}, []
    for c in cands:
        b = px.get(c["yahoo"])
        if not b:
            log("bez Yahoo cena: %s" % c["sym"])
            continue
        b = trim_incomplete(b, now, ucfg["bars_per_week"])
        if len(b["c"]) < ucfg["min_bars"]:
            log("premalo istorije (%d): %s" % (len(b["c"]), c["sym"]))
            continue
        gap = (dt.date.fromisoformat(bench["d"][-1]) - dt.date.fromisoformat(b["d"][-1])).days
        if gap > 7:
            log("zastarelo (%d dana): %s" % (gap, c["sym"]))
            continue
        if not (0.88 <= c["mark"] / b["rc"][-1] <= 1.12):
            log("cena se ne slaze (HL %.4g, Yahoo %.4g): %s" % (c["mark"], b["rc"][-1], c["sym"]))
            continue
        keep[c["yahoo"]] = b
        used.append({"sym": c["sym"], "yahoo": c["yahoo"], "vol24": c["vol24"], "bars": len(b["c"])})
    return keep, bench, used


# ------------------------------------------------------------------ izvestaj
def to_markdown(res):
    cfg, tests = res["cfg_summary"], res["tests"]
    L = ["# Lovac: studija na sirem univerzumu (%s)" % res["generated_utc"][:10], ""]
    L.append("Univerzumi: " + "; ".join("%s %d instrumenata (%s do %s)" % (k, v["n"], v["from"], v["to"]) for k, v in res["universes"].items()) + ".")
    L.append("Testova: %d (rang-porodice x horizonti x noge, dogadjaji x horizonti x noge), FDR %.0f%% preko svih. Trosak %.2f%% po krugu (strogo %.2f%%). "
             "Mera = prosecan neto prinos ODABRANE grupe minus prosek univerzuma; nepreklapajuci periodi; t preko perioda." % (
                 len(tests), 100 * cfg["fdr_q"], cfg["cost_pct"], cfg["stress_cost_pct"]))
    cnt = {}
    for r in tests:
        cnt[r["status"]] = cnt.get(r["status"], 0) + 1
    L.append("Status: " + ", ".join("%s %d" % (k, v) for k, v in sorted(cnt.items())) + ".")
    L += ["", "Ogranicenja (cita se pre brojeva): univerzum je izabran prema SADASNJOJ listi Liquid-a (preziveli i popularni), pa su istorijski rezultati verovatno prelepi; "
          "nema stopova u testu; ulaz je otvaranje sledeceg dana, a uzivo se ulazi sat-dva kasnije. Zato jedino 'potvrdjen' (posle prolaska unapred) ima ikakvu tezinu.", "",
          "## Svi testovi, poredjani po t", "",
          "| pravilo | n | neto % | apsolutno % | t | p | t prvi deo | t zadnji deo | zadnjih 270 d % | strogi trosak % | FDR | status |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(tests, key=lambda r: -(r["t"] if r.get("t") is not None else -99)):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["n"], r.get("mean"), r.get("abs_mean"), r.get("t"), r.get("p"), r.get("t_train"), r.get("t_test"), r.get("recent_mean"),
            r.get("stress_mean"), "da" if r.get("fdr") else "ne", r["status"]))
    for c in res.get("cases", []):
        pr = c["profile"]
        L += ["", "## Opisni slucaj: %s (vlasnikov ulaz %s)" % (c["sym"], c["entry"]), "",
              "Gde je %s po svakoj rang-porodici na poslednjoj sveci pre ulaza (%s). Percentil 1.0 = najvise u univerzumu (od %s clanova)." % (
                  c["sym"], pr["date"], max((v["n"] for v in pr["families"].values()), default="?")), "",
              "| porodica | ocena | percentil |", "|---|---|---|"]
        for fam, v in pr["families"].items():
            L.append("| %s | %s | %s |" % (fam, v["score"], v["pct"]))
        L += ["", "Dogadjaji u poslednjih 10 svecâ: " + (", ".join("%s %s (obim x%.1f)" % (e["event"], e["date"], e["vol_ratio"]) for e in pr["events"]) or "nijedan") + "."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ glavni tok
def prepare(cfg, now, cache, log=print, hl=None):
    cands = hl if hl is not None else hl_candidates(cfg)
    unis, used = {}, {}
    for name, ucfg in cfg["universes"].items():
        px, bench, u = build_universe_prices(cands.get(name, []), ucfg, now, cache, log)
        if not px or len(px) < cfg["min_universe"]:
            log("univerzum %s preskocen: premalo instrumenata" % name)
            continue
        unis[name] = Universe(name, px, bench, ucfg, cfg)
        used[name] = u
    return unis, used


def run(mode, cache=None, write=True, root=None, log=print, now=None, hl=None):
    root = root or ROOT
    cfg = load_cfg(os.path.join(root, "config", "discovery.json"))
    now = now or dt.datetime.now(dt.timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    d_dir = os.path.join(root, "discovery")
    unis, used = prepare(cfg, now, cache, log, hl)
    if not unis:
        log("nema nijednog univerzuma: ne diram stare fajlove")
        return 1
    rules = _load(os.path.join(d_dir, "rules.json"), {}).get("rules", {})
    res = None
    if mode == "weekly":
        tests = run_study(unis, cfg, now_iso[:10])
        rules = apply_study(rules, tests, now_iso, unis)
        res = {"generated_utc": now_iso, "tests": tests,
               "universes": {k: {"n": len(U.px), "from": min(b["d"][0] for b in U.px.values()), "to": U.cal[-1]} for k, U in unis.items()},
               "cfg_summary": {"fdr_q": cfg["gates"]["candidate"]["fdr_q"], "cost_pct": cfg["cost_pct"], "stress_cost_pct": cfg["stress_cost_pct"]},
               "cases": []}
        for tk, entry in CASES:
            U = unis.get("stocks")
            p = profile(U, tk, entry) if U else None
            if p:
                res["cases"].append({"sym": tk, "entry": entry, "profile": p})
    log_path = os.path.join(d_dir, "forward.jsonl")
    log_rows = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            log_rows = [json.loads(x) for x in f if x.strip()]
    new = log_signals(rules, unis, cfg, log_rows, now_iso)
    log_rows += new
    fst = evaluate_log(log_rows, unis, cfg)
    rules = apply_forward(rules, fst, cfg, now_iso)
    radar = build_radar(rules, unis, cfg, now_iso)
    if write:
        _save(os.path.join(d_dir, "rules.json"), {"updated_utc": now_iso, "rules": rules})
        _save(os.path.join(d_dir, "radar.json"), radar)
        _save(os.path.join(d_dir, "universe.json"), {"generated_utc": now_iso, "universes": used})
        with open(log_path, "w", encoding="utf-8") as f:
            for x in log_rows:
                f.write(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n")
        if res is not None:
            _save(os.path.join(root, "calibration", "discovery.json"), res)
            with open(os.path.join(root, "calibration", "discovery.md"), "w", encoding="utf-8") as f:
                f.write(to_markdown(res))
    log("%s: pravila %d, novih izbora %d, status: %s" % (mode, len(rules), len(new), {s: sum(1 for r in rules.values() if r["status"] == s) for s in TRACKED}))
    return 0


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] not in ("weekly", "daily"):
        print(__doc__)
        return 2
    cache = a[a.index("--cache") + 1] if "--cache" in a else None
    return run(a[0], cache=cache, write="--no-write" not in a)


if __name__ == "__main__":
    sys.exit(main())
