"""Studija: da li se cene pomeraju posle Trumpovih objava odredjenih tema? Istorija: CNN arhiva Truth Social objava (ix.cnn.io, od 2022) i Yahoo satne svece
(do 730 dana) za 6 trzista + 10 akcija. Recnik tema je unapred upisan (config/trump_tags.json, commit pre rezultata).

Metod (pozitivno nepoverenje prema sebi):
- Dogadjaj = prva objava teme u UTC danu (bez RT). Ulaz = otvaranje prve svece koja pocinje najranije 60 min posle objave (toliko mi kasnimo, "lag"); "instant" (odmah) je samo opis reakcije.
- Prinos posle 1, 4 i 24 h. Kontrola = SVE svece istog sata u danu i iste vrste dana (radni/vikend) na danima bez te teme. Potpisan prinos i apsolutni prinos (volatilnost) su dva testa.
- Benjamini-Hochberg (q = 0.10) preko cele porodice testova; placebo teme (nasumicni dani sa istim brojem i istim dobom dana) mere koliko je lazno pozitivnih.
- Nalaz = prolazi FDR u primarnom periodu (od 2025-01-20), znak isti u obe polovine perioda i n >= 40. Raniji period (od 2024-05) je samo provera ponavljanja.
Samo stdlib. Upotreba: python -m lab.trump_study [csv] [out_json] [out_md]"""
import bisect
import csv
import datetime as dt
import json
import math
import os
import random
import statistics as st
import sys
import time
import urllib.parse

from . import netutil, stats, trump

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "lab", "cache", "trump")
HOUR = 3600 * 1000
HORIZONS = (1, 4, 24)
MIN_N = 25
MAX_GAP = 90 * 60 * 1000
LAG = 60 * 60 * 1000


# ---------------------------------------------------------------- ucitavanje
def load_posts(path, lex):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            text = r.get("content") or ""
            if not text.strip():
                continue
            tg = trump.tag_text(text, lex)
            if tg["rt"]:
                continue
            try:
                ts = int(dt.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).timestamp() * 1000)
            except ValueError:
                continue
            out.append({"ts": ts, "topics": tg["topics"], "companies": tg["companies"], "shout": tg["shout"]})
    out.sort(key=lambda p: p["ts"])
    return out


class Bars:
    def __init__(self, t, o):
        self.t, self.o = t, o


def _fetch_yahoo(ticker):
    j = netutil.get_json("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=730d&interval=1h&includePrePost=false" % urllib.parse.quote(ticker, safe=""),
                         tries=3, pause=0.4, ua=netutil.BROWSER_UA, max_bytes=20_000_000)
    r = j["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    rows = [(ts * 1000, o) for ts, o in zip(r["timestamp"], q["open"]) if o is not None]
    return {"t": [a for a, _ in rows], "o": [b for _, b in rows]}


def load_bars(ticker, max_age_s=12 * 3600):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "y_%s.json" % ticker.replace("=", "_").replace("^", ""))
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age_s:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    else:
        d = _fetch_yahoo(ticker)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, separators=(",", ":"))
    return Bars(d["t"], d["o"])


# ---------------------------------------------------------------- prinosi i kontrola
def _daytype(ms):
    return 1 if dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).weekday() >= 5 else 0


def _key(ms):
    return (dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).hour, _daytype(ms))


def _day(ms):
    return ms // (24 * HOUR)


def fwd_ret(b, i, h):
    """Prinos od otvaranja svece i do otvaranja prve svece koja pocinje najranije h sati kasnije (najvise MAX_GAP docnije), u %."""
    due = b.t[i] + h * HOUR
    j = bisect.bisect_left(b.t, due, i + 1)
    if j >= len(b.t) or b.t[j] - due > MAX_GAP or not b.o[i]:
        return None
    return (b.o[j] / b.o[i] - 1.0) * 100.0


class Control:
    """Za (instrument, horizont): zbirovi prinosa po (sat, vrsta dana) i po danu, da se dani teme lako oduzmu."""

    def __init__(self, b, h, start, end):
        self.tot, self.by_day = {}, {}
        for i, t in enumerate(b.t):
            if t < start or t >= end:
                continue
            r = fwd_ret(b, i, h)
            if r is None:
                continue
            k, d = _key(t), _day(t)
            for acc in (self.tot, self.by_day.setdefault(d, {})):
                s = acc.setdefault(k, [0.0, 0.0, 0])
                s[0] += r
                s[1] += abs(r)
                s[2] += 1

    def means(self, exclude_days):
        tot = {k: list(v) for k, v in self.tot.items()}
        for d in exclude_days:
            for k, v in self.by_day.get(d, {}).items():
                if k in tot:
                    tot[k][0] -= v[0]
                    tot[k][1] -= v[1]
                    tot[k][2] -= v[2]
        return {k: (v[0] / v[2], v[1] / v[2]) for k, v in tot.items() if v[2] >= 20}


def _t(vals):
    n = len(vals)
    if n < 3:
        return None
    sd = st.pstdev(vals) * math.sqrt(n / (n - 1))
    return None if sd == 0 else st.mean(vals) / (sd / math.sqrt(n))


def event_times(posts, pred, start, end):
    """Prva objava teme po UTC danu u [start, end)."""
    first = {}
    for p in posts:
        if start <= p["ts"] < end and pred(p) and _day(p["ts"]) not in first:
            first[_day(p["ts"])] = p["ts"]
    return sorted(first.values())


def cell(b, ctrl, times, h, lag):
    """Jedna celija testa: lista odstupanja od kontrole za potpisan i apsolutni prinos."""
    ev_days = set(_day(t) for t in times)
    cm = ctrl.means(ev_days)
    d_sig, d_abs, used = [], [], []
    for ts in times:
        i = bisect.bisect_left(b.t, ts + (LAG if lag else 0))
        if i >= len(b.t) or b.t[i] - (ts + (LAG if lag else 0)) > (MAX_GAP if lag else 30 * 60 * 1000):
            continue
        r = fwd_ret(b, i, h)
        k = _key(b.t[i])
        if r is None or k not in cm:
            continue
        d_sig.append(r - cm[k][0])
        d_abs.append(abs(r) - cm[k][1])
        used.append(ts)
    return d_sig, d_abs, used


def summarize_cell(d_sig, d_abs):
    n = len(d_sig)
    if n < MIN_N:
        return None
    ts_, ta = _t(d_sig), _t(d_abs)
    if ts_ is None or ta is None:
        return None
    half = n // 2
    h1, h2 = st.mean(d_sig[:half]), st.mean(d_sig[half:])
    m = st.mean(d_sig)
    return {"n": n, "mean": round(m, 4), "t": round(ts_, 2), "p": stats.t_to_p(ts_), "abs_excess": round(st.mean(d_abs), 4), "t_abs": round(ta, 2), "p_abs": stats.t_to_p(ta),
            "stable": (h1 > 0) == (h2 > 0) == (m > 0)}


def run_window(posts, bars, cfg, start, end, with_instant=True, placebo=100, seed=7, log=lambda *a: None):
    """Vraca {"rows": [...], "placebo": {...}} za jedan period."""
    ctrls = {(tk, h): Control(b, h, start, end) for tk, b in bars.items() for h in HORIZONS}
    topics = {k: (lambda p, k=k: k in p["topics"]) for k in cfg["topics"]}
    topics["shout"] = lambda p: p["shout"]
    company = {k: (lambda p, k=k: k in p["companies"]) for k in cfg["companies"]}
    rows = []
    for tag, pred in list(topics.items()) + list(company.items()):
        times = event_times(posts, pred, start, end)
        if len(times) < MIN_N:
            continue
        targets = [cfg["companies"][tag]["ticker"]] if tag in cfg["companies"] else list(bars)
        for tk in targets:
            if tk not in bars:
                continue
            for h in HORIZONS:
                for mode in (("lag", True), ("instant", False)) if with_instant else (("lag", True),):
                    s = summarize_cell(*cell(bars[tk], ctrls[(tk, h)], times, h, mode[1])[:2])
                    if s:
                        rows.append(dict(s, tag=tag, ticker=tk, hl=cfg["instruments"].get(tk), h=h, mode=mode[0], events=len(times)))
    # placebo: isti broj dogadjaja, nasumicni dani, stvarna doba dana
    rnd = random.Random(seed)
    days = {}
    for p in posts:
        if start <= p["ts"] < end:
            days.setdefault(_day(p["ts"]), []).append(p["ts"])
    keys = sorted(days)
    sizes = sorted(len(event_times(posts, pred, start, end)) for pred in topics.values())
    k_ev = max(MIN_N + 5, sizes[len(sizes) // 2]) if sizes else MIN_N + 5
    pl_t = []
    pl_by_h = {h: ([], []) for h in HORIZONS}
    for _ in range(placebo):
        times = sorted(rnd.choice(days[d]) for d in rnd.sample(keys, min(k_ev, len(keys))))
        for tk, b in bars.items():
            for h in HORIZONS:
                s = summarize_cell(*cell(b, ctrls[(tk, h)], times, h, True)[:2])
                if s:
                    pl_t.append((s["t"], s["p"], s["t_abs"], s["p_abs"]))
                    pl_by_h[h][0].append(abs(s["t"]))
                    pl_by_h[h][1].append(abs(s["t_abs"]))
    n_pl = len(pl_t)
    pl = {"n_tests": n_pl, "events_each": k_ev, "share_abs_t_gt2": round(sum(1 for t in pl_t if abs(t[0]) > 2) / n_pl, 4) if n_pl else None,
          "share_abs_t_gt2_vol": round(sum(1 for t in pl_t if abs(t[2]) > 2) / n_pl, 4) if n_pl else None}
    pl["by_h"] = {h: [sorted(v[0]), sorted(v[1])] for h, v in pl_by_h.items()}
    return {"rows": rows, "placebo": pl}


def emp_p(t, null_sorted):
    """Empirijska dvostrana p-vrednost iz placebo raspodele |t| (ispravlja debele repove i preklapanje prozora): (1 + broj placebo >= |t|) / (1 + N)."""
    if not null_sorted:
        return stats.t_to_p(t)
    ge = len(null_sorted) - bisect.bisect_left(null_sorted, abs(t))
    return (1.0 + ge) / (1.0 + len(null_sorted))


def findings(res_primary, res_pre, q=0.10):
    rows = [r for r in res_primary["rows"] if r["mode"] == "lag"]
    by_h = res_primary["placebo"].get("by_h") or {}
    for r in rows:
        nh = by_h.get(r["h"]) or [[], []]
        r["p_emp"], r["p_emp_abs"] = emp_p(r["t"], nh[0]), emp_p(r["t_abs"], nh[1])
    sig = stats.bh_fdr([(i, r["p_emp"]) for i, r in enumerate(rows)], q)
    vol = stats.bh_fdr([(i, r["p_emp_abs"]) for i, r in enumerate(rows)], q)
    pre = {(r["tag"], r["ticker"], r["h"]): r for r in res_pre["rows"] if r["mode"] == "lag"}
    out = []
    for i, r in enumerate(rows):
        for kind, ok in (("potpisan", i in sig), ("volatilnost", i in vol)):
            if not ok or r["n"] < 40 or (kind == "potpisan" and not r["stable"]):
                continue
            p0 = pre.get((r["tag"], r["ticker"], r["h"]))
            same = None
            if p0:
                same = ((p0["mean"] > 0) == (r["mean"] > 0)) if kind == "potpisan" else (p0["abs_excess"] > 0) == (r["abs_excess"] > 0)
            out.append({"kind": kind, "tag": r["tag"], "ticker": r["ticker"], "hl": r["hl"], "h": r["h"], "n": r["n"], "mean_pct": r["mean"], "t": r["t"], "abs_excess_pct": r["abs_excess"],
                        "t_abs": r["t_abs"], "replicates_pre": same})
    return out, len(rows), len(sig), len(vol)


def to_markdown(res):
    L = ["# Trump studija: reakcija cena na objave", "",
         "Period (primarni): %s do %s; ranije (provera): %s do %s. Objava = prva objava teme u UTC danu. Ulaz = prvi sat najmanje 60 min posle objave." % (res["window"]["primary"][0], res["window"]["primary"][1],
                                                                                                                                     res["window"]["pre"][0], res["window"]["pre"][1]), "",
         "Testova (lag, primarni period): %d. Sirovo |t| > 2: %d (po slucaju se ocekuje oko %.0f%%). Prolaze FDR (p-vrednosti kalibrisane placebom): potpisan %d, volatilnost %d." % (res["n_tests"], res["raw_t2"], 100 * (res["placebo"].get("share_abs_t_gt2") or 0.05), res["n_fdr_signed"], res["n_fdr_vol"]),
         "Placebo (nasumicni dani, isti broj dogadjaja): udeo |t| > 2 u potpisanom testu %s, u volatilnosti %s." % (res["placebo"].get("share_abs_t_gt2"), res["placebo"].get("share_abs_t_gt2_vol")), ""]
    if res["findings"]:
        L += ["## Nalazi (prolaze FDR, isti znak u obe polovine, n >= 40)", "", "| vrsta | tema | trziste | sati | n | prosek % | t | apsolutni prinos viši za % | t (volatilnost) | ponavlja se u ranijem periodu |", "|---|---|---|---|---|---|---|---|---|---|"]
        for f in res["findings"]:
            L.append("| %s | %s | %s | %d | %d | %+.3f | %.2f | %+.3f | %.2f | %s |" % (f["kind"], f["tag"], f["ticker"], f["h"], f["n"], f["mean_pct"], f["t"], f["abs_excess_pct"], f["t_abs"], {True: "da", False: "ne", None: "nema podataka"}[f["replicates_pre"]]))
    else:
        L += ["## Nalazi", "", "Nijedna kombinacija ne prolazi sve uslove. Iskren odgovor: u ovim podacima nema dokazane prednosti od reagovanja na teme objava."]
    L += ["", "## Najjaci sirovi rezultati (BEZ korekcije, samo za oko)", "", "| tema | trziste | sati | mod | n | prosek % | t | t volatilnost |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(res["top_raw"], key=lambda r: -abs(r["t"]))[:20]:
        L.append("| %s | %s | %d | %s | %d | %+.3f | %.2f | %.2f |" % (r["tag"], r["ticker"], r["h"], r["mode"], r["n"], r["mean"], r["t"], r["t_abs"]))
    return "\n".join(L) + "\n"


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(CACHE, "truth_archive.csv")
    out_json = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "calibration", "trump_study.json")
    out_md = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "calibration", "trump_study.md")
    lex = trump.load_lexicon()
    cfg = lex["raw"]
    posts = load_posts(csv_path, lex)
    print("objava (bez RT, sa tekstom):", len(posts))
    bars = {}
    for tk in cfg["instruments"]:
        try:
            bars[tk] = load_bars(tk)
        except Exception as e:  # noqa: BLE001
            print("preskacem", tk, type(e).__name__)
    last = max(b.t[-1] for b in bars.values())
    ms = lambda s: int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)  # noqa: E731
    p0, p1, e0 = ms(cfg["primary_start_utc"]), last - 26 * HOUR, ms(cfg["pre_start_utc"])
    primary = run_window(posts, bars, cfg, p0, p1)
    pre = run_window(posts, bars, cfg, e0, p0, with_instant=False, placebo=0)
    fnd, n_tests, n_sig, n_vol = findings(primary, pre)
    lag_rows = [r for r in primary["rows"] if r["mode"] == "lag"]
    iso = lambda m: dt.datetime.fromtimestamp(m / 1000, dt.timezone.utc).strftime("%Y-%m-%d")  # noqa: E731
    res = {"generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "lexicon_version": cfg["version"], "window": {"primary": [iso(p0), iso(p1)], "pre": [iso(e0), iso(p0)]},
           "n_tests": n_tests, "raw_t2": sum(1 for r in lag_rows if abs(r["t"]) > 2), "n_fdr_signed": n_sig, "n_fdr_vol": n_vol, "placebo": {k: v for k, v in primary["placebo"].items() if k != "by_h"}, "findings": fnd,
           "top_raw": sorted(primary["rows"], key=lambda r: -abs(r["t"]))[:30], "rows": primary["rows"]}
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(to_markdown(res))
    ev = {"generated_utc": res["generated_utc"], "source": "trump_study", "window": res["window"]["primary"], "tests": res["n_tests"], "raw_t2": res["raw_t2"],
          "fdr_pass": n_sig + n_vol, "placebo_t2_share": primary["placebo"].get("share_abs_t_gt2"), "findings": fnd[:6],
          "hints_not_evidence": [{"tag": r["tag"], "ticker": r["ticker"], "h": r["h"], "mode": r["mode"], "n": r["n"], "mean_pct": r["mean"], "t": r["t"]}
                                  for r in sorted(lag_rows, key=lambda r: -abs(r["t"]))[:3]],
          "note": "Reakcija cena na teme Trumpovih objava (ulaz 60 min posle objave). Bez nalaza koji prolaze placebom kalibrisan FDR znaci: nema dokazane prednosti; sirovi 'hints' su sumnje, ne dokaz."}
    with open(os.path.join(ROOT, "config", "events_evidence.json"), "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
