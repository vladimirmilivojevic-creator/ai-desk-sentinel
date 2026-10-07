"""Portfolio simulacija poretka unutar grupe (CSM) na dnevnim svecama: dugo najjaci, kratko najslabiji, drzanje H dana, jedan 'tranš' dnevno
(1/H kapitala), trosak po krugu, dnevna kriva kapitala, Sharpe, najveci pad i rezultat po godinama. Ovo je prava mera strategije
(korpa), a ne pojedinacnih trejdova. Samo stdlib. Upotreba: python -m lab.portfolio_sim [grupa=crypto]"""
import datetime as dt
import math
import statistics as st
import sys

from . import backtest

DAY = 86400000


def basket_series(members, score, H=7, k=5, sign=1, cost_pct=0.23, min_names=8, delay=0):
    """Opsta korpa: svaki dan poredak instrumenata po skoru, dugo k najvisih i kratko k najnizih (sign=-1: obrnuto), drzanje H dana.
    score(mi, i, t) vraca broj ili None (i = indeks svece t kod instrumenta mi). Vraca listu (t_ms, dnevni prinos kapitala %) i broj tranša."""
    idx = [{t: i for i, t in enumerate(m.t)} for m in members]
    all_t = sorted(set(t for m in members for t in m.t))
    # tranše: otvaraju se na zatvaranju dana t, traju H dana
    tranches = []  # (t_open, [long_members_idx], [short_members_idx])
    for t in all_t:
        vals = []
        for mi, ix in enumerate(idx):
            i = ix.get(t)
            if i is None:
                continue
            v = score(mi, i, t)
            if v is not None:
                vals.append((v, mi))
        if len(vals) < min_names:
            continue
        vals.sort()
        kk = min(k, len(vals) // 3)
        low, high = [mi for _, mi in vals[:kk]], [mi for _, mi in vals[-kk:]]
        tranches.append((t + delay * DAY, high if sign > 0 else low, low if sign > 0 else high))  # delay: ulaz kasni delay dana posle signala
    out = {}
    for t_open, longs, shorts in tranches:
        for d in range(1, H + 1):
            t = t_open + d * DAY
            rl, rs = [], []
            for mi in longs:
                ix = idx[mi]
                a, b = ix.get(t_open + (d - 1) * DAY), ix.get(t)
                if a is not None and b is not None:
                    rl.append(members[mi].c[b] / members[mi].c[a] - 1.0)
            for mi in shorts:
                ix = idx[mi]
                a, b = ix.get(t_open + (d - 1) * DAY), ix.get(t)
                if a is not None and b is not None:
                    rs.append(members[mi].c[b] / members[mi].c[a] - 1.0)
            if not rl or not rs:
                continue
            day_ret = (sum(rl) / len(rl) - sum(rs) / len(rs)) / 2.0  # po jedinici kapitala tranša (pola dugo, pola kratko)
            out[t] = out.get(t, 0.0) + day_ret * 100.0 / H
        # trosak: otvaranje i zatvaranje tranša, 1/H kapitala (placa se na dan otvaranja)
        out[t_open] = out.get(t_open, 0.0) - cost_pct / H
    rows = sorted(out.items())
    return rows, len(tranches)


def csm_series(series, group="crypto", L=14, H=7, k=5, momentum=True, cost_pct=0.23, min_names=8, delay=0):
    """Poredak po prinosu u poslednjih L dana (momentum: dugo najjaci). series: {sym: Series} (dnevne svece)."""
    members = [s for s in series.values() if s.group == group]

    def score(mi, i, t):
        m = members[mi]
        return m.c[i] / m.c[i - L] - 1.0 if i >= L else None

    return basket_series(members, score, H, k, 1 if momentum else -1, cost_pct, min_names, delay)


def metrics(rows, t_from=None, t_to=None):
    """rows: lista (t_ms, dnevni prinos %). Vraca Sharpe (godisnji), t, prinos, pad i rezultat po godinama."""
    if t_from is not None or t_to is not None:
        rows = [(t, x) for t, x in rows if (t_from is None or t >= t_from) and (t_to is None or t < t_to)]
    if len(rows) < 30:
        return {"n_days": len(rows)}
    r = [x for _, x in rows]
    mu, sd = st.mean(r), st.pstdev(r)
    eq, peak, mdd = 1.0, 1.0, 0.0
    byy = {}
    for t, x in rows:
        eq *= 1 + x / 100.0
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1.0)
        y = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).year
        byy.setdefault(y, []).append(x)
    ann = lambda v: v * 365  # noqa: E731
    return {"n_days": len(r), "sharpe": round(mu / sd * math.sqrt(365), 3) if sd > 0 else None,
            "t": round(mu / (sd / math.sqrt(len(r))), 2) if sd > 0 else None, "ann_return_pct": round(ann(mu), 2),
            "ann_vol_pct": round(sd * math.sqrt(365), 2), "max_dd_pct": round(mdd * 100, 2), "total_pct": round((eq - 1) * 100, 2),
            "by_year": {y: {"sharpe": round(st.mean(v) / st.pstdev(v) * math.sqrt(365), 2) if len(v) > 10 and st.pstdev(v) > 0 else None,
                            "ann_return_pct": round(st.mean(v) * 365, 2), "n": len(v)} for y, v in sorted(byy.items())}}


def vol_managed(rows, target_ann_pct=20.0, win=30, cap=1.0):
    """Ciljana volatilnost na nivou korpe: skala dana = min(cap, cilj / realizovana vol zadnjih `win` dana) (samo PRETHODNI dani, bez gledanja unapred).
    cap=1.0 znaci samo smanjenje rizika kad je tržište nemirno, nikad poluga (tvrdo pravilo: 1x)."""
    out, past = [], []
    for t, x in rows:
        if len(past) >= win:
            sd = st.pstdev(past[-win:]) * math.sqrt(365)
            scale = cap if sd <= 0 else min(cap, target_ann_pct / sd)
        else:
            scale = cap
        out.append((t, x * scale))
        past.append(x)  # realizovana vol se meri na NEskaliranom prinosu strategije
    return out


def grid(series, group, Ls=(7, 14, 21, 30), Hs=(3, 7, 14), ks=(3, 5, 8), cost_pct=0.23):
    res = []
    for L in Ls:
        for H in Hs:
            for k in ks:
                rows, n = csm_series(series, group, L, H, k, True, cost_pct)
                m = metrics(rows)
                if m.get("n_days", 0) >= 30:
                    res.append(dict(m, L=L, H=H, k=k, tranches=n))
    return res


def ts_ms(y, m=1, d=1):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


def oos_selection(series, group, cut=ts_ms(2025), cost_pct=0.23):
    """Izbor najbolje kombinacije SAMO na podacima pre `cut`, pa rezultat te kombinacije posle `cut` (pravi test van uzorka)."""
    combos = []
    for L in (7, 14, 21, 30):
        for H in (3, 7, 14):
            for k in (3, 5, 8):
                rows, _ = csm_series(series, group, L, H, k, True, cost_pct)
                a, b = metrics(rows, None, cut), metrics(rows, cut, None)
                if a.get("sharpe") is not None and b.get("sharpe") is not None:
                    combos.append((a["sharpe"], b["sharpe"], b.get("t"), L, H, k))
    combos.sort(reverse=True)
    return combos


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "crypto"
    cfg, _ = backtest.load_config()
    series = backtest.build_series(cfg, 1500, with_funding=False, interval="1d", log=lambda *a: None)
    print("instrumenata u grupi %s: %d" % (group, sum(1 for s in series.values() if s.group == group)))
    for cost in (0.23, 0.10, 0.06):
        res = grid(series, group, cost_pct=cost)
        res.sort(key=lambda r: -(r["sharpe"] or -9))
        print("\ntrosak po krugu %.2f%% (%s) | L H k | Sharpe | god. prinos %% | pad %% | po godinama (Sharpe)" % (cost, {0.23: "paper+proklizavanje", 0.10: "pravi taker kripto", 0.06: "maker"}[cost]))
        for r in res[:8]:
            print("  L%2d H%2d k%d | %5.2f | %6.1f | %6.1f | %s" % (r["L"], r["H"], r["k"], r["sharpe"] or 0, r["ann_return_pct"], r["max_dd_pct"],
                                                              {y: v["sharpe"] for y, v in r["by_year"].items()}))
        pos = sum(1 for r in res if (r["sharpe"] or 0) > 0)
        print("  pozitivan Sharpe u %d od %d kombinacija; medijana Sharpe %.2f" % (pos, len(res), st.median([r["sharpe"] or 0 for r in res])))
    print("\nKASNJENJE ULAZA (L14 H7 k5 i L7 H14 k5, trosak 0.23%): Sharpe | t")
    for L, H in ((14, 7), (7, 14)):
        line = []
        for d in (0, 1, 2, 3):
            m = metrics(csm_series(series, group, L, H, 5, True, 0.23, delay=d)[0])
            line.append("+%dd: %.2f | t %.2f" % (d, m["sharpe"], m["t"]))
        print("  L%d H%d: %s" % (L, H, "   ".join(line)))
    print("\nIZBOR PRE 2025, TEST POSLE 2025 (sve 36 kombinacija; Sharpe pre | Sharpe posle | t posle | L H k):")
    c = oos_selection(series, group)
    for a, b, t, L, H, k in c[:5]:
        print("  %5.2f | %5.2f | t %5.2f | L%d H%d k%d" % (a, b, t or 0, L, H, k))
    print("  medijana Sharpe posle 2025 po svim kombinacijama: %.2f; pozitivnih %d/%d; korelacija izbor->test: %.2f" % (
        st.median([x[1] for x in c]), sum(1 for x in c if x[1] > 0), len(c),
        st.correlation([x[0] for x in c], [x[1] for x in c]) if len(c) > 3 else float("nan")))
    print("\nCILJANA VOLATILNOST NA NIVOU KORPE (samo smanjenje, cap 1.0, trosak 0.23%; Sharpe | pad % | god. prinos %; medijana preko 36 kombinacija):")
    allrows = {}
    for L in (7, 14, 21, 30):
        for H in (3, 7, 14):
            for k in (3, 5, 8):
                allrows[(L, H, k)] = csm_series(series, group, L, H, k, True, 0.23)[0]
    for target in (None, 25.0, 20.0, 15.0):
        ms = [metrics(r if target is None else vol_managed(r, target)) for r in allrows.values()]
        ms = [m for m in ms if m.get("sharpe") is not None]
        print("  cilj %s: Sharpe %.2f | pad %.1f | prinos %.1f | pozitivnih %d/%d" % (
            "bez" if target is None else "%.0f%%" % target, st.median([m["sharpe"] for m in ms]), st.median([m["max_dd_pct"] for m in ms]),
            st.median([m["ann_return_pct"] for m in ms]), sum(1 for m in ms if m["sharpe"] > 0), len(ms)))
    for key in ((7, 14, 5), (14, 7, 5)):
        a, b = metrics(allrows[key]), metrics(vol_managed(allrows[key], 20.0))
        print("  L%d H%d k%d: bez %s -> cilj 20%% %s" % (key + ({k: a[k] for k in ("sharpe", "max_dd_pct")}, {k: b[k] for k in ("sharpe", "max_dd_pct")})))
        print("     po godinama (cilj 20%%): %s" % {y: v["sharpe"] for y, v in b["by_year"].items()})
    for L, H in ((14, 7), (7, 14)):
        last = metrics(csm_series(series, group, L, H, 5, True, 0.23)[0], ts_ms(2026))
        print("  L%d H%d k5 samo 2026: Sharpe %s, t %s, prinos %s%% god., dana %s" % (L, H, last.get("sharpe"), last.get("t"), last.get("ann_return_pct"), last.get("n_days")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
