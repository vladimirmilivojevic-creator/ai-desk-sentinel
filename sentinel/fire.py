"""Okidanje mozga POSLE objave dogadjaja na main (poziva se iz workflow-a kao poseban korak).
Cita pending_fire.json iz stanja, salje POST na /fire (samo ID-jevi i sha12), brise fajl kad uspe.
Najvise 3 pokusaja kroz uzastopne krugove; ako je red stariji od 30 min, odbacuje se (dogadjaj je zastareo).
Nikad ne pada workflow zbog neuspeha okidanja."""
import argparse
import os
import sys
import time

from . import notify
from .util import iso, parse_iso, read_json, write_json

MAX_ATTEMPTS, MAX_AGE_MIN = 3, 30


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="_state")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    path = os.path.join(a.state, "pending_fire.json")
    pend = read_json(path)
    if not pend:
        print("nema reda za okidanje")
        return 0
    now = time.time()
    age = (now - parse_iso(pend["created"])) / 60.0
    if age > MAX_AGE_MIN:
        print("red za okidanje je star %.0f min, odbacujem" % age)
        write_json(os.path.join(a.state, "fire_dropped.json"), {"ts": iso(now), "why": "star", "payload": pend["payload"]})
        os.remove(path)
        return 0
    ok, info = notify.fire_brain(pend["payload"], dry=a.dry)
    print("okidanje:", info)
    if ok:
        write_json(os.path.join(a.state, "last_fire.json"), {"ts": iso(now), "payload": pend["payload"]})
        os.remove(path)
        return 0
    pend["attempts"] = pend.get("attempts", 0) + 1
    if pend["attempts"] >= MAX_ATTEMPTS:
        write_json(os.path.join(a.state, "fire_dropped.json"), {"ts": iso(now), "why": info, "payload": pend["payload"]})
        os.remove(path)
        notify.telegram("Straza: okidanje mozga nije uspelo %d puta (%s)." % (MAX_ATTEMPTS, info), dry=a.dry)
    else:
        write_json(path, pend)
    return 0


if __name__ == "__main__":
    sys.exit(main())
