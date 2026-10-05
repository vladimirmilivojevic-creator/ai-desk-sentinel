"""Kalibracija pragova na istoriji (samo cenovna porodica P, deterministicka).
Mozak se NE replay-uje na istoriji (pamcenje modela); vesti se kalibrisu u senci.

Pokretanje: python -m sentinel.replay [--source yahoo|hl] [--out replay_result.md]
Izlaz: koliko puta dnevno bi prag okinuo, i sta se desavalo posle (+4 h, +24 h, +72 h),
u poredjenju sa osnovom (svi sati, nasumican ulaz u istom smeru).
"""
import argparse
import json
import os
import statistics
import time

from . import sources
from .util import pct

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(os.path.dirname(HERE), "config")
MULTS = (0.8, 1.0, 1.25, 1.5, 2.0)
FWD = (4, 24, 72)


def load_hourly(inst, source):
    if source == "yahoo" and inst.get("yahoo") and inst["class"] != "crypto":
        rows = sources.yahoo_series(inst["yahoo"], "1h", "2y")
        return [(t - 3600, c) for t, c in rows], "yahoo"  # (pocetak sata, close)
    rows = sources.hl_candles(inst["hl"], "1h", 5000 * 60)
    return [(t - 3600, c) for t, c in rows], "hl"


def fwd_return(ts_list, px_list, i, hours):
    target = ts_list[i] + hours * 3600
    j = i
    while j < len(ts_list) and ts_list[j] < target:
        j += 1
    if j >= len(ts_list) or ts_list[j] - target > 2 * 3600:
        return None
    return pct(px_list[j], px_list[i])


def analyse(inst, rows):
    ts = [t for t, _ in rows]
    px = [c for _, c in rows]
    n = len(rows)
    days = (ts[-1] - ts[0]) / 86400.0 if n > 1 else 0
    rets = [None] + [pct(px[i], px[i - 1]) if ts[i] - ts[i - 1] <= 4500 else None for i in range(1, n)]
    out = {"days": days, "n": n, "rows": []}
    base = {h: [] for h in FWD}
    for i in range(n):
        for h in FWD:
            r = fwd_return(ts, px, i, h)
            if r is not None:
                base[h].append(abs(r))
    out["base_abs"] = {h: (statistics.mean(v) if v else None) for h, v in base.items()}
    # klizna sigma jednosatnih promena (plain float, O(n))
    sig = [None] * n
    win_n, ssum, ssq = 0, 0.0, 0.0
    from collections import deque
    q = deque()
    for i in range(n):
        if i > 0 and rets[i] is not None:
            pass
        # sigma za bar i racuna se iz prethodnih (do 480) promena, bez i
        if len(q) >= 100:
            mean = ssum / len(q)
            var = max(ssq / len(q) - mean * mean, 0.0)
            sig[i] = var ** 0.5
        r = rets[i]
        if r is not None:
            q.append(r)
            ssum += r
            ssq += r * r
            if len(q) > 480:
                x = q.popleft()
                ssum -= x
                ssq -= x * x
    for m in MULTS:
        thr60, thr240 = inst["thr60"] * m, inst["thr240"] * m
        events, last_i = [], -999
        for i in range(24, n):
            r60 = rets[i]
            r240 = pct(px[i], px[i - 4]) if ts[i] - ts[i - 4] <= 5 * 3600 else None
            e60 = max(thr60, 4 * sig[i]) if sig[i] else thr60
            e240 = max(thr240, 8 * sig[i]) if sig[i] else thr240
            hit60 = r60 is not None and abs(r60) >= e60
            hit240 = r240 is not None and abs(r240) >= e240
            if (hit60 or hit240) and i - last_i >= 6:  # 6 h mirovanja = jedan dogadjaj
                mv = r60 if hit60 else r240
                events.append((i, 1 if mv > 0 else -1))
                last_i = i
        row = {"mult": m, "events": len(events), "per_day": len(events) / days if days else None}
        for h in FWD:
            cont = []
            for i, d in events:
                r = fwd_return(ts, px, i, h)
                if r is not None:
                    cont.append(r * d)
            row["fwd_%d" % h] = (statistics.mean(cont) if cont else None, len(cont),
                                 (sum(1 for x in cont if x > 0) / len(cont)) if cont else None)
        out["rows"].append(row)
    return out


def fmt(x, nd=2):
    return "n/a" if x is None else ("%+.*f" % (nd, x))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="yahoo")
    ap.add_argument("--out", default="replay_result.md")
    a = ap.parse_args(argv)
    insts = [i for i in json.load(open(os.path.join(CONFIG, "instruments.json"), encoding="utf-8"))["instruments"]
             if not i.get("ctx_only")]
    lines = ["# Replay P-porodice (cenovni okidac), izvor: %s, generisano %s" % (a.source, time.strftime("%Y-%m-%d %H:%MZ", time.gmtime())),
             "", "Svaki red: koliko je puta dnevno prag okinuo i prosecan povrat POSLE okidaca u smeru pomaka",
             "(pozitivno = nastavak, negativno = vracanje). `osnova` = prosecan apsolutni povrat bilo kog sata.",
             "Okidac: |pomak 60 min| >= max(prag, 4 sigma) ili |pomak 4 h| >= max(prag240, 8 sigma); 6 h mirovanja = isti dogadjaj.",
             "Ovo je kalibracija ucestalosti, NE dokaz dobiti. Mali uzorak i smer-nastavak/vracanje nisu zakljucak.", ""]
    for inst in insts:
        try:
            rows, src = load_hourly(inst, a.source)
        except Exception as e:
            lines.append("## %s: izvor nije dostupan (%s)\n" % (inst["name"], type(e).__name__))
            continue
        r = analyse(inst, rows)
        lines.append("## %s (%s, %d satnih sveca, %.0f dana, prag %.1f%%/60m)" % (inst["name"], src, r["n"], r["days"], inst["thr60"]))
        lines.append("osnova |povrat| posle 4/24/72 h: " + " / ".join(fmt(r["base_abs"][h]) + "%" for h in FWD))
        lines.append("")
        lines.append("| prag x | dogadjaja | dnevno | +4h (n, uspeh) | +24h | +72h |")
        lines.append("|---|---|---|---|---|---|")
        for row in r["rows"]:
            cells = []
            for h in FWD:
                mean, n, hit = row["fwd_%d" % h]
                cells.append("%s%% (%d, %s)" % (fmt(mean), n, "n/a" if hit is None else "%.0f%%" % (hit * 100)))
            lines.append("| %.2f | %d | %.3f | %s |" % (row["mult"], row["events"], row["per_day"] or 0, " | ".join(cells)))
        lines.append("")
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    main()
