"""Indikatori nad listama brojeva (stdlib). Nedovoljno istorije = None."""
import math


def ema(vals, n):
    k = 2.0 / (n + 1)
    out, e = [], None
    for x in vals:
        e = x if e is None else x * k + e * (1 - k)
        out.append(e)
    return out


def wilder(vals, n):
    out, a = [], None
    for i, x in enumerate(vals):
        if i < n - 1:
            out.append(None)
        elif i == n - 1:
            a = sum(vals[:n]) / n
            out.append(a)
        else:
            a = (a * (n - 1) + x) / n
            out.append(a)
    return out


def rsi(closes, n=14):
    gains = [0.0] + [max(closes[i] - closes[i - 1], 0.0) for i in range(1, len(closes))]
    losses = [0.0] + [max(closes[i - 1] - closes[i], 0.0) for i in range(1, len(closes))]
    ag, al = wilder(gains, n), wilder(losses, n)
    out = []
    for a, b in zip(ag, al):
        if a is None or b is None:
            out.append(None)
        else:
            out.append(100.0 if b == 0 else 100.0 - 100.0 / (1.0 + a / b))
    return out


def atr(cs, n=14):
    closes = [c["c"] for c in cs]
    tr = [cs[0]["h"] - cs[0]["l"]] + [max(cs[i]["h"] - cs[i]["l"], abs(cs[i]["h"] - closes[i - 1]),
                                         abs(cs[i]["l"] - closes[i - 1])) for i in range(1, len(cs))]
    return wilder(tr, n)


def rolling_mean_std(vals, n):
    m, s = [None] * len(vals), [None] * len(vals)
    for i in range(n - 1, len(vals)):
        w = vals[i - n + 1:i + 1]
        mu = sum(w) / n
        m[i] = mu
        s[i] = math.sqrt(sum((x - mu) ** 2 for x in w) / n)
    return m, s


def rolling_max(vals, n):
    """max prethodnih n vrednosti (bez tekuce): out[i] = max(vals[i-n:i])."""
    out = [None] * len(vals)
    for i in range(n, len(vals)):
        out[i] = max(vals[i - n:i])
    return out


def rolling_min(vals, n):
    out = [None] * len(vals)
    for i in range(n, len(vals)):
        out[i] = min(vals[i - n:i])
    return out


def pct_rank(vals, i, n):
    """percentil vrednosti vals[i] unutar poslednjih n (0..1)."""
    if i < n - 1 or vals[i] is None:
        return None
    w = [x for x in vals[i - n + 1:i + 1] if x is not None]
    if len(w) < n:
        return None
    return sum(1 for x in w if x <= vals[i]) / float(n)


class Series:
    """Predračunati nizovi jednog instrumenta."""

    def __init__(self, cs, funding=None, sym="", group="", cls=""):
        self.sym, self.group, self.cls = sym, group, cls
        self.cs = cs
        self.n = len(cs)
        self.t = [c["t"] for c in cs]
        self.o = [c["o"] for c in cs]
        self.h = [c["h"] for c in cs]
        self.l = [c["l"] for c in cs]
        self.c = [c["c"] for c in cs]
        self.rsi = rsi(self.c)
        self.rsi_by = {14: self.rsi, 2: rsi(self.c, 2), 3: rsi(self.c, 3)}
        self.atr = atr(cs)
        self.ema20, self.ema50, self.ema200 = ema(self.c, 20), ema(self.c, 50), ema(self.c, 200)
        self.bb_m, self.bb_s = rolling_mean_std(self.c, 20)
        self.hi = {n: rolling_max(self.h, n) for n in (20, 24, 55, 72, 100, 168)}
        self.lo = {n: rolling_min(self.l, n) for n in (20, 24, 55, 72, 100, 168)}
        self.atr_pct = [None if a is None else a / x for a, x in zip(self.atr, self.c)]
        self.funding = {}
        if funding:
            # fonding po satu, poravnat na pocetak sata
            for f in funding:
                self.funding[(f["t"] // 3600000) * 3600000] = f["rate"]

    def ret(self, i, L):
        if i - L < 0:
            return None
        return self.c[i] / self.c[i - L] - 1.0

    def z(self, i, L):
        """pomak za L sati u jedinicama ocekivane varijacije (ATR% * sqrt(L))."""
        r = self.ret(i, L)
        a = self.atr_pct[i]
        if r is None or a is None or a <= 0:
            return None
        return r / (a * math.sqrt(L))

    def fund(self, i):
        return self.funding.get((self.t[i] // 3600000) * 3600000)
