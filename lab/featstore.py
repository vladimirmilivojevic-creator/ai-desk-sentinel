"""Skladiste osobina (feature store): SVI brojevi iz data lake-a u jednom ravnom recniku {ime: broj}, sa grupom i opisom na srpskom.
Isti recnik ide u satnu istoriju (z-skorovi), u data/features.json (za AI i panel) i u zapis svakog kruga Istrazivaca (ctx), pa se kasnije
statistikom vidi koja osobina zaista zavisi sa ishodom. Nedostupno = ne ulazi (nikad izmisljeno). Samo stdlib."""
import re
import statistics as st

GROUPS = {"time": "Vreme", "cal": "Kalendar", "hl": "Hyperliquid struktura", "drv": "Derivati", "mac": "Makro", "liq": "Likvidnost", "sent": "Raspolozenje",
          "pos": "Pozicioniranje", "act": "Aktivnost mreza", "bn": "Binance derivati", "sm": "Pametan novac", "chain": "On-chain", "news": "Vesti", "trump": "Trump objave"}

DESC = {
    "vix": "VIX: strah na akcijama", "vix3m": "VIX na 3 meseca", "dxy": "Dolar indeks", "hy_oas": "Kreditni raspon rizicnih firmi (HY OAS)", "fear_greed": "Kripto strah/pohlepa 0-100",
    "dvol_btc": "Ocekivana volatilnost BTC iz opcija", "dvol_eth": "Ocekivana volatilnost ETH iz opcija", "put_call_oi": "BTC opcije: put/call odnos", "okx_lsr_btc": "OKX: odnos dugih i kratkih naloga BTC",
    "btc_fund_h": "BTC funding po satu (Hyperliquid)", "eth_fund_h": "ETH funding po satu (Hyperliquid)", "btc_oi_usd": "BTC otvoreni interes na Hyperliquid-u ($)",
    "btc_spread_bps": "BTC spread (bps)", "btc_bin_minus_hl_h": "BTC funding: Binance minus Hyperliquid", "stable_chg_7d": "Ponuda stablecoin-a, promena za 7 d (%)",
    "btc_smart_net_share": "Pametan novac: neto udeo na BTC (-1..+1)", "hl_fund_mean": "Prosecan funding kripto instrumenata (po satu)", "hl_fund_pos_share": "Udeo kripto instrumenata sa pozitivnim fundingom",
    "hl_premium_mean": "Prosecna premija perpetuala prema indeksu", "hl_oi_total_b": "Ukupan otvoreni interes lab kripto instrumenata (mlrd $)",
    "hl_spread_med_bps": "Medijana spreda lab instrumenata (bps)", "hl_imb_btc": "BTC knjiga naloga: neravnoteza kupaca/prodavaca u 1% (-1..+1)", "hl_imb_crypto_mean": "Prosecna neravnoteza knjige kripto instrumenata",
    "cal_hrs_to_high": "Sati do sledece VAZNE objave (99 = nema u 72 h)", "cal_n_high_24h": "Broj vaznih objava u narednih 24 h", "cal_n_med_24h": "Broj srednjih objava u narednih 24 h",
    "earn_n_14d": "Broj nasih akcija sa zaradama u narednih 14 dana", "earn_days_min": "Dana do najblizih zarada nasih akcija",
    "fed_exp_rate": "Kalshi: ocekivana Fed stopa posle sledeceg sastanka", "fed_p_up": "Kalshi: verovatnoca vise stope od najverovatnije", "fed_p_down": "Kalshi: verovatnoca nize stope od najverovatnije",
    "fed_days": "Dana do sledeceg Fed sastanka", "dex_vol_b": "DEX obim 24 h (mlrd $)", "dex_c1": "DEX obim: promena 1 d (%)", "dex_c7": "DEX obim: promena 7 d (%)", "dex_c1m": "DEX obim: promena 1 m (%)",
    "fees_m": "Naknade protokola 24 h (mil $)", "fees_c7": "Naknade: promena 7 d (%)", "fees_c1m": "Naknade: promena 1 m (%)", "hl_dex_vol_m": "Hyperliquid (DefiLlama) obim 24 h (mil $)",
    "f_net_liq_tn": "Neto likvidnost USD (Fed bilans minus TGA minus RRP, bil $)", "t_hour": "Sat u danu (UTC)", "t_dow": "Dan u nedelji (0=nedelja)",
    "bn_glob_ls_med": "Binance: medijana odnosa dugih/kratkih naloga svih kovanica", "bn_oi_chg_7_med": "Binance: medijana promene otvorenog interesa za 7 d (%)",
    "bn_taker_med": "Binance: medijana taker odnosa (kupovina/prodaja)", "bn_glob_ls_hi_share": "Binance: udeo kovanica sa odnosom dugih/kratkih preko 1.5",
    "oc_btc_adr_z": "BTC aktivne adrese (z-skor 30 d)", "oc_btc_tx_z": "BTC transakcije (z-skor 30 d)", "oc_btc_adr_c7": "BTC aktivne adrese: promena 7 d (%)",
}


def ascii_name(s):
    s = str(s).lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "", s)


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v == v and abs(v) != float("inf") else None


def _dig(d, ks):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def flatten(files, core, now_ms):
    """files: {task: {updated_utc, data}}; core: scalars() iz collect.py. Vraca ({ime: broj}, {ime: [grupa, opis]})."""
    f, g = {}, {}

    def put(name, val, group, desc=None):
        v = _num(val)
        if v is None:
            return
        f[name] = round(v, 6) if abs(v) < 1e6 else round(v, 1)
        g[name] = [GROUPS.get(group, group), desc or DESC.get(name) or name]

    data = lambda k: ((files.get(k) or {}).get("data") or {})  # noqa: E731
    for k, v in core.items():
        grp = "mac" if k in ("vix", "vix3m", "dxy", "hy_oas") else ("sm" if "smart" in k else ("sent" if k in ("fear_greed", "stable_chg_7d") else "drv"))
        put(k, v, grp)
    # makro: Yahoo
    for name, rec in (data("macro").get("yahoo") or {}).items():
        if not rec:
            continue
        a = ascii_name(name)
        put("y_" + a, rec.get("last"), "mac", "Yahoo: %s (nivo)" % name)
        for c, lab in (("chg_1d_pct", "c1"), ("chg_5d_pct", "c5"), ("chg_20d_pct", "c20")):
            put("y_%s_%s" % (a, lab), rec.get(c), "mac", "Yahoo: %s, promena %s (%%)" % (name, lab[1:] + " d"))
    # makro: FRED
    fred = data("macro").get("fred") or {}
    for sid, rec in fred.items():
        if not rec:
            continue
        put("f_" + sid.lower(), rec.get("last"), "mac", "FRED %s: %s" % (sid, rec.get("name")))
        put("f_%s_c5" % sid.lower(), rec.get("chg_5"), "mac", "FRED %s: promena 5 posmatranja" % sid)
    try:
        w, t, r = [(fred.get(k) or {}).get("last") for k in ("WALCL", "WTREGEN", "RRPONTSYD")]
        if None not in (w, t, r):
            put("f_net_liq_tn", (w - t) / 1e6 - r / 1e3, "liq", DESC["f_net_liq_tn"])
    except (TypeError, ValueError):
        pass
    # raspolozenje
    sen = data("sentiment")
    put("fg_avg7", _dig(sen, ("fear_greed", "avg7")), "sent", "Kripto strah/pohlepa, prosek 7 d")
    put("fg_avg30", _dig(sen, ("fear_greed", "avg30")), "sent", "Kripto strah/pohlepa, prosek 30 d")
    put("btc_dom", _dig(sen, ("crypto_global", "btc_dominance")), "sent", "BTC dominacija (%)")
    put("mcap_chg_24h", _dig(sen, ("crypto_global", "mcap_chg_24h_pct")), "sent", "Ukupna kripto kapitalizacija, promena 24 h (%)")
    tot = _num(_dig(sen, ("stablecoins", "total_usd")))
    put("stable_total_tn", tot / 1e12 if tot else None, "sent", "Ponuda stablecoin-a (bil $)")
    put("stable_c30", _dig(sen, ("stablecoins", "chg_30d_pct")), "sent", "Ponuda stablecoin-a, promena 30 d (%)")
    for art, rec in (sen.get("wiki_attention") or {}).items():
        if rec:
            put("wiki_%s_z" % ascii_name(art), rec.get("z"), "sent", "Wikipedia pazanja: %s (z-skor)" % art)
    # derivati
    dv = data("derivs")
    put("dvol_btc_c24", _dig(dv, ("deribit", "dvol_btc", "chg_24h")), "drv", "DVOL BTC: promena 24 h")
    put("dvol_eth_c24", _dig(dv, ("deribit", "dvol_eth", "chg_24h")), "drv", "DVOL ETH: promena 24 h")
    for c, rec in (dv.get("okx_lsr") or {}).items():
        if rec:
            put("okx_lsr_%s" % c.lower(), rec.get("last"), "drv", "OKX: odnos dugih/kratkih naloga %s" % c)
            put("okx_lsr_%s_c24" % c.lower(), rec.get("chg_24h"), "drv", "OKX: odnos dugih/kratkih %s, promena 24 h" % c)
    for c, rec in (dv.get("coinalyze") or {}).items():
        if rec and not rec.get("error"):
            for k, lab in (("oi_usd", "otvoreni interes sve berze ($)"), ("funding_mean", "prosecan funding"), ("liq_long_24h", "likvidacije dugih 24 h ($)"),
                           ("liq_short_24h", "likvidacije kratkih 24 h ($)"), ("lsr_last", "odnos dugih/kratkih")):
                put("cz_%s_%s" % (c.lower(), k), rec.get(k), "drv", "Coinalyze %s: %s" % (c, lab))
    fl = data("okx_flow")
    for c, rec in fl.items():
        if rec and not rec.get("error"):
            for k, lab in (("taker_ratio_24h", "taker odnos 24 h (kupovina/prodaja)"), ("taker_ratio_prev24h", "taker odnos prethodnih 24 h"), ("oi_chg_24h_pct", "promena OI 24 h (%)"),
                           ("funding_8h", "funding na 8 h")):
                put("okx_%s_%s" % (c.lower(), k), rec.get(k), "drv", "OKX %s: %s" % (c, lab))
    # Hyperliquid struktura
    mk = data("market")
    crypto = [s for s in mk if not s.startswith("xyz:") and (mk[s] or {}).get("ctx")]
    fund = [mk[s]["ctx"]["funding_h"] for s in crypto if mk[s]["ctx"].get("funding_h") is not None]
    prem = [mk[s]["ctx"]["premium"] for s in crypto if mk[s]["ctx"].get("premium") is not None]
    oi = [mk[s]["ctx"]["oi_usd"] for s in crypto if mk[s]["ctx"].get("oi_usd")]
    spr = [mk[s]["book"]["spread_bps"] for s in crypto if (mk[s].get("book") or {}).get("spread_bps") is not None]
    imb = [mk[s]["book"]["imb_1pct"] for s in crypto if (mk[s].get("book") or {}).get("imb_1pct") is not None]
    if fund:
        put("hl_fund_mean", sum(fund) / len(fund), "hl")
        put("hl_fund_pos_share", sum(1 for x in fund if x > 0) / len(fund), "hl")
    if prem:
        put("hl_premium_mean", sum(prem) / len(prem), "hl")
    if oi:
        put("hl_oi_total_b", sum(oi) / 1e9, "hl")
    if spr:
        put("hl_spread_med_bps", st.median(spr), "hl")
    if imb:
        put("hl_imb_crypto_mean", sum(imb) / len(imb), "hl")
    put("hl_imb_btc", _dig(mk, ("BTC", "book", "imb_1pct")), "hl")
    # pametan novac
    for c in ("ETH", "SOL", "HYPE"):
        put("sm_%s_net_share" % c.lower(), _dig(data("smart_money"), ("coins", c, "net_share")), "sm", "Pametan novac: neto udeo na %s" % c)
    # kalendar
    cal = data("calendar")
    ev = cal.get("events") or []
    now_s = now_ms / 1000.0
    import datetime as _dt

    def tsec(e):
        try:
            return _dt.datetime.fromisoformat(e["ts"].replace("Z", "+00:00")).timestamp()
        except (KeyError, ValueError):
            return None
    highs = [tsec(e) for e in ev if e.get("impact") == "High" and tsec(e) is not None and tsec(e) >= now_s - 1800]
    meds = [tsec(e) for e in ev if e.get("impact") == "Medium" and tsec(e) is not None and tsec(e) >= now_s - 1800]
    put("cal_hrs_to_high", (min(highs) - now_s) / 3600.0 if highs else 99.0, "cal")
    put("cal_n_high_24h", sum(1 for t in highs if t - now_s <= 86400), "cal")
    put("cal_n_med_24h", sum(1 for t in meds if t - now_s <= 86400), "cal")
    er = cal.get("earnings") or {}
    put("earn_n_14d", len(er), "cal")
    days = []
    for rec in er.values():
        try:
            days.append((_dt.date.fromisoformat(rec["date"]) - _dt.datetime.fromtimestamp(now_s, _dt.timezone.utc).date()).days)
        except (KeyError, ValueError, TypeError):
            continue
    put("earn_days_min", min(days) if days else 99, "cal")
    # CFTC
    for k, rec in data("cftc").items():
        if rec:
            put("cftc_%s_net" % k, rec.get("net_pct_oi"), "pos", "CFTC %s: neto spekulanti, %% otvorenog interesa" % k.upper())
            put("cftc_%s_pctl" % k, rec.get("pctl"), "pos", "CFTC %s: percentil u 3 godine (0-100)" % k.upper())
            put("cftc_%s_c1w" % k, rec.get("chg_1w"), "pos", "CFTC %s: promena za nedelju" % k.upper())
    # DefiLlama
    ll = data("llama")
    put("dex_vol_b", (_num(_dig(ll, ("dex", "total24h"))) or 0) / 1e9 or None, "act")
    put("dex_c1", _dig(ll, ("dex", "chg_1d")), "act")
    put("dex_c7", _dig(ll, ("dex", "chg_7d")), "act")
    put("dex_c1m", _dig(ll, ("dex", "chg_1m")), "act")
    put("fees_m", (_num(_dig(ll, ("fees", "total24h"))) or 0) / 1e6 or None, "act")
    put("fees_c7", _dig(ll, ("fees", "chg_7d")), "act")
    put("fees_c1m", _dig(ll, ("fees", "chg_1m")), "act")
    put("hl_dex_vol_m", (_num(_dig(ll, ("dex", "hyperliquid_24h"))) or 0) / 1e6 or None, "act")
    # Kalshi
    kl = data("kalshi")
    put("fed_exp_rate", kl.get("expected_rate"), "mac")
    put("fed_p_up", kl.get("p_up"), "mac")
    put("fed_p_down", kl.get("p_down"), "mac")
    put("fed_days", kl.get("days_to_meeting"), "mac")
    # Binance dnevno
    bn = data("bn_daily")
    for k, v in (bn.get("agg") or {}).items():
        put("bn_" + k, v, "bn", DESC.get("bn_" + k) or "Binance dnevno: %s" % k)
    for c in ("BTC", "ETH"):
        rec = (bn.get("coins") or {}).get(c) or {}
        for k in ("oi_chg_7", "glob_ls", "top_acc_ls", "top_pos_ls", "taker", "glob_ls_z", "top_acc_ls_z"):
            put("bn_%s_%s" % (c.lower(), k), rec.get(k), "bn", "Binance %s: %s" % (c, k))
    # on-chain
    oc = data("onchain")
    put("oc_btc_adr_z", oc.get("btc_adr_z"), "chain")
    put("oc_btc_tx_z", oc.get("btc_tx_z"), "chain")
    put("oc_btc_adr_c7", oc.get("btc_adr_chg_7d_pct"), "chain")
    # vesti
    for q, rec in data("gdelt").items():
        if rec:
            put("gd_%s_tone" % q, rec.get("tone_24h"), "news", "GDELT ton vesti '%s' (negativno = lose vesti)" % q)
            put("gd_%s_tone_chg" % q, rec.get("tone_chg"), "news", "GDELT ton '%s': promena prema prethodnih 6 d" % q)
    # Trump objave (samo brojevi i imena tema; tekst se nigde ne cuva)
    tr = data("trump")
    for k, ds in (("posts_1h", "Trump: broj sopstvenih objava u poslednjih 1 h"), ("posts_4h", "Trump: broj sopstvenih objava u poslednja 4 h"),
                  ("posts_24h", "Trump: broj sopstvenih objava u poslednja 24 h"), ("rt_24h", "Trump: broj repostova u 24 h"), ("shout_24h", "Trump: objave pisane velikim slovima u 24 h"),
                  ("company_24h", "Trump: objave koje pominju neku od nasih kompanija u 24 h"), ("last_age_min", "Trump: minuta od poslednje sopstvene objave")):
        put("tr_" + k, tr.get(k), "trump", ds)
    for t, n in (tr.get("topics_24h") or {}).items():
        put("tr_%s_24h" % t, n, "trump", "Trump: objave o temi '%s' u 24 h" % t)
    for t, n in (tr.get("topics_4h") or {}).items():
        put("tr_%s_4h" % t, n, "trump", "Trump: objave o temi '%s' u 4 h" % t)
    # vreme
    import time as _t
    tm = _t.gmtime(now_s)
    put("t_hour", tm.tm_hour, "time")
    put("t_dow", (tm.tm_wday + 1) % 7, "time")
    return f, g


def instrument_features(market):
    """Osobine po instrumentu iz market.json: {sym: {funding_h, premium, oi_usd, vol24, spread_bps, imb_1pct, bin_minus_hl_h}} (samo dostupno)."""
    out = {}
    for s, row in (market or {}).items():
        c, b, x = (row or {}).get("ctx") or {}, (row or {}).get("book") or {}, (row or {}).get("fund_xv") or {}
        rec = {"funding_h": c.get("funding_h"), "premium": c.get("premium"), "oi_usd": c.get("oi_usd"), "vol24": c.get("vol24"), "spread_bps": b.get("spread_bps"),
               "imb_1pct": b.get("imb_1pct"), "bin_minus_hl_h": x.get("bin_minus_hl_h")}
        rec = {k: v for k, v in rec.items() if v is not None}
        if rec:
            out[s] = rec
    return out
