"""Telegram i okidanje mozga. Greske nikad ne stampaju URL niti token."""
import json
import os

from .util import SourceError, http


def telegram(text, dry=False):
    """Obican tekst, bez parse_mode. Vraca (ok, poruka)."""
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return False, "telegram nije podesen"
    if dry:
        return True, "dry"
    try:
        http("POST", "https://api.telegram.org/bot%s/sendMessage" % token,
             {"chat_id": chat, "text": text[:400], "disable_web_page_preview": True}, retries=2)
        return True, "poslato"
    except SourceError as e:
        return False, "telegram greska: %s" % e


def fire_brain(payload, dry=False):
    """POST na /fire routine 'desk-shock'. Samo ID-jevi i sha12, nikad tekst vesti."""
    url, token = os.environ.get("FIRE_URL"), os.environ.get("FIRE_TOKEN")
    if not url or not token:
        return False, "FIRE_URL/FIRE_TOKEN nisu podeseni"
    if dry:
        return True, "dry"
    body = {"text": json.dumps(payload, separators=(",", ":"))}
    last = "greska"
    for i in range(3):
        try:
            http("POST", url, body, headers={"Authorization": "Bearer " + token,
                                             "anthropic-beta": "experimental-cc-routine-2026-04-01",
                                             "anthropic-version": "2023-06-01"}, retries=1, timeout=15)
            return True, "okinuto"
        except SourceError as e:
            last = str(e)
    return False, "fire greska: %s" % last
