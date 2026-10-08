"""Panel podataka (instrument x sat) za model "motor za poene": svaki sat se trajno upisuje sve sto sistem zna (globalne osobine + osobine po instrumentu + cene),
a ishod (prinos posle 1/4/24 h) se racuna iz cena kad stignu, bez posebnog koraka. Iz toga se kasnije uci sta zaista zavisi sa ishodom.

Fajlovi (<state>/data/): panel_global.jsonl  {"t": sat_ms, "f": {osobina: broj}, "m": {instrument: cena}}
                         panel_inst.jsonl    {"t": sat_ms, "i": {instrument: {osobina: broj}}}
Cuva poslednjih KEEP_DAYS dana. Upis je idempotentan po satu. Samo stdlib."""
import json
import os

HOUR = 3600 * 1000
KEEP_DAYS = 60
HORIZONS = (1, 4, 24)
G_FILE, I_FILE = "panel_global.jsonl", "panel_inst.jsonl"


def _read(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except ValueError:
                        continue
    return rows


def _write(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.replace(tmp, path)


def _merge(rows, new, keep_from):
    by_t = {r["t"]: r for r in rows}
    for r in new:
        by_t[r["t"]] = r  # novi upis za isti sat zamenjuje stari
    return [by_t[t] for t in sorted(by_t) if t >= keep_from]


def seed(state_dir):
    """Prvi put: iz satne istorije (data/history.json: osobine + cene) i lab/features.jsonl (cena, funding, OI, premija, obim po instrumentu) napravi pocetne redove."""
    data = os.path.join(state_dir, "data")
    g_path, i_path = os.path.join(data, G_FILE), os.path.join(data, I_FILE)
    g_new, i_new = [], []
    if not os.path.exists(g_path):
        hist = []
        try:
            with open(os.path.join(data, "history.json"), encoding="utf-8") as f:
                hist = json.load(f)
        except (OSError, ValueError):
            pass
        for h in hist:
            if h.get("m") and h.get("t") and h["t"] % HOUR == 0:
                g_new.append({"t": h["t"], "f": {k: v for k, v in h.items() if k not in ("t", "m")}, "m": h["m"]})
    if not os.path.exists(i_path):
        for r in _read(os.path.join(state_dir, "lab", "features.jsonl")):
            inst = {}
            for sym, v in (r.get("f") or {}).items():
                if isinstance(v, list) and len(v) >= 5:
                    rec = {k: x for k, x in zip(("funding_h", "oi_usd", "premium", "vol24"), (v[1], v[2], v[3], v[4])) if x is not None}
                    if rec:
                        inst[sym] = rec
            if inst and r.get("t") and r["t"] % HOUR == 0:
                i_new.append({"t": r["t"], "i": inst})
    return g_new, i_new


def append_hour(state_dir, t_ms, feats, inst, marks):
    """Upisi sat t_ms (poceo sata). feats {ime: broj}, inst {instrument: {osobina: broj}}, marks {instrument: cena}. Vraca (n_global, n_inst)."""
    data = os.path.join(state_dir, "data")
    os.makedirs(data, exist_ok=True)
    g_path, i_path = os.path.join(data, G_FILE), os.path.join(data, I_FILE)
    g_seed, i_seed = seed(state_dir)
    keep_from = t_ms - KEEP_DAYS * 24 * HOUR
    g_rows = _merge(_read(g_path), g_seed + [{"t": t_ms, "f": feats, "m": marks}], keep_from)
    i_rows = _merge(_read(i_path), i_seed + [{"t": t_ms, "i": inst}], keep_from)
    _write(g_path, g_rows)
    _write(i_path, i_rows)
    return len(g_rows), len(i_rows)


def load(state_dir):
    data = os.path.join(state_dir, "data")
    return _read(os.path.join(data, G_FILE)), _read(os.path.join(data, I_FILE))


def price_index(g_rows):
    """{t: {instrument: cena}}"""
    return {r["t"]: r.get("m") or {} for r in g_rows}


def dataset(g_rows, i_rows, horizons=HORIZONS, past=(1, 4, 24)):
    """Redovi (t, instrument): x = osobine instrumenta + prosli prinosi (r1, r4, r24, u %), y<h> = prinos posle h sati (u %), yx<h> = isti prinos minus prosek svih
    instrumenata tog sata (uklanja zajednicko kretanje trzista). Redovi bez ijednog ishoda se izostavljaju (jos nisu stigli)."""
    px = price_index(g_rows)
    inst_by_t = {r["t"]: r.get("i") or {} for r in i_rows}
    out = []
    for t in sorted(px):
        m0 = px[t]
        ys = {}
        for h in horizons:
            m1 = px.get(t + h * HOUR)
            if not m1:
                continue
            ys[h] = {s: (m1[s] / p - 1.0) * 100.0 for s, p in m0.items() if p and m1.get(s)}
        if not ys:
            continue
        means = {h: (sum(v.values()) / len(v) if v else None) for h, v in ys.items()}
        for s in m0:
            row = {"t": t, "sym": s, "x": dict(inst_by_t.get(t, {}).get(s, {}))}
            for k in past:
                mp = px.get(t - k * HOUR)
                if mp and mp.get(s) and m0.get(s):
                    row["x"]["r%d" % k] = (m0[s] / mp[s] - 1.0) * 100.0
            has = False
            for h, v in ys.items():
                if s in v:
                    row["y%d" % h] = v[s]
                    row["yx%d" % h] = v[s] - means[h]
                    has = True
            if has:
                out.append(row)
    return out
