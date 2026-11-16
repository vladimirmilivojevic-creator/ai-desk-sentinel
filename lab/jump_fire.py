"""Okidanje rutine skokova (ai-desk routines/jump.md) POSLE objave stanja na granu state: tako rutina zatekne dogadjaj u jumps/events.json.
Cita <state>/jumps/pending_fire.json koji je u ISTOM krugu napisao lab/jumps.py, salje POST na JUMP_FIRE_URL (samo ID-jevi dogadjaja).
Red stariji od 10 min se ne salje (ostatak iz ranijeg kruga). Bez tajni ne radi nista. Nikad ne pada workflow. Upotreba: python -m lab.jump_fire --state _state [--dry]"""
import json
import os
import sys
import time

MAX_AGE_MIN = 10


def run(state_dir, now_ms=None, dry=False, fire=None):
    path = os.path.join(state_dir, "jumps", "pending_fire.json")
    try:
        with open(path, encoding="utf-8") as f:
            pend = json.load(f)
    except (OSError, ValueError):
        return {"fired": False, "why": "nema reda"}
    now_ms = now_ms or int(time.time() * 1000)
    age = (now_ms - int(pend.get("created_ms", 0))) / 60000.0
    if age > MAX_AGE_MIN or age < -1:
        return {"fired": False, "why": "red je star %.0f min" % age}
    ids = [str(x) for x in (pend.get("payload") or {}).get("ids", [])][:5]
    if not ids:
        return {"fired": False, "why": "prazan red"}
    if fire is None:
        from sentinel import notify
        fire = lambda payload: notify.fire_brain(payload, dry=dry, url_env="JUMP_FIRE_URL", token_env="JUMP_FIRE_TOKEN")  # noqa: E731
    ok, info = fire({"kind": "jump", "ids": ids})
    return {"fired": bool(ok), "why": info, "ids": ids}


def main(argv=None):
    argv = argv or sys.argv[1:]
    state = argv[argv.index("--state") + 1] if "--state" in argv else "_state"
    try:
        res = run(state, dry="--dry" in argv)
    except Exception as e:  # noqa: BLE001
        res = {"fired": False, "why": "greska: %s" % type(e).__name__}
    print("okidanje skoka:", json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
