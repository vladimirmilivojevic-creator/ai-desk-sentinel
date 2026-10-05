# ai-desk-sentinel (Straža)

Javni repo. Bot koji svakih ~5 minuta (GitHub Actions) proverava cene, vesti i prediction markete i beleži kad se tržište naglo pomeri.
**Ne trguje, ne odlučuje i nema nikakav pristup novcu.** Zvoni mozgu (`ai-desk`, privatni repo) samo kad je jak signal, a mozak sve brojke ponovo proverava.
Prati: Brent, WTI, zlato, SP500, Nasdaq-100, BTC, ETH (+ VIX i DXY kao pomoćni signal). Simulacija, nije finansijski savet.

Javna tabla (GitHub Pages iz `/docs`): `https://<vlasnik>.github.io/ai-desk-sentinel/`

## Kako odlučuje (bez AI-ja)

Porodice signala, svaka je nezavisna: **P** cena (1, a 2 ako druga cena potvrdi smer), **PX** izuzetno velik pomak (≥ 2× prag), **X** više vrsta imovine se pomera istovremeno, **M** prediction market se pomerio ≥ 15 p.p., **H** naslovi iz ≥ 2 izdavača, **O** zvanični izvor (Fed, EIA), **V** GDELT (isključeno dok se ne proveri iz Actions-a).

| nivo | uslov | šta se dešava |
|---|---|---|
| N1 | jedna porodica | samo beleška i dnevni pregled |
| N2 | ocena ≥ 3,0 i cena je među signalima | alarm (Telegram), mozak sme samo da upravlja postojećim pozicijama |
| N3 | ocena ≥ 4,5, cena ≥ 2× prag, ≥ 3 porodice | jak alarm, mozak sme da razmotri ulaz |

Vest bez cenovnog pomaka nikad ne prelazi N1. Okidanje mozga: najviše 1 na 20 min, 4 na sat, 3 na dan; u okidaču su samo ID-jevi događaja i `sha12`, nikad tekst vesti.
Početno je **režim senke** (`config/sentinel.json`: `"fire_enabled": false`): straža beleži i šalje Telegram, ali ne zove mozak.

## Fajlovi

- `sentinel/run.py` jedan krug straže; `scoring.py` ocenjivanje (čista logika, testirana); `episodes.py` epizode i hlađenje; `sources.py` izvori; `notify.py` Telegram i okidač; `replay.py` kalibracija na istoriji.
- `config/` pragovi, instrumenti, upiti i kalendar. **Menja ih samo vlasnik repoa.**
- Grana `state` (siroče, jedan commit po krugu): `status/latest.json`, `heartbeat.json`, `health.json`... Čita je javna tabla i mozak.
- `events/YYYY/MM/EV-*.json` događaji N2+ (naslovi u njima su NEPOUZDAN tekst), `log/YYYY-MM-DD.jsonl` dnevni log. Piše ih samo workflow `sentinel`.
- `calibration/` rezultati replay-a (istorijska učestalost okidača).

## Sigurnost

- Tajne su samo u Actions secrets: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `FIRE_URL`, `FIRE_TOKEN`. Nikad u kodu, ni u četu, ni u logu (greške izvora ne sadrže URL).
- Workflow se pokreće samo na `schedule` i ručno (nikad `pull_request`), pa fork ne dobija tajne.
- Ovaj repo nikad ne sadrži portfolio, ključeve ni nalog.

## Testovi i provera

```
python -m unittest discover -s tests
python -m sentinel.run --probe          # jedan poziv svakog izvora
python -m sentinel.run --state _state --root . --dry
```
Ručni workflow-i: `probe` (dostupnost izvora iz Actions-a), `replay` (kalibracija pragova).

## Poznata ograničenja

- Cene kasne (Hyperliquid je skoro uživo, Yahoo futures oko 10 min), a Actions rasporedu kasni i do nekoliko minuta; zato je realno kašnjenje straže 5-20 min.
- GDELT daje 429 sa većine adresa; ostaje isključen dok `probe` ne pokaže drugačije.
- Kalendar objava: računata pravila (EIA sreda, NFP prvi petak, istek ugovora); tačne datume FOMC/CPI dodaje vlasnik u `config/calendar.json` ili ih mozak proverava preko Equibles kalendara.
- Pragovi su početni i kalibrišu se u senci; vidi `calibration/`.
