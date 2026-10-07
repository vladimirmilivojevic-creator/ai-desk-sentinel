"""Statistika koja ne laze: neto posle troska, nepreklapajuci uzorci, t-vrednost po DANIMA (korelisani instrumenti se ne broje kao
nezavisni), deo podataka za proveru i Bonferroni korekcija za broj testiranih varijanti."""
import math
import statistics as st
from statistics import NormalDist

DAY_MS = 86400000


def thin(signals, H):
    """Nepreklapajuci uzorci: po instrumentu najmanje H svece izmedju ulaza. signals: lista (sym, i, t, side) sortirana po (sym, i)."""
    out, last = [], {}
    for s in signals:
        sym, i = s[0], s[1]
        if sym in last and i < last[sym] + H:
            continue
        last[sym] = i
        out.append(s)
    return out


def daily_t(rets_by_ts):
    """rets_by_ts: lista (t_ms, ret%). Prosek po danu, pa srednja vrednost po danima i t."""
    days = {}
    for t, r in rets_by_ts:
        days.setdefault(t // DAY_MS, []).append(r)
    avg = [sum(v) / len(v) for _, v in sorted(days.items())]
    n = len(avg)
    if n < 3:
        return {"days": n, "mean_day": None, "t": None}
    m = st.mean(avg)
    sd = st.stdev(avg)
    return {"days": n, "mean_day": round(m, 4), "t": None if sd == 0 else round(m / (sd / math.sqrt(n)), 2)}


def summarize(trades, t_min, t_max, split=0.6):
    """trades: lista (t_ms, ret%, sym). Ukupno + prvi (60%) i drugi (40%) deo vremenskog prozora."""
    if not trades:
        return {"n": 0}
    cut = t_min + (t_max - t_min) * split
    a = [(t, r) for t, r, _ in trades if t < cut]
    b = [(t, r) for t, r, _ in trades if t >= cut]
    rets = [r for _, r, _ in trades]
    out = {"n": len(trades), "mean": round(st.mean(rets), 4),
           "win_pct": round(100.0 * sum(1 for x in rets if x > 0) / len(rets), 1),
           "all": daily_t([(t, r) for t, r, _ in trades])}
    out["train"] = dict(daily_t(a), n=len(a), mean=round(st.mean([r for _, r in a]), 4) if a else None)
    out["test"] = dict(daily_t(b), n=len(b), mean=round(st.mean([r for _, r in b]), 4) if b else None)
    return out


def t_to_p(t):
    """Dvostrana p-vrednost iz t (normalna aproksimacija; broj dana je velik)."""
    return 2.0 * (1.0 - NormalDist().cdf(abs(t)))


def bh_fdr(pvals, q=0.10):
    """Benjamini-Hochberg: kontrola ocekivanog udela lazno otkrivenih. pvals: lista (kljuc, p). Vraca skup kljuceva koji prolaze."""
    items = sorted((p, k) for k, p in pvals if p is not None)
    m = len(items)
    cut = 0
    for rank, (p, _) in enumerate(items, start=1):
        if p <= rank / m * q:
            cut = rank
    return {k for _, k in items[:cut]}


def summarize_windows(trades, windows):
    """trades: lista (t_ms, ret%, sym); windows: lista (ime, t_od, t_do). Vraca {ime: {n, mean, t}} (t po danima)."""
    out = {}
    for name, a, b in windows:
        rows = [(t, r) for t, r, _ in trades if a <= t < b]
        if not rows:
            out[name] = {"n": 0, "mean": None, "t": None}
            continue
        d = daily_t(rows)
        out[name] = {"n": len(rows), "mean": round(st.mean(r for _, r in rows), 4), "t": d["t"]}
    return out


def bonferroni_z(k, alpha=0.05):
    return NormalDist().inv_cdf(1.0 - alpha / 2.0 / max(k, 1))


def verdict(s, k_tests):
    """potvrdjeno: t >= Bonferroni z i oba dela pozitivna; obecava: t >= 2 u OBA dela; slabo: ukupno t >= 2; inace odbaceno."""
    if not s or s.get("n", 0) < 30:
        return "premalo"
    tt, ta, tb = s["all"].get("t"), s["train"].get("t"), s["test"].get("t")
    if tt is None or ta is None or tb is None:
        return "premalo"
    if s["mean"] <= 0:
        return "odbaceno"
    if tt >= bonferroni_z(k_tests) and ta > 0 and tb > 0:
        return "potvrdjeno"
    if ta >= 2.0 and tb >= 2.0:
        return "obecava"
    if tt >= 2.0 and ta > 0 and tb > 0:
        return "slabo"
    return "odbaceno"
