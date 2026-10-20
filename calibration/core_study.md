# Jezgro: istorijska provera (trend-ansambl na velikim kovanicama)

Generisano 2026-10-20T01:45Z, `python -m lab.core_study`. Pravila su upisana unapred u `config/core.json` (verzija 1) i nisu podesavana na ovim rezultatima. Podaci: Binance perp dnevne svece 2021-04-01..2026-10-14, 12 kovanica (ADA, AVAX, BNB, BTC, DOGE, ETH, LINK, LTC, SOL, TRX, XLM, XRP). Trosak 0.095% po strani (kao paper simulacija), signal na zatvaranju, prinos od sledeceg dana.

## Ukratko

- Ceo period (2021-04-01..2026-10-14): Sharpe 0.97, prosecno 21.3% godisnje pri volatilnosti 22.0%, najveci pad -25.6%. Kupi-i-drzi iste kovanice: Sharpe 0.56, pad -77.7%.
- Placebo (nasumican znak umesto trenda, ista mehanika, 60 ponavljanja): Sharpe u proseku 0.73 (sd 0.1). Placebo je samo-dugo sa oko pola vremena u poziciji, pa nosi isti kripto rast: ZASLUGA TRENDA JE RAZLIKA prema placebu, ne ceo rezultat.
- Mesecno: pozitivno 30 od 67 meseci, najgori -11.0%, najbolji 28.7%, medijana -0.39%.
- Dan nedeljnog rebalansa menja ishod (Sharpe po danima nedelje, ceo period): [1.09, 0.98, 1.16, 1.06, 1.03, 0.98, 0.97].

## Rezultat po godinama (neto %, jezgro / kupi-i-drzi / BTC)

| godina | jezgro | kupi-i-drzi | BTC |
|---|---|---|---|
| 2021 | 45.2 | 90.8 | -21.3 |
| 2022 | -18.2 | -68.3 | -64.2 |
| 2023 | 46.7 | 142.7 | 155.6 |
| 2024 | 36.3 | 125.1 | 121.3 |
| 2025 | 15.5 | -25.7 | -6.3 |
| 2026 | 3.9 | -9.1 | -4.6 |

## Po periodima i varijantama

| varijanta | 2021-04..2022-12 | 2023..2024 | 2025..danas | sve |
|---|---|---|---|---|
| kupi-i-drzi, jednako (bez troska) | Sharpe 0.15, god. 13.1%, pad -77.7% | Sharpe 1.8, god. 100.4%, pad -38.1% | Sharpe -0.06, god. -3.7%, pad -63.8% | Sharpe 0.56, god. 39.2%, pad -77.7% |
| BTC kupi-i-drzi | Sharpe -0.69, god. -47.9%, pad -76.6% | Sharpe 2.02, god. 98.4%, pad -26.2% | Sharpe 0.07, god. 3.1%, pad -53.0% | Sharpe 0.39, god. 21.4%, pad -76.6% |
| JEZGRO (ansambl 14/28/56/112, samo dugo, vol 20%, UZ FONDING) | Sharpe 0.53, god. 12.5%, pad -25.6% | Sharpe 1.63, god. 37.2%, pad -20.8% | Sharpe 0.63, god. 12.1%, pad -16.5% | Sharpe 0.97, god. 21.3%, pad -25.6% |
|   isto BEZ fondinga (kako je prvo racunato) | Sharpe 0.64, god. 15.1%, pad -25.7% | Sharpe 1.76, god. 40.4%, pad -20.1% | Sharpe 0.66, god. 12.8%, pad -16.7% | Sharpe 1.07, god. 23.5%, pad -25.7% |
|   samo horizont L14 | Sharpe 0.52, god. 14.1%, pad -27.4% | Sharpe 1.04, god. 24.6%, pad -24.0% | Sharpe 0.43, god. 9.2%, pad -27.8% | Sharpe 0.67, god. 16.3%, pad -32.6% |
|   samo horizont L28 | Sharpe 0.86, god. 23.7%, pad -27.2% | Sharpe 1.71, god. 41.8%, pad -23.4% | Sharpe 0.42, god. 9.4%, pad -22.5% | Sharpe 1.03, god. 25.6%, pad -27.2% |
|   samo horizont L56 | Sharpe 0.44, god. 11.0%, pad -30.3% | Sharpe 1.47, god. 37.9%, pad -25.4% | Sharpe 0.5, god. 10.6%, pad -19.5% | Sharpe 0.85, god. 20.6%, pad -30.3% |
|   samo horizont L112 | Sharpe 0.05, god. 1.3%, pad -33.5% | Sharpe 1.85, god. 44.6%, pad -14.9% | Sharpe 0.86, god. 19.0%, pad -20.2% | Sharpe 0.94, god. 22.7%, pad -33.5% |
| ansambl dugo/kratko (isto) | Sharpe 0.26, god. 4.4%, pad -18.0% | Sharpe 0.37, god. 6.6%, pad -22.3% | Sharpe 0.09, god. 1.5%, pad -18.3% | Sharpe 0.25, god. 4.3%, pad -27.2% |
| JEZGRO uz trosak 0,20% po strani | Sharpe 0.49, god. 11.6%, pad -26.4% | Sharpe 1.57, god. 35.9%, pad -21.5% | Sharpe 0.56, god. 10.7%, pad -17.5% | Sharpe 0.91, god. 20.1%, pad -26.4% |
| JEZGRO ciljana vol 12% | Sharpe 0.57, god. 8.8%, pad -15.0% | Sharpe 1.56, god. 22.9%, pad -14.3% | Sharpe 0.71, god. 9.7%, pad -11.4% | Sharpe 0.97, god. 14.2%, pad -15.0% |
| JEZGRO ciljana vol 35% | Sharpe 0.46, god. 16.3%, pad -41.1% | Sharpe 1.68, god. 56.1%, pad -27.5% | Sharpe 0.48, god. 13.0%, pad -24.0% | Sharpe 0.92, god. 29.6%, pad -41.1% |
| placebo (nasumican znak, prosek 60, ISTA mehanika) | Sharpe 0.23, god. 4.9%, pad -30.3% | Sharpe 1.64, god. 35.0%, pad -17.0% | Sharpe 0.23, god. 5.0%, pad -29.4% | Sharpe 0.73, god. 15.8%, pad -31.4% |

## Ograničenja (iskreno)

- Istorija je kratka (oko 5 godina) i sadrzi samo dva velika rasta i jedan medved (2022). To je jedan uzorak trzista, ne zakon.
- Kovanice su bile jedne od najvecih 2020-2021 i prezivele su do danas (pristrasnost prezivelih), iako smo namerno uzeli najvece i najstarije. Uzorak 2025..danas je najmanje pristrasan.
- Jezgro je u sustini upravljan nacin drzanja kripto rizika (trend, volatilnost). U padu 2022. je izgubilo, u rastu 2023-24. zaradilo; ne zaradjuje kad trzista nema.
- Nista od ovoga nije dokaz buduce dobiti. Unapred se meri od T0 (`config/core.json`), a odluku o pravom novcu donosi iskljucivo vlasnik.
