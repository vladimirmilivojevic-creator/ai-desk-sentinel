"""Mrezni pomocnici za kolektore: ponavljanje sa pauzom (429/5xx), vremenska ogranicenja, bez stampanja URL-a ili kljuca u greskama."""
import json
import time
import urllib.error
import urllib.request

UA = "ai-desk-sentinel/0.3 (public research bot, no trading)"
BROWSER_UA = "Mozilla/5.0 (compatible; ai-desk-sentinel/0.3)"


class NetError(Exception):
    """Greska izvora; poruka nikad ne sadrzi URL ni kljuc."""

    def __init__(self, msg, status=None):
        super().__init__(msg)
        self.status = status


def request(method, url, body=None, headers=None, timeout=20, tries=3, pause=0.0, ua=UA, max_bytes=8_000_000):
    h = {"User-Agent": ua}
    h.update(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    last = NetError("nepoznato")
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(max_bytes)
            if pause:
                time.sleep(pause)
            return raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = NetError("HTTP %s" % e.code, status=e.code)
            if e.code in (400, 401, 403, 404, 451):
                break  # ponavljanje ne pomaze
            retry_after = 0
            try:
                retry_after = int(e.headers.get("Retry-After", 0))
            except (TypeError, ValueError, AttributeError):
                pass
            time.sleep(max(retry_after, 1.5 * (k + 1)))
        except Exception as e:  # noqa: BLE001
            last = NetError(type(e).__name__)
            time.sleep(1.5 * (k + 1))
    raise last


def get_text(url, **kw):
    return request("GET", url, **kw)


def get_json(url, **kw):
    return json.loads(request("GET", url, **kw))


def post_json(url, body, **kw):
    return json.loads(request("POST", url, body=body, **kw))
