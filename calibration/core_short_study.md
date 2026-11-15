# Kratka strana Jezgra i korpa po fondingu: istorijska provera (2026-11-15)

Pitanje vlasnika: može li sistem da zarađuje i kad tržište pada. Plan studije je upisan i objavljen pre pokretanja (`config/core_short_study.json`, commit 2a297ee).
Podaci: Binance perpetuali, lokalni keš, univerzum kakav je bio tog dana (top 12 po prometu 30 dana, 438 kovanica uključujući ugašene), 2021-06-01 do 2026-10-14, trošak 0,095% po strani, uz fonding. Isti motor kao `lab/core.py`.

## 1. Kratka strana po trendu (6 unapred upisanih varijanti)

| varijanta | 2021-06..2022-12 | 2023..2024 | 2025..danas | sve |
|---|---|---|---|---|
| A samo dugo (Jezgro) | Sharpe 0,02, 0,5%, pad −27,0% | 1,04, 22,3%, −21,2% | 0,26, 5,5%, −24,6% | **0,47, 10,3%, −27,0%** |
| B dugo i kratko simetrično | 0,31, 5,0%, −10,8% | 0,05, 0,8%, −20,5% | 0,22, 3,9%, −16,4% | 0,18, 3,1%, −23,0% |
| C samo kratko | 0,72, 17,1%, −19,5% | −1,21, −26,0%, −44,0% | −0,06, −1,6%, −27,4% | **−0,22, −5,2%, −55,9%** |
| D samo kratko, uz filter BTC | 0,89, 21,3%, −13,6% | −1,17, −18,3%, −33,8% | −0,13, −2,8%, −27,2% | **−0,07, −1,5%, −46,4%** |
| E = A + 0,5 x D | 0,53, 11,2%, −15,1% | 0,66, 13,2%, −24,2% | 0,21, 4,1%, −15,3% | 0,48, 9,6%, −24,2% |
| F = A + 0,5 x C | 0,47, 9,1%, −15,1% | 0,53, 9,4%, −19,9% | 0,27, 4,7%, −14,4% | 0,43, 7,7%, −19,9% |
| BTC kupi i drži | −0,54, −36,2%, −78,0% | 1,81, 88,5%, −29,3% | −0,02, −1,0%, −53,7% | 0,41, 21,9%, −78,0% |

Po godinama (%): A 2021 +12,6, 2022 −14,1, 2023 +33,9, 2024 +11,5, 2025 +8,3, 2026 −2,2. C 2021 −7,7, 2022 +36,1, 2023 −21,2, 2024 −28,0, 2025 −4,1, 2026 −4,2. E 2021 +13,0, 2022 +2,1, 2023 +22,6, 2024 +2,1, 2025 +10,2, 2026 −5,5.

**Odluka po unapred upisanom pravilu:** kratka noga sama (C i D) ima Sharpe ispod nule na celom uzorku, pa se kratka strana po trendu NE uvodi u Jezgro. Kratka strana zarađuje u godini pada (2022: +36%), ali to vraća i više od toga u godinama rasta (2023 −21%, 2024 −28%). Kombinacija E ne povećava prinos (9,6% prema 10,3%); ona samo premešta zaradu iz godina rasta u godine pada (osiguranje, ne dodatna zarada). Ostaje senka (rukavac S05).

## 2. Korpa po fondingu, tržišno neutralna (rukavci S13 i S14, upisani 2026-11-07)

Kratko k kovanica sa najvišim zbirom fondinga, dugo k sa najnižim, isti iznos na obe strane, ciljana volatilnost 20%, nedeljno. Ne zavisi od smera tržišta po konstrukciji.

| varijanta | 2021-06..2022-12 | 2023..2024 | 2025..danas | sve (t) |
|---|---|---|---|---|
| S13 (7 d, k=4), top 30 | Sharpe 0,48, 9,7%, pad −19,3% | 1,83, 38,9%, −16,1% | −0,05, −1,1%, −31,0% | 0,81, 17,0%, −31,0% (t 1,87) |
| S13, top 30, bez troška | 0,64 | 1,99 | 0,11 | 0,97 (t 2,24) |
| S14 (3 d, k=6), top 30 | −0,01, −0,1%, −20,5% | 2,12, 42,0%, −14,3% | 0,06, 1,3%, −26,1% | 0,78, 16,1%, −26,1% (t 1,81) |
| S13 (7 d, k=4), top 12 | 0,84, 15,8%, −14,1% | 1,03, 20,0%, −23,3% | 1,06, 21,0%, −16,3% | 0,99, 19,1%, −23,3% (t 2,29) |
| S14 (3 d, k=4), top 12 | 0,73, 13,2%, −14,3% | 0,91, 17,6%, −26,3% | 0,58, 13,5%, −21,2% | 0,73, 14,9%, −26,3% (t 1,70) |

Po godinama (%): S13 top 30: 2021 −2,5, 2022 +15,9, 2023 +51,1, 2024 +37,8, 2025 +5,1, 2026 −10,5. S13 top 12: 2021 +15,3, 2022 +8,4, 2023 +17,9, 2024 +21,9, 2025 +37,2, 2026 +2,4.

**Ocena (pošteno):** ovo je najjači trag do sada i jedini koji je pozitivan i u padu 2022. i u rastu 2023-2024. Nije dokaz: t je oko 2 (ispod praga 3 za više isprobanih varijanti), četiri varijante su gledane, top 30 je od 2025. oko nule (2026: −10,5%), a ranija studija korpe po fondingu sa drugačijom konstrukcijom (`carry_study.md`) je pala. Senka uživo: S13 +7,0% za 7 dana uz BTC −15,5% (premalo dana).
**Odluka:** S13 ulazi u paper trgovanje kao probni rukavac sa malim kapitalom (ai-desk `scripts/core_desk.py`, prekidač `FUND_TRADING`), tačno po upisanoj varijanti (30 kovanica sa Hyperliquid-a, 7 dana, k=4). Gasi se ako padne 10% kapitala rukavca od vrha.
