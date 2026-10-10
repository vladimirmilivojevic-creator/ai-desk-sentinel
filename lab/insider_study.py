"""Klasteri insider kupovina (SEC Form 4, kod P): da li pratnja daje prednost, i da li pravilo "ne juri" (15%) pomaze ili stetu?
Pitanje vlasnika: rucno kupljen GME (5 insidera kupilo, ulaz posle +34%) je najbolji trejd, a sistem takve ne nalazi. Ovo je merenje, ne tvrdnja.

Podaci: SEC "Insider Transactions Data Sets" (javni kvartalni TSV: SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS). Cene: Yahoo dnevne (otvaranje, zatvaranje), SPY kao ravnalo.
Definicija dogadjaja je zadata UNAPRED (kao u desk/playbook.md): u kliznom prozoru od 30 dana od datuma PRIJAVE bar 2 razlicita kupca (po prijavi, zajednicke prijave su jedan kupac),
bar jedan je direktor ili funkcioner, ukupno bar $100.000, cena akcije bar $2; dogadjaj je datum prijave koji je prvi ispunio uslov; 60 dana tisine po izdavaocu.
Ulaz: otvaranje PRVOG trgovackog dana posle datuma prijave (konzervativno). Izlaz: zatvaranje posle H trgovackih dana. Trosak 0,23% (isti kao laboratorija). Mera: prinos minus SPY za isti prozor.
Placebo: isti izdavaoci, slucajni datumi (ravnalo za drift izdavaoca koji kupuju insideri). t se racuna preko NEDELJA prijave (dogadjaji iste nedelje nisu nezavisni).
Samo stdlib. Upotreba: python -m lab.insider_study <dir_sa_raspakovanim_kvartalima> <izlaz.md> [--xyz fajl.json] [--cache dir]"""
import csv
import datetime as dt
import json
import math
import os
import random
import statistics as st
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

COST_PCT = 0.23
MIN_PRICE = 2.0
MIN_TOTAL = 100000.0
WINDOW_D = 30
QUIET_D = 60
HORIZONS = (5, 10, 20, 40, 60)
PRIMARY_H = 20
BAD_TITLE = ("option", "warrant", "preferred", "note", "right", "unit", "debenture", "bond")
CEO_WORDS = ("chief executive", "ceo", "chief financial", "cfo", "president", "chairman", "chair")
UA = {"User-Agent": "Mozilla/5.0 (ai-desk research)"}


def parse_date(s):
    try:
        return dt.datetime.strptime(s.strip().upper(), "%d-%b-%Y").date()
    except (ValueError, AttributeError):
        return None


def _rows(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t")


def load_quarter(d):
    """Vraca (kupovine, prodaje) iz jednog raspakovanog kvartala. Kupovina = {t, tk, cik, owner, od, ceo, value, price, acc, f10b5}."""
    sub = {}
    for r in _rows(os.path.join(d, "SUBMISSION.tsv")):
        if r.get("DOCUMENT_TYPE") != "4":
            continue
        fd = parse_date(r.get("FILING_DATE", ""))
        tk = (r.get("ISSUERTRADINGSYMBOL") or "").strip().upper()
        if fd and tk:
            sub[r["ACCESSION_NUMBER"]] = (fd, tk, r.get("ISSUERCIK", ""), r.get("AFF10B5ONE") == "1")
    owners = {}
    for r in _rows(os.path.join(d, "REPORTINGOWNER.tsv")):
        a = r["ACCESSION_NUMBER"]
        if a not in sub:
            continue
        rel = (r.get("RPTOWNER_RELATIONSHIP") or "")
        title = (r.get("RPTOWNER_TITLE") or "").lower()
        o = owners.setdefault(a, {"cik": r.get("RPTOWNERCIK", ""), "od": False, "ceo": False})
        if "Director" in rel or "Officer" in rel:
            o["od"] = True
        if any(w in title for w in CEO_WORDS):
            o["ceo"] = True
    buys, sells = [], []
    for r in _rows(os.path.join(d, "NONDERIV_TRANS.tsv")):
        a = r["ACCESSION_NUMBER"]
        if a not in sub:
            continue
        code = r.get("TRANS_CODE")
        if code not in ("P", "S"):
            continue
        title = (r.get("SECURITY_TITLE") or "").lower()
        if any(w in title for w in BAD_TITLE):
            continue
        try:
            sh, px = float(r.get("TRANS_SHARES") or 0), float(r.get("TRANS_PRICEPERSHARE") or 0)
        except ValueError:
            continue
        fd, tk, cik, f10 = sub[a]
        o = owners.get(a, {"cik": "", "od": False, "ceo": False})
        rec = {"t": fd, "tk": tk, "cik": cik, "owner": o["cik"] or a, "od": o["od"], "ceo": o["ceo"], "value": sh * px, "price": px, "acc": a, "f10b5": f10}
        if code == "P" and r.get("TRANS_ACQUIRED_DISP_CD") in ("A", "") and sh > 0 and px >= MIN_PRICE:
            buys.append(rec)
        elif code == "S" and sh > 0 and px > 0:
            sells.append(rec)
    return buys, sells


def find_clusters(buys, sells=(), window_d=WINDOW_D, quiet_d=QUIET_D, min_total=MIN_TOTAL, min_buyers=2):
    """Dogadjaji po pravilu iz zaglavlja. Vraca listu dict: tk, date, n_buyers, total, ceo, avg_price, first_buy, sells_30d."""
    by_tk = {}
    for b in buys:
        if b["od"]:
            by_tk.setdefault(b["tk"], []).append(b)
    sells_by = {}
    for s in sells:
        sells_by.setdefault(s["tk"], []).append(s)
    events = []
    for tk, rows in by_tk.items():
        rows.sort(key=lambda r: r["t"])
        last_ev = None
        for d in sorted({r["t"] for r in rows}):
            if last_ev is not None and (d - last_ev).days < quiet_d:
                continue
            win = [r for r in rows if 0 <= (d - r["t"]).days < window_d]
            buyers = {r["owner"] for r in win}
            total = sum(r["value"] for r in win)
            if len(buyers) >= min_buyers and total >= min_total:
                w_sum = sum(r["value"] for r in win)
                avg = sum(r["price"] * r["value"] for r in win) / w_sum if w_sum else None
                sl = [s for s in sells_by.get(tk, []) if 0 <= (d - s["t"]).days < window_d and not s["f10b5"]]
                events.append({"tk": tk, "date": d, "n_buyers": len(buyers), "total": round(total), "ceo": any(r["ceo"] for r in win),
                               "avg_price": avg, "first_buy": min(r["t"] for r in win), "sells_30d": len(sl)})
                last_ev = d
    events.sort(key=lambda e: (e["date"], e["tk"]))
    return events


# ------------------------------------------------------------------ cene
def _fetch_yahoo(sym, tries=3):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=6y&interval=1d" % urllib.request.quote(sym, safe="")
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                j = json.load(r)
            res = j["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose")
            out = []
            for i, ts in enumerate(res.get("timestamp") or []):
                o, c = q["open"][i], q["close"][i]
                if o and c:
                    f = (adj[i] / c) if adj and adj[i] else 1.0
                    out.append((dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat(), o * f, c * f, o))
            return out
        except Exception:  # mreza, 404 (nema simbola), 429
            time.sleep(1.5 * (k + 1))
    return None


def load_prices(syms, cache):
    os.makedirs(cache, exist_ok=True)

    def one(sym):
        p = os.path.join(cache, "d_%s.json" % sym.replace("/", "_").replace("^", ""))
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return sym, json.load(f)
        d = _fetch_yahoo(sym)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, separators=(",", ":"))
        return sym, d

    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for sym, d in ex.map(one, sorted(syms)):
            if d:
                out[sym] = {"d": [x[0] for x in d], "o": [x[1] for x in d], "c": [x[2] for x in d], "ro": [x[3] for x in d]}
    return out


def _idx_after(dates, day_iso):
    """Indeks prvog trgovackog dana STROGO posle datuma."""
    lo, hi = 0, len(dates)
    while lo < hi:
        mid = (lo + hi) // 2
        if dates[mid] <= day_iso:
            lo = mid + 1
        else:
            hi = mid
    return lo


def fwd(bars, i, h):
    """Prinos u % od otvaranja dana i do zatvaranja dana i+h-1 (h trgovackih dana), ili None."""
    if i + h - 1 >= len(bars["c"]) or not bars["o"][i]:
        return None
    return (bars["c"][i + h - 1] / bars["o"][i] - 1.0) * 100.0


def event_returns(ev, px, spy, horizons=HORIZONS):
    b = px.get(ev["tk"])
    if not b:
        return None
    i = _idx_after(b["d"], ev["date"].isoformat())
    j = _idx_after(spy["d"], ev["date"].isoformat())
    if i >= len(b["d"]) or j >= len(spy["d"]):
        return None
    chase = (b["ro"][i] / ev["avg_price"] - 1.0) * 100.0 if ev["avg_price"] else None
    out = {"chase": chase, "entry_gap_d": (dt.date.fromisoformat(b["d"][i]) - ev["date"]).days}
    for h in horizons:
        r, m = fwd(b, i, h), fwd(spy, j, h)
        out["r%d" % h] = None if r is None or m is None else r - m - COST_PCT  # prinos minus SPY minus trosak
        out["raw%d" % h] = r
    return out


def placebo_mean(events, px, spy, h, n_sims=200, seed=5):
    """Slucajni datumi za ISTE izdavaoce (po jedan po dogadjaju u svakoj simulaciji); vraca listu prosecnih 'prinos minus SPY minus trosak'."""
    rnd = random.Random(seed)
    tks = [e["tk"] for e in events if e["tk"] in px]
    sims = []
    for _ in range(n_sims):
        v = []
        for tk in tks:
            b = px[tk]
            n = len(b["d"])
            if n < h + 40:
                continue
            i = rnd.randrange(20, n - h)
            j = _idx_after(spy["d"], b["d"][i - 1])
            r, m = fwd(b, i, h), fwd(spy, j, h)
            if r is not None and m is not None:
                v.append(r - m - COST_PCT)
        if v:
            sims.append(st.mean(v))
    return sims


def week_key(d):
    y, w, _ = d.isocalendar()
    return (y, w)


def summarize(rows, h):
    """rows = [(event, returns)] -> n, srednje, medijana, udeo pozitivnih, t preko nedelja."""
    vals = [(e["date"], r["r%d" % h]) for e, r in rows if r and r.get("r%d" % h) is not None]
    if not vals:
        return {"n": 0}
    weeks = {}
    for d, v in vals:
        weeks.setdefault(week_key(d), []).append(v)
    wm = [st.mean(x) for x in weeks.values()]
    x = [v for _, v in vals]
    t = None
    if len(wm) >= 3 and st.stdev(wm) > 0:
        t = st.mean(wm) / (st.stdev(wm) / math.sqrt(len(wm)))
    return {"n": len(x), "weeks": len(wm), "mean": round(st.mean(x), 3), "median": round(st.median(x), 3), "pos": round(sum(1 for v in x if v > 0) / len(x), 3),
            "t": None if t is None else round(t, 2)}


def groups(rows):
    G = {"SVE": lambda e, r: True,
         "2 kupca": lambda e, r: e["n_buyers"] == 2,
         "3 kupca": lambda e, r: e["n_buyers"] == 3,
         "4+ kupaca": lambda e, r: e["n_buyers"] >= 4,
         "CEO/CFO/predsednik medju kupcima": lambda e, r: e["ceo"],
         "bez CEO/CFO": lambda e, r: not e["ceo"],
         "iznos >= $500k": lambda e, r: e["total"] >= 500000,
         "iznos < $250k": lambda e, r: e["total"] < 250000,
         "cena ulaza ispod proseka insidera": lambda e, r: r["chase"] is not None and r["chase"] < 0,
         "juri 0 do 15%": lambda e, r: r["chase"] is not None and 0 <= r["chase"] < 15,
         "juri 15 do 30%": lambda e, r: r["chase"] is not None and 15 <= r["chase"] < 30,
         "juri preko 30%": lambda e, r: r["chase"] is not None and r["chase"] >= 30,
         "GME recept: 4+ kupaca i juri preko 15%": lambda e, r: e["n_buyers"] >= 4 and r["chase"] is not None and r["chase"] >= 15,
         "bez prodaja u 30 d": lambda e, r: e["sells_30d"] == 0,
         "sa prodajama u 30 d": lambda e, r: e["sells_30d"] > 0,
         "cena akcije < $10": lambda e, r: e["avg_price"] is not None and e["avg_price"] < 10,
         "cena akcije $10-50": lambda e, r: e["avg_price"] is not None and 10 <= e["avg_price"] < 50,
         "cena akcije >= $50": lambda e, r: e["avg_price"] is not None and e["avg_price"] >= 50}
    for y in (2023, 2024, 2025, 2026):
        G["godina %d" % y] = (lambda yy: lambda e, r: e["date"].year == yy)(y)
    return {k: [(e, r) for e, r in rows if f(e, r)] for k, f in G.items()}


def run(buys, sells, px, spy, xyz=None, n_sims=200):
    events = find_clusters(buys, sells)
    rows = []
    missing = 0
    for e in events:
        r = event_returns(e, px, spy)
        if r is None:
            missing += 1
        else:
            rows.append((e, r))
    res = {"events": len(events), "priced": len(rows), "missing_prices": missing, "groups": {}, "horizons": {}}
    for h in HORIZONS:
        s = summarize(rows, h)
        pl = placebo_mean([e for e, _ in rows], px, spy, h, n_sims)
        if pl and s.get("n"):
            s["placebo_mean"] = round(st.mean(pl), 3)
            s["placebo_p"] = round((1 + sum(1 for x in pl if x >= s["mean"])) / (1 + len(pl)), 3)
        res["horizons"][h] = s
    for name, rs in groups(rows).items():
        res["groups"][name] = {h: summarize(rs, h) for h in HORIZONS}
    if xyz:
        sub = [(e, r) for e, r in rows if e["tk"] in xyz]
        res["xyz"] = {"n_events": len(sub), "summary": {h: summarize(sub, h) for h in HORIZONS}, "list": [(e["tk"], e["date"].isoformat(), e["n_buyers"], e["total"], None if r["chase"] is None else round(r["chase"], 1), None if r.get("r20") is None else round(r["r20"], 2)) for e, r in sub]}
    res["rows"] = rows
    return res


def to_markdown(res):
    L = ["# Klasteri insider kupovina (SEC Form 4, kod P): merenje", "",
         "Dogadjaja po unapred zadatom pravilu: %d, sa cenama: %d (bez cena: %d; izdavaoci bez Yahoo istorije su verovatno izbaceni sa berze, pa je ovo blago optimisticno - greska preziveli)." % (res["events"], res["priced"], res["missing_prices"]),
         "Mera: prinos od otvaranja prvog dana posle prijave do zatvaranja posle H trgovackih dana, MINUS SPY, MINUS trosak %.2f%%. t je preko nedelja prijave. Placebo = isti izdavaoci, slucajni datumi." % COST_PCT, "",
         "## Svi dogadjaji, po horizontu", "", "| H (dana) | n | nedelja | srednje % | medijana % | udeo > 0 | t | placebo srednje % | p protiv placeba |", "|---|---|---|---|---|---|---|---|---|"]
    for h, s in res["horizons"].items():
        if s.get("n"):
            L.append("| %d | %d | %d | %+.2f | %+.2f | %.2f | %s | %s | %s |" % (h, s["n"], s["weeks"], s["mean"], s["median"], s["pos"], s["t"], s.get("placebo_mean"), s.get("placebo_p")))
    L += ["", "## Podgrupe (primarni horizont %d dana; ostali su orijentacija). Podgrupe su istrazivacke, bez korekcije za mnogo poredjenja." % PRIMARY_H, "",
          "| podgrupa | n | srednje % | medijana % | udeo > 0 | t | srednje % (H=5) | srednje % (H=60) |", "|---|---|---|---|---|---|---|---|"]
    for name, g in res["groups"].items():
        s = g[PRIMARY_H]
        if s.get("n"):
            L.append("| %s | %d | %+.2f | %+.2f | %.2f | %s | %s | %s |" % (name, s["n"], s["mean"], s["median"], s["pos"], s["t"], g[5].get("mean"), g[60].get("mean")))
    if res.get("xyz"):
        x = res["xyz"]
        L += ["", "## Samo akcije koje se trguju na Liquid-u (xyz): %d dogadjaja" % x["n_events"], "", "| H | n | srednje % | udeo > 0 | t |", "|---|---|---|---|---|"]
        for h, s in x["summary"].items():
            if s.get("n"):
                L.append("| %d | %d | %+.2f | %.2f | %s |" % (h, s["n"], s["mean"], s["pos"], s["t"]))
        L += ["", "| akcija | datum prijave | kupaca | iznos $ | juri % | prinos 20 d % (minus SPY, trosak) |", "|---|---|---|---|---|---|"]
        for row in x["list"]:
            L.append("| %s | %s | %d | %d | %s | %s |" % row)
    return "\n".join(L) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base, out_md = args[0], args[1]
    xyz = None
    cache = os.path.join(base, "_px")
    for i, a in enumerate(sys.argv):
        if a == "--xyz":
            with open(sys.argv[i + 1], encoding="utf-8") as f:
                xyz = {x.replace("xyz:", "") for x in json.load(f)}
        if a == "--cache":
            cache = sys.argv[i + 1]
    buys, sells = [], []
    for q in sorted(os.listdir(base)):
        p = os.path.join(base, q)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "SUBMISSION.tsv")):
            b, s = load_quarter(p)
            buys += b
            sells += s
            print(q, len(b), "kupovina,", len(s), "prodaja", flush=True)
    events = find_clusters(buys, sells)
    syms = {e["tk"] for e in events} | {"SPY"}
    print("dogadjaja", len(events), "izdavalaca", len(syms) - 1, flush=True)
    px = load_prices(syms, cache)
    spy = px.pop("SPY")
    res = run(buys, sells, px, spy, xyz)
    md = to_markdown(res)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
