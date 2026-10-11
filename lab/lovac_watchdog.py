"""Cuvar Lovca.

GitHub zakazane pokrete kasni i ponekad preskace (2026-10-11: dnevni krug od 00:40 UTC krenuo je u 06:25, nedeljna studija od 03:30 u 10:14).
Cuvar se poziva u svakom krugu strazara (na oko 5 min) i, ako je radar stariji od 25 h ili nedeljna studija starija od 8 dana,
rucno pokrece discovery.yml. Koristi samo ugradjeni GITHUB_TOKEN (actions: write), bez tajni, bez AI-ja, ne trguje.

Zastita od petlje: ne pokrece dok neki krug Lovca radi ili ceka, najvise jednom u 90 min, i nikad posle 3 uzastopna pada
(pad zahteva coveka, ne beskonacno ponavljanje).

Upotreba: python -m lab.lovac_watchdog
"""
import datetime as dt
import json
import os
import sys
import urllib.request

ACTIVE = {"queued", "in_progress", "waiting", "requested", "pending"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse(ts):
    if not ts:
        return None
    try:
        t = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def decide(now, radar_utc, study_utc, runs, daily_h=25, weekly_days=8, gap_min=90, max_fail=3):
    """'daily', 'weekly' ili None. runs: poslednji krugovi discovery.yml, najnoviji prvi ({status, conclusion, created_at})."""
    if any(r.get("status") in ACTIVE for r in runs):
        return None
    last = parse(runs[0].get("created_at")) if runs else None
    if last is not None and now - last < dt.timedelta(minutes=gap_min):
        return None
    fails = 0
    for r in runs:
        if r.get("conclusion") != "failure":
            break
        fails += 1
    if fails >= max_fail:
        return None
    study, radar = parse(study_utc), parse(radar_utc)
    if study is None or now - study > dt.timedelta(days=weekly_days):
        return "weekly"
    if radar is None or now - radar > dt.timedelta(hours=daily_h):
        return "daily"
    return None


def _generated(path):
    try:
        with open(os.path.join(ROOT, *path.split("/")), encoding="utf-8") as f:
            return json.load(f).get("generated_utc")
    except (OSError, ValueError):
        return None


def _api(repo, token, path, method="GET", body=None):
    req = urllib.request.Request(
        "https://api.github.com/repos/%s/%s" % (repo, path), method=method,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "User-Agent": "sentinel-lovac-watchdog",
                 "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
    return json.loads(raw) if raw else {}


def main():
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        print("cuvar Lovca: nema GITHUB_REPOSITORY/GITHUB_TOKEN, preskacem")
        return 0
    try:
        runs = _api(repo, token, "actions/workflows/discovery.yml/runs?per_page=5").get("workflow_runs", [])
        mode = decide(dt.datetime.now(dt.timezone.utc), _generated("discovery/radar.json"), _generated("calibration/discovery.json"), runs)
        if mode is None:
            print("cuvar Lovca: u redu")
            return 0
        _api(repo, token, "actions/workflows/discovery.yml/dispatches", "POST", {"ref": "main", "inputs": {"mode": mode}})
        print("cuvar Lovca: pokrenut krug (%s), jer je zakazani kasnio ili ga nije bilo" % mode)
    except Exception as e:  # noqa: BLE001  cuvar nikad ne sme da obori strazu
        print("cuvar Lovca: greska (%s): %s" % (type(e).__name__, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
