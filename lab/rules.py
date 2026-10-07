"""Biblioteka pravila. Svako pravilo je cista funkcija (serija, indeks svece, kontekst) -> 'long' | 'short' | None.
Signal se racuna iz podataka do ZATVARANJA svece i (indeks i), ulaz je po toj ceni (nema gledanja unapred).
Pravila su parametrizovana i imaju stabilan id. Novi kandidati (npr. iz nedeljnog pregleda interneta) dodaju se
u config/lab_candidates.json kao {family, params, source, rationale}: nikad kao kod."""

import hashlib

FAMILIES = {}


def family(name):
    def deco(fn):
        FAMILIES[name] = fn
        return fn
    return deco


def _side(x):
    return "long" if x > 0 else "short"


def _flip(side):
    return "short" if side == "long" else "long"


@family("MOM")
def mom(S, i, ctx, L=4, z=2.0, fade=False):
    zz = S.z(i, L)
    if zz is None or abs(zz) < z:
        return None
    s = _side(zz)
    return _flip(s) if fade else s


@family("RSIX")
def rsix(S, i, ctx, hi=75, lo=25, fade=True, p=14):
    r = S.rsi_by[p][i]
    if r is None:
        return None
    s = "short" if r >= hi else ("long" if r <= lo else None)
    if s is None:
        return None
    return s if fade else _flip(s)


@family("TREND")
def trend(S, i, ctx, mode="pullback"):
    e20, e50, e200, a, c, r = S.ema20[i], S.ema50[i], S.ema200[i], S.atr[i], S.c[i], S.rsi[i]
    if a is None or r is None or i < 200:
        return None
    if mode == "pullback":
        near = abs(c - e20) <= 0.6 * a
        if e20 > e50 > e200 and c >= e50 and near and 40 <= r <= 60:
            return "long"
        if e20 < e50 < e200 and c <= e50 and near and 40 <= r <= 60:
            return "short"
    elif mode == "cross":
        up = S.c[i - 1] <= S.ema50[i - 1] and c > e50 and e50 > e200
        dn = S.c[i - 1] >= S.ema50[i - 1] and c < e50 and e50 < e200
        return "long" if up else ("short" if dn else None)
    return None


@family("DON")
def donchian(S, i, ctx, N=72, fade=False):
    hi, lo = S.hi[N][i], S.lo[N][i]
    if hi is None or lo is None:
        return None
    s = "long" if S.c[i] > hi else ("short" if S.c[i] < lo else None)
    if s is None:
        return None
    return _flip(s) if fade else s


@family("BB")
def bollinger(S, i, ctx, k=2.0, fade=True):
    m, sd = S.bb_m[i], S.bb_s[i]
    if m is None or not sd:
        return None
    s = "short" if S.c[i] > m + k * sd else ("long" if S.c[i] < m - k * sd else None)
    if s is None:
        return None
    return s if fade else _flip(s)


@family("SQZ")
def squeeze(S, i, ctx, pct=0.2, N=24):
    if i < 168:
        return None
    w = [x for x in S.atr_pct[i - 167:i + 1] if x is not None]
    hi, lo = S.hi[N][i], S.lo[N][i]
    if len(w) < 168 or hi is None or S.atr_pct[i] is None:
        return None
    p = sum(1 for x in w if x <= S.atr_pct[i]) / 168.0
    if p > pct:
        return None
    return "long" if S.c[i] > hi else ("short" if S.c[i] < lo else None)


@family("CSM")
def cross_sectional(S, i, ctx, L=24, k=2, momentum=False):
    """Poredak unutar grupe (kripto, makro, akcije) po prinosu za L sati: k najslabijih = long, k najjacih = short
    (obrnuto za momentum)."""
    row = ctx.get("csm", {}).get((S.group, L), {}).get(S.t[i])
    if not row or S.sym not in row:
        return None
    rank, n = row[S.sym]
    if n < 2 * k + 1:
        return None
    s = "long" if rank < k else ("short" if rank >= n - k else None)
    if s is None:
        return None
    return _flip(s) if momentum else s


@family("BTCLEAD")
def btc_lead(S, i, ctx, z=2.0):
    if S.sym == "BTC" or S.group != "crypto":
        return None
    B = ctx.get("btc")
    if B is None:
        return None
    j = ctx["btc_index"].get(S.t[i])
    if j is None:
        return None
    zb, zs = B.z(j, 1), S.z(i, 1)
    if zb is None or zs is None or abs(zb) < z or abs(zs) >= 0.5:
        return None
    return _side(zb)


@family("RAND")
def placebo(S, i, ctx, p=0.02, seed=7):
    """Placebo: nasumican ulaz (determinist: iz hesa instrumenta i vremena) sa verovatnocom p po svecici. Nema nikakvu prednost,
    pa pokazuje sta bi 'pravilo bez znanja' dalo posle troska: svako pravilo treba da pobedi OVO, ne nulu."""
    d = hashlib.md5(("%s|%d|%d" % (S.sym, S.t[i], seed)).encode()).digest()
    if int.from_bytes(d[:4], "big") / 4294967296.0 >= p:
        return None
    return "long" if (d[4] & 1) else "short"


@family("FUND")
def funding_extreme(S, i, ctx, thr=0.00004):
    f = S.fund(i)
    if f is None:
        return None
    return "short" if f >= thr else ("long" if f <= -thr else None)


def default_variants():
    v = []
    for L in (1, 4, 24):
        for z in (1.5, 2.5):
            v.append(("MOM_L%d_z%.1f" % (L, z), "MOM", dict(L=L, z=z, fade=False)))
            v.append(("FADE_L%d_z%.1f" % (L, z), "MOM", dict(L=L, z=z, fade=True)))
    for hi, lo in ((75, 25), (80, 20)):
        v.append(("RSIFADE_%d" % hi, "RSIX", dict(hi=hi, lo=lo, fade=True)))
        v.append(("RSIFOLLOW_%d" % hi, "RSIX", dict(hi=hi, lo=lo, fade=False)))
    v.append(("TREND_pullback", "TREND", dict(mode="pullback")))
    v.append(("TREND_cross", "TREND", dict(mode="cross")))
    for N in (24, 72, 168):
        v.append(("DON_follow_%d" % N, "DON", dict(N=N, fade=False)))
        v.append(("DON_fade_%d" % N, "DON", dict(N=N, fade=True)))
    v.append(("BB_fade", "BB", dict(k=2.0, fade=True)))
    v.append(("BB_follow", "BB", dict(k=2.0, fade=False)))
    v.append(("SQZ_break", "SQZ", dict(pct=0.2, N=24)))
    for L in (4, 24):
        v.append(("CSM_rev_L%d" % L, "CSM", dict(L=L, k=2, momentum=False)))
        v.append(("CSM_mom_L%d" % L, "CSM", dict(L=L, k=2, momentum=True)))
    for z in (2.0, 3.0):
        v.append(("BTCLEAD_z%.1f" % z, "BTCLEAD", dict(z=z)))
    for thr in (0.00004, 0.00008):
        v.append(("FUND_x%g" % (thr * 100), "FUND", dict(thr=thr)))
    v.append(("PLACEBO_p2", "RAND", dict(p=0.02, seed=7)))
    return v


def daily_variants():
    """Pravila za DNEVNE svece (horizont u danima): trend i obrtanje na vise dana, gde je trosak mali u odnosu na pomak."""
    v = []
    for L in (7, 14, 21, 30, 60, 90):
        for z in (0.5, 1.0):
            v.append(("D_MOM_L%d_z%.1f" % (L, z), "MOM", dict(L=L, z=z, fade=False)))
    for L in (1, 3):
        v.append(("D_FADE_L%d_z1.0" % L, "MOM", dict(L=L, z=1.0, fade=True)))
    v.append(("D_RSI2_fade_90", "RSIX", dict(hi=90, lo=10, fade=True, p=2)))
    v.append(("D_RSI2_fade_95", "RSIX", dict(hi=95, lo=5, fade=True, p=2)))
    v.append(("D_RSI14_fade_70", "RSIX", dict(hi=70, lo=30, fade=True)))
    for N in (20, 55, 100):
        v.append(("D_DON_follow_%d" % N, "DON", dict(N=N, fade=False)))
        v.append(("D_DON_fade_%d" % N, "DON", dict(N=N, fade=True)))
    v.append(("D_TREND_cross", "TREND", dict(mode="cross")))
    for L in (7, 14, 30):
        v.append(("D_CSM_mom_L%d" % L, "CSM", dict(L=L, k=2, momentum=True)))
        v.append(("D_CSM_rev_L%d" % L, "CSM", dict(L=L, k=2, momentum=False)))
    v.append(("D_BB_fade", "BB", dict(k=2.0, fade=True)))
    v.append(("D_PLACEBO_p5", "RAND", dict(p=0.05, seed=11)))
    return v


def candidate_variants(candidates):
    """Kandidati su samo parametri poznatih porodica (nikad izvrsni kod); nepoznato se preskace."""
    out = []
    for c in candidates or []:
        fam, params = c.get("family"), c.get("params", {})
        if fam not in FAMILIES or not isinstance(params, dict):
            continue
        clean = {k: v for k, v in params.items() if isinstance(v, (int, float, bool, str))}
        vid = "CAND_%s_%s" % (fam, "_".join("%s%s" % (k, clean[k]) for k in sorted(clean)))
        out.append((vid, fam, clean))
    return out


def csm_context(series_by_sym, Ls=(4, 24, 7, 14, 30)):
    """Unapred izracunat poredak po grupi i vremenu: {(grupa, L): {t: {sym: (rang od najslabijeg, n)}}}."""
    groups = {}
    for s in series_by_sym.values():
        groups.setdefault(s.group, []).append(s)
    out = {}
    for g, members in groups.items():
        idx = [{t: i for i, t in enumerate(m.t)} for m in members]
        all_t = sorted(set(t for m in members for t in m.t))
        for L in Ls:
            table = {}
            for t in all_t:
                vals = []
                for m, ix in zip(members, idx):
                    i = ix.get(t)
                    if i is None:
                        continue
                    r = m.ret(i, L)
                    if r is not None:
                        vals.append((r, m.sym))
                if len(vals) >= 5:
                    vals.sort()
                    table[t] = {sym: (rank, len(vals)) for rank, (_, sym) in enumerate(vals)}
            out[(g, L)] = table
    return out
