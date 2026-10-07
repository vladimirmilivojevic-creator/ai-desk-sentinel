# Studija derivatskih osobina (Binance javni arhiv), dnevne svece, kripto grupa

Generisano 2026-10-07T12:26:38Z. Instrumenata: 44, od 2025-01-01, trosak po krugu 0.23%, k=5, testova (unapred zadat skup): 54, BH-FDR 10% preko celog skupa.

Placebo (nasumican poredak, 20 zrna): H1 srednji Sharpe -3.61, sd 0.60, max -2.48; H3 srednji Sharpe -2.18, sd 0.73, max -0.94; H7 srednji Sharpe -1.22, sd 0.67, max 0.20

Sharpe i t su po tranšima (svaki se otvara i zatvara za sebe, konzervativno); 'prebijanje' = jedna pozicija po simbolu, trosak samo na promenu tezine (kako bi stvarno islo na berzi).

| osobina | znak (+ dugo visoko, - kontra) | H | Sharpe | t | Sharpe prebijanje, t | promet dnevno | god. prinos % | pad % | Sharpe po godinama | Sharpe uz stvarni taker | z prema placebu | FDR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top_acc_ls | -1 | 7 | 1.21 | 1.61 | 1.474, 1.97 | 0.111 | 33.1 | -16.0 | {2025: 0.96, 2026: 1.68} | 1.462 | 3.66 | ne |
| glob_ls | -1 | 7 | 1.08 | 1.44 | 1.348, 1.8 | 0.115 | 28.2 | -14.0 | {2025: 1.13, 2026: 1.02} | 1.341 | 3.46 | ne |
| top_pos_ls | -1 | 7 | 0.88 | 1.17 | 1.205, 1.61 | 0.078 | 23.5 | -27.2 | {2025: 0.92, 2026: 0.83} | 1.137 | 3.16 | ne |
| taker_z | -1 | 7 | 0.85 | 1.13 | 0.985, 1.32 | 0.239 | 11.2 | -11.8 | {2025: 1.75, 2026: -0.16} | 1.368 | 3.12 | ne |
| top_acc_ls | -1 | 3 | 0.73 | 0.97 | 1.415, 1.88 | 0.207 | 20.6 | -22.1 | {2025: 0.82, 2026: 0.6} | 1.292 | 3.98 | ne |
| top_pos_ls_z | -1 | 7 | 0.59 | 0.79 | 0.752, 1.0 | 0.215 | 10.3 | -19.4 | {2025: 1.06, 2026: -0.2} | 0.983 | 2.73 | ne |
| taker_z | -1 | 3 | 0.54 | 0.72 | 0.812, 1.08 | 0.547 | 9.6 | -15.2 | {2025: 1.17, 2026: -0.24} | 1.43 | 3.71 | ne |
| top_pos_ls | -1 | 3 | 0.47 | 0.62 | 1.253, 1.67 | 0.139 | 13.1 | -32.1 | {2025: 0.71, 2026: 0.1} | 1.027 | 3.61 | ne |
| glob_ls | -1 | 3 | 0.41 | 0.54 | 1.106, 1.47 | 0.216 | 10.9 | -22.1 | {2025: 0.44, 2026: 0.36} | 0.993 | 3.53 | ne |
| smart_div | -1 | 7 | 0.15 | 0.21 | 0.318, 0.42 | 0.217 | 2.6 | -16.3 | {2025: 0.65, 2026: -0.52} | 0.559 | 2.07 | ne |
| oi_chg_7 | +1 | 7 | -0.02 | -0.03 | 0.037, 0.05 | 0.251 | -0.5 | -34.1 | {2025: 0.07, 2026: -0.17} | 0.284 | 1.8 | ne |
| top_pos_ls_z | -1 | 3 | -0.04 | -0.05 | 0.471, 0.63 | 0.406 | -0.8 | -27.2 | {2025: 0.16, 2026: -0.39} | 0.708 | 2.92 | ne |
| oi_chg_3 | +1 | 7 | -0.06 | -0.07 | 0.038, 0.05 | 0.243 | -0.9 | -23.6 | {2025: 0.62, 2026: -1.22} | 0.338 | 1.75 | ne |
| oi_chg_7 | +1 | 3 | -0.13 | -0.17 | 0.277, 0.37 | 0.409 | -3.4 | -30.4 | {2025: 0.1, 2026: -0.48} | 0.474 | 2.8 | ne |
| glob_ls_z | -1 | 7 | -0.21 | -0.28 | -0.089, -0.12 | 0.228 | -4.0 | -23.7 | {2025: 0.06, 2026: -0.62} | 0.149 | 1.52 | ne |
| oi_chg_3 | +1 | 3 | -0.22 | -0.29 | -0.066, -0.09 | 0.579 | -5.0 | -28.2 | {2025: 0.14, 2026: -0.77} | 0.465 | 2.68 | ne |
| smart_div | -1 | 3 | -0.39 | -0.51 | 0.131, 0.17 | 0.413 | -7.9 | -22.4 | {2025: 0.17, 2026: -1.2} | 0.389 | 2.45 | ne |
| glob_ls_z | -1 | 3 | -0.91 | -1.20 | -0.469, -0.62 | 0.438 | -19.7 | -37.1 | {2025: -1.04, 2026: -0.71} | -0.18 | 1.74 | ne |
| oi_chg_7 | -1 | 7 | -1.06 | -1.40 | -0.994, -1.33 | 0.251 | -23.5 | -43.9 | {2025: -1.06, 2026: -1.07} | -0.752 | 0.25 | ne |
| glob_ls_z | +1 | 7 | -1.06 | -1.41 | -0.936, -1.25 | 0.228 | -20.0 | -39.4 | {2025: -1.26, 2026: -0.77} | -0.703 | 0.24 | ne |

Pozitivan t u 10 od 54 testova (znaci su ogledalo, pa se oko polovine ocekuje i bez prednosti); prolaze FDR: 30.

## Da li je to samo poznat faktor? Regresija korpe na kontrole (nizak vol 30 d, momentum 30 d i 90 d, isto H, isti trosak)

| osobina | znak | H | alfa god. % | t alfe | R2 | beta nizak_vol / mom30 / mom90 | dana |
|---|---|---|---|---|---|---|---|
| top_acc_ls | -1 | 7 | 28.3 | 1.54 | 0.202 | -0.208 / 0.081 / 0.228 | 644 |
| glob_ls | -1 | 7 | 23.8 | 1.32 | 0.167 | -0.181 / 0.1 / 0.171 | 644 |
| top_pos_ls | -1 | 7 | 26.7 | 1.47 | 0.181 | 0.088 / 0.039 / 0.265 | 644 |
| taker_z | -1 | 7 | 9.5 | 1.01 | 0.105 | -0.025 / 0.143 / -0.047 | 644 |
| top_acc_ls | -1 | 3 | 15.4 | 0.8 | 0.192 | -0.205 / 0.064 / 0.231 | 644 |
| top_pos_ls_z | -1 | 7 | 11.0 | 0.86 | 0.034 | 0.044 / 0.066 / 0.007 | 644 |

Placebo napomena: nasumican poredak placa isti trosak po tranšu, pa mu je Sharpe jako negativan (trosak, ne prednost); poredi se samo neto Sharpe i t, a 'z prema placebu' pokazuje koliko osobina gubi manje od slucajnosti, ne da zaradjuje. Simulacija ne prebija iste pozicije izmedju tranša, pa precenjuje trosak sporo promenljivih osobina.
