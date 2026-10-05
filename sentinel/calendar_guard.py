"""Oznaka 'zakazano': da li je trenutak blizu poznate objave ili isteka ugovora.
Bez zoneinfo (na Windows-u nema tzdata): americko letnje racunanje je ugradjeno."""
import datetime as dt


def _nth_weekday(year, month, weekday, n):
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def ny_offset_hours(utc):
    """UTC-4 od 2. nedelje marta 07:00 UTC do 1. nedelje novembra 06:00 UTC, inace UTC-5."""
    y = utc.year
    start = dt.datetime.combine(_nth_weekday(y, 3, 6, 2), dt.time(7, 0), tzinfo=dt.timezone.utc)
    end = dt.datetime.combine(_nth_weekday(y, 11, 6, 1), dt.time(6, 0), tzinfo=dt.timezone.utc)
    return -4 if start <= utc < end else -5


def scheduled_flags(now_ts, cal):
    utc = dt.datetime.fromtimestamp(now_ts, dt.timezone.utc)
    win = cal.get("window_min", 20) * 60
    flags = []

    def near(target):
        return abs((utc - target).total_seconds()) <= win

    off = ny_offset_hours(utc)
    for w in cal.get("weekly", []):
        # najblizi dogadjaj istog dana u nedelji (juce, danas, sutra radi granice dana)
        for delta in (-1, 0, 1):
            d = (utc + dt.timedelta(days=delta)).date()
            if d.weekday() == w["weekday"]:
                t = dt.datetime.combine(d, dt.time(w["hour"], w["minute"]), tzinfo=dt.timezone.utc) - dt.timedelta(
                    hours=off)
                if near(t):
                    flags.append(w["name"])
    for m in cal.get("monthly_first_friday", []):
        for delta in (-1, 0, 1):
            d = (utc + dt.timedelta(days=delta)).date()
            if d == _nth_weekday(d.year, d.month, 4, 1):
                t = dt.datetime.combine(d, dt.time(m["hour"], m["minute"]), tzinfo=dt.timezone.utc) - dt.timedelta(
                    hours=off)
                if near(t):
                    flags.append(m["name"])
    if utc.month in cal.get("quad_witching_months", []) and utc.date() == _nth_weekday(utc.year, utc.month, 4, 3):
        flags.append("istek terminskih ugovora (treci petak)")
    for s in cal.get("dates", []):
        try:
            t = dt.datetime.strptime(s["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        except (KeyError, ValueError):
            continue
        if near(t):
            flags.append(s.get("name", "objava"))
    return flags
