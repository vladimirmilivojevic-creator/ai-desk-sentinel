"""Korpa po fondingu (carry): unapred zadata studija (config/carry.json, upisana PRE rezultata).
Svakog rebalansa se iz prvih 30 kovanica po prometu (point-in-time) biraju k sa NAJNIZIM i k sa NAJVISIM prosecnim fondingom poslednjih n dana;
'carry' = dugo najnizi / kratko najvisi (prima se fonding na obe strane), 'reverse' = obrnuto. Tezine su obrnuto srazmerne volatilnosti (30 dana).
Neto po periodu = 0,5 x (duga noga: cena minus placeni fonding; kratka noga: minus cena plus primljeni fonding) minus trosak po krugu.
Razlaganje na komponentu cene i komponentu fondinga pokazuje da li pomaci cene pojedu fonding (Robot Wealth: na Hyperliquid-u od 2024 jeste).
Podaci: Binance javni arhiv (mesecni fundingRate) + Binance spot dnevne svece iz Lovca. Samo stdlib.
Upotreba: python -m lab.carry_study [--cache lab/cache] [--out calibration/carry_study]"""
import csv
import datetime as dt
import io
import json
import math
import os
import random
import statistics as st
import sys
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

from . import discovery as D
from . import stats as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FURL = "https://data.binance.vision/data/futures/um/monthly/fundingRate/%s/%s-fundingRate-%s.zip"
UA = {"User-Agent": "ai-desk-sentinel/0.3 (public research, read-only)"}


def load_cfg(path=None):
    with open(path or os.path.join(ROOT, "config", "carry.json"), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- fonding
def parse_funding_csv(text):
    """[(t_ms, stopa)] iz CSV-a mesecnog fajla (calc_time, funding_interval_hours, last_funding_rate)."""
    rows = []
    for p in csv.reader(io.StringIO(text)):
        if len(p) < 3:
            continue
        try:
            rows.append((int(p[0]), float(p[2])))
        except ValueError:
            continue  # zaglavlje
    return rows


def daily_funding(rows):
    """{datum: zbir stopa isplacenih tog UTC dana} (tri isplate dnevno za 8-casovni ugovor, vise za kraci interval)."""
    out = {}
    for t, r in rows:
        d = dt.datetime.fromtimestamp(t / 1000.0, dt.timezone.utc).date().isoformat()
        out[d] = out.get(d, 0.0) + r
    return out


def fetch_month(perp, ym, cache=None, timeout=30, tries=3):
    """Isplate fondinga za jedan mesec: lista, [] kad fajla nema (404), None kad preuzimanje ne uspe. Keš na disku (i za 'nema')."""
    p = os.path.join(cache, "fr_%s_%s.json" % (perp, ym)) if cache else None
    if p and os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return [tuple(x) for x in json.load(f)]
    rows = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(FURL % (perp, perp, ym), headers=UA), timeout=timeout) as r:
                raw = r.read(3_000_000)
            z = zipfile.ZipFile(io.BytesIO(raw))
            rows = parse_funding_csv(z.read(z.namelist()[0]).decode("utf-8", "replace"))
            break
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                rows = []
                break
        except Exception:  # noqa: BLE001
            pass
    if rows is not None and p:
        os.makedirs(cache, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(rows, f, separators=(",", ":"))
    return rows


def months(d0, d1):
    y, m = int(d0[:4]), int(d0[5:7])
    out = []
    while "%04d-%02d" % (y, m) <= d1[:7]:
        out.append("%04d-%02d" % (y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def load_funding(members, last_day, cache=None, workers=12, log=print):
    """{spot_simbol: {datum: dnevni fonding}} samo za kovanice koje imaju perpetual. Perp je isti naziv, ili 1000 + osnova (npr. 1000PEPEUSDT)."""
    def one(sym):
        base = sym[:-4]
        days = sorted(members[sym])
        ms = months(days[0], min(days[-1], last_day))
        for perp in (sym, "1000%sUSDT" % base):
            rows, bad = [], 0
            for ym in ms:
                r = fetch_month(perp, ym, cache)
                if r is None:
                    bad += 1
                else:
                    rows += r
            if rows:
                return sym, daily_funding(rows), bad
        return sym, {}, 0
    out, bad_total = {}, 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for sym, f, bad in ex.map(one, sorted(members)):
            bad_total += bad
            if f:
                out[sym] = f
    log("fonding: %d od %d kovanica ima perpetual, neuspelih mesecnih fajlova: %d" % (len(out), len(members), bad_total))
    return out


# ---------------------------------------------------------------- studija
def vol30(b, i):
    if i < 30:
        return None
    rets = [b["c"][k] / b["c"][k - 1] - 1.0 for k in range(i - 29, i + 1)]
    sd = st.pstdev(rets)
    return sd if sd > 0 else None


def add_days(d, n):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()


def build_index(px):
    return {s: {d: i for i, d in enumerate(b["d"])} for s, b in px.items()}


def leg_numbers(px, idx, fund, sym, d, H):
    """(r, F) za nogu: r = cena od otvaranja d+1 do zatvaranja d+H (ili poslednjeg dostupnog zatvaranja ako je kovanica prestala da se trguje:
    nema gledanja unapred, ulaz mora da postoji); F = zbir fonding isplata dana d+1 .. d+H. None kad ulaza nema."""
    b, ix = px[sym], idx[sym]
    d1 = add_days(d, 1)
    if d1 not in ix:
        return None
    last = None
    for k in range(1, H + 1):
        dk = add_days(d, k)
        if dk in ix:
            last = ix[dk]
        elif last is not None:
            break  # prekid: pozicija se zatvara na poslednjoj dostupnoj ceni
    if last is None:
        return None
    o = b["o"][ix[d1]]
    if not o:
        return None
    r = b["c"][last] / o - 1.0
    f = sum(fund[sym].get(add_days(d, k), 0.0) for k in range(1, H + 1))
    return r, f


def pick(px, idx, fund, mem, d, n_sig, k, min_names, rng=None):
    """Kovanice koje su clanovi na dan d, imaju fonding za svih n_sig dana (do kraja dana d) i cene za volatilnost: (nizak, visok) po fondingu.
    rng (placebo): umesto ranga nasumicno biranje iste velicine."""
    el = []
    for s, days in mem.items():
        if d not in days or s not in fund or s not in px or d not in idx[s]:
            continue
        fs = [fund[s].get(add_days(d, -j)) for j in range(n_sig)]
        if any(x is None for x in fs):
            continue
        v = vol30(px[s], idx[s][d])
        if v is None:
            continue
        el.append((sum(fs) / n_sig, s, v))
    if len(el) < max(min_names, 2 * k):
        return None
    if rng is not None:
        rng.shuffle(el)
        return el[:k], el[k:2 * k]
    el.sort(key=lambda x: (x[0], x[1]))
    return el[:k], el[-k:]


def period_result(px, idx, fund, lo, hi, d, H, orient, cost):
    """Neto po periodu u % (i komponente) ili None. Duga strana je lo ('carry') ili hi ('reverse')."""
    longs, shorts = (lo, hi) if orient == "carry" else (hi, lo)
    comp = {"price": 0.0, "fund": 0.0}
    for sign, leg in ((1.0, longs), (-1.0, shorts)):
        w = [1.0 / x[2] for x in leg]
        tot = sum(w)
        for wi, (_, s, _) in zip(w, leg):
            n = leg_numbers(px, idx, fund, s, d, H)
            if n is None:
                return None
            r, f = n
            comp["price"] += 0.5 * sign * (wi / tot) * r
            comp["fund"] += 0.5 * (-sign) * (wi / tot) * f  # duga strana placa pozitivan fonding, kratka ga prima
    price, fnd = comp["price"] * 100.0, comp["fund"] * 100.0
    return {"net": price + fnd - cost, "price": price, "fund": fnd}


def run_test(px, idx, fund, mem, dates, n_sig, H, orient, cfg, offset=0, rng=None):
    out = []
    for i in range(offset, len(dates), H):
        d = dates[i]
        sel = pick(px, idx, fund, mem, d, n_sig, cfg["k"], cfg["universe"]["min_names"], rng)
        if sel is None:
            continue
        r = period_result(px, idx, fund, sel[0], sel[1], d, H, orient, cfg["cost_per_round_trip_pct"])
        if r is not None:
            r["date"] = add_days(d, 1)
            out.append(r)
    return out


def summarize_periods(rows, H, last_day):
    n = len(rows)
    if not n:
        return {"n": 0}
    net = [r["net"] for r in rows]
    mean = sum(net) / n
    sd = st.stdev(net) if n > 1 else 0.0
    t = round(mean / (sd / math.sqrt(n)), 2) if sd > 0 and n >= 3 else None
    cut = int(n * 0.6)
    a, b = net[:cut], net[cut:]
    ago = add_days(last_day, -270)
    rec = [r["net"] for r in rows if r["date"] >= ago]
    by_year = {}
    for r in rows:
        by_year.setdefault(r["date"][:4], []).append(r["net"])
    return {"n": n, "mean": round(mean, 3), "sd": round(sd, 3), "t": t, "sharpe": round(mean / sd * math.sqrt(365.0 / H), 2) if sd > 0 else None,
            "hit": round(100.0 * sum(1 for x in net if x > 0) / n, 1), "price": round(sum(r["price"] for r in rows) / n, 3), "fund": round(sum(r["fund"] for r in rows) / n, 3),
            "mean_first": round(sum(a) / len(a), 3) if a else None, "mean_last": round(sum(b) / len(b), 3) if b else None,
            "last270": round(sum(rec) / len(rec), 3) if rec else None, "n270": len(rec), "by_year": {y: round(sum(v) / len(v), 3) for y, v in sorted(by_year.items())}}


def run_study(px, fund, mem, cfg, last_day, log=print):
    idx = build_index(px)
    cal = sorted({d for s in mem for d in mem[s]})
    dates = [d for d in cal if cfg["universe"]["from"] <= d <= last_day]
    results = []
    for n_sig in cfg["signal_days"]:
        for H in cfg["hold_days"]:
            for orient in cfg["orientations"]:
                rows = run_test(px, idx, fund, mem, dates, n_sig, H, orient, cfg)
                s = summarize_periods(rows, H, last_day)
                offs = [summarize_periods(run_test(px, idx, fund, mem, dates, n_sig, H, orient, cfg, offset=o), H, last_day).get("mean") for o in range(min(H, 3))]
                plc = []
                for seed in range(cfg["placebo_runs"]):
                    pr = run_test(px, idx, fund, mem, dates, n_sig, H, orient, cfg, rng=random.Random(1000 + seed))
                    if pr:
                        plc.append(sum(r["net"] for r in pr) / len(pr))
                s.update(id="%s:%dd:%dd" % (orient, n_sig, H), signal_days=n_sig, hold_days=H, orient=orient,
                         offsets_mean=[x for x in offs if x is not None],
                         placebo_mean=round(st.mean(plc), 3) if plc else None, placebo_sd=round(st.stdev(plc), 3) if len(plc) > 1 else None)
                s["p"] = round(S.t_to_p(s["t"]), 5) if s.get("t") is not None and s["n"] >= cfg["min_periods"] else None
                results.append(s)
                log("%s n=%s mean=%s t=%s" % (s["id"], s.get("n"), s.get("mean"), s.get("t")))
    # svih 12 unapred upisanih testova ulazi u FDR; test bez dovoljno perioda ima p = 1 (ne moze da prodje, ali se broji)
    passed = S.bh_fdr([(r["id"], r["p"] if r["p"] is not None else 1.0) for r in results], cfg["fdr_q"])
    g = cfg["candidate_gates"]
    for r in results:
        r["fdr"] = r["id"] in passed
        ok = (r.get("n", 0) >= cfg["min_periods"] and r["fdr"] and (r.get("mean") or 0) > g["mean_gt"] and (r.get("mean_first") or 0) > g["both_halves_mean_gt"]
              and (r.get("mean_last") or 0) > g["both_halves_mean_gt"] and (r.get("last270") or 0) > g["last_270d_mean_gt"])
        r["status"] = "kandidat" if ok else ("premalo" if r.get("n", 0) < cfg["min_periods"] else "odbaceno")
    return results


def to_markdown(res, cfg, meta):
    L = ["# Korpa po fondingu (carry): studija (%s)" % meta["generated_utc"][:10], "",
         "Unapred zadato u config/carry.json (verzija %s, %s). %d testova, FDR %.0f%%. Kovanica sa fondingom: %d, period %s do %s, k=%d po strani, trosak %.2f%% po krugu. Placebo = nasumican izbor iste velicine, %d ponavljanja."
         % (cfg["version"], cfg["registered_utc"][:10], len(res["tests"]), 100 * cfg["fdr_q"], meta["n_coins"], meta["from"], meta["to"], cfg["k"], cfg["cost_per_round_trip_pct"], cfg["placebo_runs"]), "",
         "'carry' = dugo najnizi fonding, kratko najvisi (prima se fonding); 'reverse' = obrnuto. 'cena' i 'fonding' su komponente srednjeg neto rezultata po periodu u %.", "",
         "| test | n | srednje neto % | t | Sharpe | cena % | fonding % | prvi deo | poslednji deo | 270 d | placebo % (sd) | FDR | status |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(res["tests"], key=lambda r: -(r.get("t") if r.get("t") is not None else -99)):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s (%s) | %s | %s |" % (r["id"], r.get("n"), r.get("mean"), r.get("t"), r.get("sharpe"), r.get("price"), r.get("fund"),
                                                                                     r.get("mean_first"), r.get("mean_last"), r.get("last270"), r.get("placebo_mean"), r.get("placebo_sd"), "da" if r["fdr"] else "ne", r["status"]))
    cand = [r for r in res["tests"] if r["status"] == "kandidat"]
    L += ["", "Kandidata: %d od %d. Kad je komponenta fonding pozitivna a komponenta cena negativna, pomaci cene jedu fonding." % (len(cand), len(res["tests"])), ""]
    best = sorted(res["tests"], key=lambda r: -(r.get("t") if r.get("t") is not None else -99))[:3]
    for r in best:
        L.append("- %s po godinama (srednje neto %%): %s; pomereni početak (ofseti): %s" % (r["id"], r.get("by_year"), r.get("offsets_mean")))
    L += ["", "Ograničenja: " + cfg["limits"], ""]
    return "\n".join(L)


def prepare(cfg, cache, log=print):
    """Cene (Binance spot iz Lovca), clanstvo prvih top_n i fonding. Vraca (px, fund, mem, last_day)."""
    now = dt.datetime.now(dt.timezone.utc)
    dcfg = D.load_cfg()
    ucfg = dict(dcfg["universes"]["crypto"], top_n=cfg["universe"]["top_n"], rank_window=cfg["universe"]["rank_window"])
    start = dt.datetime.fromisoformat(cfg["universe"]["from"]).replace(tzinfo=dt.timezone.utc) - dt.timedelta(days=60)
    start_ms = int(start.timestamp() * 1000)
    allsyms = D.binance_symbols(log)
    excl = set(ucfg.get("exclude_bases", []))
    sset = set(allsyms)
    syms = [s for s in allsyms if s[:-4] not in excl
            and not any(s[:-4].endswith(x) and s[:-4][:-len(x)] + "USDT" in sset for x in ("UP", "DOWN", "BULL", "BEAR"))]
    sup, wf = D.binance_superset(syms, start_ms, ucfg["top_n"], ucfg.get("prefilter_factor", 1.5), cache)
    sup.add(ucfg["benchmark"])
    raw, fails = D.load_binance(sorted(sup), start_ms, cache)
    px = {}
    for s, b in raw.items():
        b = D.clean_series(b)
        if len(b["c"]) < 120 or (len(b["c"]) >= 100 and max(b["c"]) / min(b["c"]) < 1.35):
            continue
        px[s] = D.trim_incomplete(b, now, 7)
    mem = D.pit_membership(px, ucfg["top_n"], ucfg["rank_window"])
    mem = {s: {d for d in days if d >= cfg["universe"]["from"]} for s, days in mem.items()}
    mem = {s: days for s, days in mem.items() if days}
    # fonding postoji do kraja poslednjeg punog meseca
    first_this_month = now.date().replace(day=1)
    last_day = (first_this_month - dt.timedelta(days=1)).isoformat()
    fund = load_funding(mem, last_day, os.path.join(cache, "carry") if cache else None, log=log)
    mem = {s: {d for d in days if d <= last_day} for s, days in mem.items() if s in fund}
    px = {s: b for s, b in px.items() if s in mem}
    log("kovanica u studiji: %d, poslednji dan %s" % (len(mem), last_day))
    return px, fund, mem, last_day


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    cache = a[a.index("--cache") + 1] if "--cache" in a else os.path.join(ROOT, "lab", "cache")
    out = a[a.index("--out") + 1] if "--out" in a else os.path.join(ROOT, "calibration", "carry_study")
    cfg = load_cfg()
    px, fund, mem, last_day = prepare(cfg, cache)
    tests = run_study(px, fund, mem, cfg, last_day)
    meta = {"generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "n_coins": len(mem), "from": cfg["universe"]["from"], "to": last_day}
    res = {"meta": meta, "cfg": {k: cfg[k] for k in ("version", "registered_utc", "signal_days", "hold_days", "k", "cost_per_round_trip_pct", "fdr_q")}, "tests": tests}
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, separators=(",", ":"))
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write(to_markdown(res, cfg, meta))
    print("zapisano", out + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
