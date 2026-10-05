"""Zajednicke pomocne funkcije. Samo standardna biblioteka."""
import datetime as dt
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

UA = "ai-desk-sentinel/0.1 (public research bot, no trading)"
BROWSER_UA = "Mozilla/5.0 (compatible; ai-desk-sentinel/0.1)"


class SourceError(Exception):
    """Greska izvora. Poruka nikad ne sadrzi URL (tokeni bi mogli da procure u log)."""

    def __init__(self, msg, rate_limited=False):
        super().__init__(msg)
        self.rate_limited = rate_limited


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def iso(ts):
    if isinstance(ts, (int, float)):
        ts = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()


def http(method, url, body=None, headers=None, timeout=10, retries=2, ua=UA):
    h = {"User-Agent": ua}
    h.update(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    last = SourceError("unknown")
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=h, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            last = SourceError("HTTP %s" % e.code, rate_limited=(e.code == 429))
            if e.code < 500:
                break  # 4xx i 429: bez ponovnog pokusaja
        except Exception as e:  # mrezna greska, timeout
            last = SourceError(type(e).__name__)
        if i + 1 < retries:
            time.sleep(1 + i)
    raise last


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def canon(obj):
    """Deterministicki bajtovi: iste vrednosti uvek daju isti sha12."""
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode()


def write_json(path, obj, canonical=False):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(canon(obj) if canonical else (json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode())


def sha12(data):
    return hashlib.sha256(data).hexdigest()[:12]


def pct(a, b):
    return (a / b - 1.0) * 100.0 if b else 0.0
