"""Istorijska presuda za uvezene predloge AI-ja: spaja rezultat istorijske provere (lab.backtest, 200 dana, svi instrumenti, trosak uracunat)
sa presudama uvoza (calibration/ideas_status.json). Glavni test je E24: prinos PREKO korpe iste grupe posle 24 h (uklanja smer trzista).
Presuda: 'nagovestaj' samo ako je E24 pozitivan, t >= 2 i pozitivan u oba dela vremena; inace 'palo na istoriji'. Nista odavde ne ide u trgovanje:
ideja sa nagovestajem se i dalje samo meri unapred. Cista funkcija (bez mreze).
Upotreba: python -m lab.ideas_verdict <ideas_status.json> <backtest.json>      -> dopisuje `history` uz svaku uvezenu ideju
          python -m lab.ideas_verdict <ideas_status.json> --need               -> stampa 'yes' ako neka uvezena ideja jos nema istorijsku presudu"""
import json
import sys

PRIMARY = "E24"
T_MIN = 2.0
N_MIN = 100


def need(status):
    return any(r.get("status") == "u laboratoriji" and not r.get("history") for r in status.get("ideas", []))


def verdict_of(rows):
    """rows: redovi istorijske provere za JEDNU varijantu (po testu). -> recnik za polje `history`."""
    by = {r.get("test"): r for r in rows}
    r = by.get(PRIMARY)
    if not r:
        return {"verdict": "nema istorijskog testa %s" % PRIMARY}
    s = r.get("stats") or {}
    t, tt, te = (s.get("all") or {}).get("t"), (s.get("train") or {}).get("t"), (s.get("test") or {}).get("t")
    n, mean = s.get("n", 0), s.get("mean")
    out = {"test": PRIMARY, "n": n, "mean_pct": mean, "t": t, "t_train": tt, "t_test": te}
    if n < N_MIN:
        out["verdict"] = "premalo signala na istoriji (n < %d)" % N_MIN
    elif mean is not None and mean > 0 and t is not None and t >= T_MIN and (tt or 0) > 0 and (te or 0) > 0:
        out["verdict"] = "nagovestaj (pozitivno preko korpe, t >= %g, oba dela vremena): i dalje samo merenje unapred" % T_MIN
    else:
        out["verdict"] = "palo na istoriji (preko korpe posle troska nije pozitivno sa t >= %g u oba dela vremena)" % T_MIN
    return out


def merge(status, backtest):
    """Dopisuje `history` uz uvezene ideje ciji id postoji u istorijskoj proveri. Vraca broj dopisanih."""
    rows = {}
    for r in backtest.get("results", []):
        rows.setdefault(r.get("id"), []).append(r)
    n = 0
    for idea in status.get("ideas", []):
        if idea.get("status") != "u laboratoriji" or idea.get("variant") not in rows:
            continue
        idea["history"] = dict(verdict_of(rows[idea["variant"]]), generated_utc=backtest.get("generated_utc"), k_tests=backtest.get("k_tests"))
        n += 1
    status["history_note"] = ("Istorijska provera: %s dana, trosak %s%% po krugu, %s testova u istom pokretanju (prag za tvrdnju uz toliko testova je z oko %s, "
                              "pa je 'nagovestaj' samo razlog da se ideja prati, ne dokaz)." % (backtest.get("days"), backtest.get("cost_pct"), backtest.get("k_tests"), backtest.get("bonferroni_z")))
    return n


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        print(__doc__)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        status = json.load(f)
    if argv[1] == "--need":
        print("yes" if need(status) else "no")
        return 0
    with open(argv[1], encoding="utf-8") as f:
        bt = json.load(f)
    n = merge(status, bt)
    with open(argv[0], "w", encoding="utf-8", newline="\n") as f:
        json.dump(status, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("istorijska presuda dopisana za %d ideja" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
