"""Uvoz predloga ideja (desk/explorer/candidates.json iz ai-desk, koje pise desk-learn) u config/lab_candidates.json.
Predlog je SAMO podatak: porodica (poznata) i parametri (brojevi, logicke vrednosti ili kratki stringovi, samo imena koja ta porodica prihvata).
Nista iz teksta predloga se ne izvrsava. Posle uvoza pokrece se istorijska provera (python -m lab.backtest) pre bilo kakvog zivog koriscenja.
Upotreba: python -m lab.candidates_import <candidates.json> [--apply]"""
import inspect
import json
import os
import sys

from . import rules

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "config", "lab_candidates.json")
MAX_CANDIDATES = 40


def validate(c):
    """Vraca (ok, razlog)."""
    if not isinstance(c, dict):
        return False, "nije objekat"
    fam, params = c.get("family"), c.get("params", {})
    if fam is None:
        return False, "porodica null (traži novu porodicu: odluka čoveka)"
    if fam not in rules.FAMILIES or fam == "RAND":
        return False, "nepoznata porodica %r" % fam
    if not isinstance(params, dict):
        return False, "params nije objekat"
    allowed = set(inspect.signature(rules.FAMILIES[fam]).parameters) - {"S", "i", "ctx"}
    for k, v in params.items():
        if k not in allowed:
            return False, "parametar %r ne postoji u porodici %s" % (k, fam)
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            if not (-1e6 < v < 1e6):
                return False, "parametar %r van opsega" % k
            continue
        if isinstance(v, str) and len(v) <= 20 and v.replace("_", "").isalnum():
            continue
        return False, "parametar %r ima nedozvoljen tip" % k
    return True, ""


def merge(existing, proposals):
    """Dodaje samo valjane i nove; vraca (lista, prihvaceno, odbaceno[(razlog)])."""
    out = list(existing)
    seen = {(x["family"], json.dumps(x["params"], sort_keys=True)) for x in out}
    ok_n, bad = 0, []
    for c in proposals:
        good, why = validate(c)
        if not good:
            bad.append(why)
            continue
        key = (c["family"], json.dumps(c.get("params", {}), sort_keys=True))
        if key in seen:
            bad.append("već postoji")
            continue
        if len(out) >= MAX_CANDIDATES:
            bad.append("dostignut najveći broj kandidata (%d)" % MAX_CANDIDATES)
            continue
        seen.add(key)
        out.append({"family": c["family"], "params": c.get("params", {}), "source": str(c.get("source_url", ""))[:200],
                    "rationale": str(c.get("rationale", ""))[:300], "added": str(c.get("date", ""))[:10]})
        ok_n += 1
    return out, ok_n, bad


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        proposals = json.load(f)
    if isinstance(proposals, dict):
        proposals = proposals.get("candidates", [])
    existing = []
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            existing = json.load(f).get("candidates", [])
    merged, n, bad = merge(existing, proposals)
    print("prihvaćeno %d, odbačeno %d" % (n, len(bad)))
    for b in bad:
        print(" -", b)
    if "--apply" in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump({"candidates": merged}, f, ensure_ascii=False, indent=1)
        print("upisano u", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
