# Jezgro: istorijska provera (trend-ansambl na velikim kovanicama)

Generisano 2026-10-20T00:39Z, `python -m lab.core_study`. Pravila su upisana unapred u `config/core.json` (verzija 1) i nisu podesavana na ovim rezultatima. Podaci: Binance perp dnevne svece 2021-04-01..2026-10-14, 12 kovanica (ADA, AVAX, BNB, BTC, DOGE, ETH, LINK, LTC, SOL, TRX, XLM, XRP). Trosak 0.095% po strani (kao paper simulacija), signal na zatvaranju, prinos od sledeceg dana.

## Ukratko

- Ceo period (2021-04-01..2026-10-14): Sharpe 1.07, prosecno 23.5% godisnje pri volatilnosti 22.0%, najveci pad -25.7%. Kupi-i-drzi iste kovanice: Sharpe 0.56, pad -77.7%.
- Placebo (nasumican znak umesto trenda, ista mehanika, 60 ponavljanja): Sharpe u proseku 0.82 (sd 0.1). Placebo je samo-dugo sa oko pola vremena u poziciji, pa nosi isti kripto rast: ZASLUGA TRENDA JE RAZLIKA prema placebu, ne ceo rezultat.
- Mesecno: pozitivno 30 od 67 meseci, najgori -10.8%, najbolji 29.3%, medijana -0.35%.
- Dan nedeljnog rebalansa menja ishod (Sharpe po danima nedelje, ceo period): [1.18, 1.08, 1.26, 1.15, 1.12, 1.06, 1.07].

## Rezultat po godinama (neto %, jezgro / kupi-i-drzi / BTC)

| godina | jezgro | kupi-i-drzi | BTC |
|---|---|---|---|
| 2021 | 53.0 | 90.8 | -21.3 |
| 2022 | -18.9 | -68.3 | -64.2 |
| 2023 | 50.1 | 142.7 | 155.6 |
| 2024 | 42.1 | 125.1 | 121.3 |
| 2025 | 16.8 | -25.7 | -6.3 |
| 2026 | 4.0 | -9.1 | -4.6 |

## Po periodima i varijantama

| varijanta | 2021-04..2022-12 | 2023..2024 | 2025..danas | sve |
|---|---|---|---|---|
| kupi-i-drzi, jednako (bez troska) | Sharpe 0.15, god. 13.1%, pad -77.7% | Sharpe 1.8, god. 100.4%, pad -38.1% | Sharpe -0.06, god. -3.7%, pad -63.8% | Sharpe 0.56, god. 39.2%, pad -77.7% |
| BTC kupi-i-drzi | Sharpe -0.69, god. -47.9%, pad -76.6% | Sharpe 2.02, god. 98.4%, pad -26.2% | Sharpe 0.07, god. 3.1%, pad -53.0% | Sharpe 0.39, god. 21.4%, pad -76.6% |
| JEZGRO (ansambl 14/28/56/112, samo dugo, vol 20%) | Sharpe 0.64, god. 15.1%, pad -25.7% | Sharpe 1.76, god. 40.4%, pad -20.1% | Sharpe 0.66, god. 12.8%, pad -16.7% | Sharpe 1.07, god. 23.5%, pad -25.7% |
|   samo horizont L14 | Sharpe 0.6, god. 16.3%, pad -27.3% | Sharpe 1.17, god. 27.9%, pad -23.2% | Sharpe 0.46, god. 10.0%, pad -27.4% | Sharpe 0.76, god. 18.5%, pad -32.7% |
|   samo horizont L28 | Sharpe 0.96, god. 26.5%, pad -27.0% | Sharpe 1.84, god. 45.0%, pad -22.6% | Sharpe 0.46, god. 10.2%, pad -22.4% | Sharpe 1.12, god. 27.9%, pad -27.0% |
|   samo horizont L56 | Sharpe 0.56, god. 14.0%, pad -30.4% | Sharpe 1.59, god. 41.1%, pad -24.8% | Sharpe 0.53, god. 11.2%, pad -19.8% | Sharpe 0.95, god. 22.9%, pad -30.4% |
|   samo horizont L112 | Sharpe 0.13, god. 3.5%, pad -34.5% | Sharpe 1.97, god. 47.7%, pad -14.4% | Sharpe 0.89, god. 19.7%, pad -20.4% | Sharpe 1.02, god. 24.7%, pad -34.5% |
| ansambl dugo/kratko (isto) | Sharpe 0.4, god. 6.9%, pad -17.4% | Sharpe 0.46, god. 8.1%, pad -22.5% | Sharpe 0.11, god. 1.9%, pad -18.4% | Sharpe 0.33, god. 5.7%, pad -26.5% |
| JEZGRO uz trosak 0,20% po strani | Sharpe 0.6, god. 14.1%, pad -26.6% | Sharpe 1.7, god. 39.1%, pad -20.7% | Sharpe 0.59, god. 11.4%, pad -17.6% | Sharpe 1.01, god. 22.3%, pad -26.6% |
| JEZGRO ciljana vol 12% | Sharpe 0.67, god. 10.4%, pad -15.0% | Sharpe 1.7, god. 24.9%, pad -13.8% | Sharpe 0.74, god. 10.2%, pad -11.5% | Sharpe 1.06, god. 15.6%, pad -15.0% |
| JEZGRO ciljana vol 35% | Sharpe 0.58, god. 20.5%, pad -41.4% | Sharpe 1.82, god. 60.7%, pad -26.5% | Sharpe 0.51, god. 13.9%, pad -24.2% | Sharpe 1.02, god. 32.9%, pad -41.4% |
| placebo (nasumican znak, prosek 60, ISTA mehanika) | Sharpe 0.32, god. 7.1%, pad -30.3% | Sharpe 1.78, god. 38.1%, pad -16.8% | Sharpe 0.26, god. 5.6%, pad -29.4% | Sharpe 0.82, god. 17.8%, pad -31.4% |

## Ograničenja (iskreno)

- Istorija je kratka (oko 5 godina) i sadrzi samo dva velika rasta i jedan medved (2022). To je jedan uzorak trzista, ne zakon.
- Kovanice su bile jedne od najvecih 2020-2021 i prezivele su do danas (pristrasnost prezivelih), iako smo namerno uzeli najvece i najstarije. Uzorak 2025..danas je najmanje pristrasan.
- Jezgro je u sustini upravljan nacin drzanja kripto rizika (trend, volatilnost). U padu 2022. je izgubilo, u rastu 2023-24. zaradilo; ne zaradjuje kad trzista nema.
- Nista od ovoga nije dokaz buduce dobiti. Unapred se meri od T0 (`config/core.json`), a odluku o pravom novcu donosi iskljucivo vlasnik.
