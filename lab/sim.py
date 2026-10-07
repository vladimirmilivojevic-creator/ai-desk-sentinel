"""Simulacija ishoda: fiksni horizont i 'izvrsna' varijanta (stop 2,5 x ATR, cilj 2 x stop, vremenski stop). Neto posle troska."""
COST_PCT = 0.23  # 0,19% provizije po krugu (izmereno na Liquid-u) + 0,04% proklizavanja

CLASS_BOUNDS = {"crypto": (1.2, 3.5), "oil": (1.2, 3.0), "metal": (0.8, 2.5), "index": (0.7, 1.8),
                "stock": (1.0, 3.0), "gas": (1.5, 4.0)}
ATR_MULT = 2.5
TP_MULT = 2.0


def sign(side):
    return 1.0 if side == "long" else -1.0


def fixed_return(S, i, side, H, cost=COST_PCT):
    if i + H >= S.n:
        return None
    return sign(side) * (S.c[i + H] / S.c[i] - 1.0) * 100.0 - cost


def stop_pct_for(S, i, cls):
    a = S.atr_pct[i]
    if a is None:
        return None
    lo, hi = CLASS_BOUNDS.get(cls, (1.2, 3.5))
    return round(min(max(ATR_MULT * a * 100.0, lo), hi), 2)


def stop_return(S, i, side, stop_pct, H=24, cost=COST_PCT, tp_mult=None):
    """Ulaz po zatvaranju svece i; stop ima prednost ako oba nivoa padnu u istoj sveci (konzervativno)."""
    tp_mult = TP_MULT if tp_mult is None else tp_mult
    if i + H >= S.n or stop_pct is None:
        return None
    e = S.c[i]
    s, t = stop_pct / 100.0, stop_pct * tp_mult / 100.0
    stop = e * (1 - s) if side == "long" else e * (1 + s)
    tp = e * (1 + t) if side == "long" else e * (1 - t)
    for k in range(i + 1, i + H + 1):
        hi, lo = S.h[k], S.l[k]
        if side == "long":
            if lo <= stop:
                return -stop_pct - cost
            if hi >= tp:
                return stop_pct * tp_mult - cost
        else:
            if hi >= stop:
                return -stop_pct - cost
            if lo <= tp:
                return stop_pct * tp_mult - cost
    return sign(side) * (S.c[i + H] / e - 1.0) * 100.0 - cost
