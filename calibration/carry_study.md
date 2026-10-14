# Korpa po fondingu (carry): studija (2026-10-14)

Unapred zadato u config/carry.json (verzija 1, 2026-10-14). 12 testova, FDR 10%. Kovanica sa fondingom: 320, period 2021-01-01 do 2026-09-30, k=5 po strani, trosak 0.33% po krugu. Placebo = nasumican izbor iste velicine, 50 ponavljanja.

'carry' = dugo najnizi fonding, kratko najvisi (prima se fonding); 'reverse' = obrnuto. 'cena' i 'fonding' su komponente srednjeg neto rezultata po periodu u %.

| test | n | srednje neto % | t | Sharpe | cena % | fonding % | prvi deo | poslednji deo | 270 d | placebo % (sd) | FDR | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carry:3d:14d | 148 | 1.122 | 2.02 | 0.85 | 0.91 | 0.542 | 2.13 | -0.356 | -1.549 | -0.339 (0.392) | da | odbaceno |
| carry:7d:14d | 148 | 0.895 | 2.02 | 0.85 | 0.655 | 0.57 | 1.202 | 0.445 | -1.252 | -0.346 (0.437) | da | odbaceno |
| carry:7d:7d | 298 | 0.398 | 1.62 | 0.68 | 0.38 | 0.347 | 0.598 | 0.1 | -1.443 | -0.302 (0.239) | ne | odbaceno |
| carry:3d:7d | 298 | 0.335 | 1.41 | 0.59 | 0.324 | 0.342 | 0.738 | -0.262 | -1.58 | -0.276 (0.266) | ne | odbaceno |
| carry:3d:3d | 698 | -0.033 | -0.3 | -0.13 | 0.126 | 0.171 | 0.187 | -0.361 | -0.47 | -0.317 (0.089) | ne | odbaceno |
| carry:7d:3d | 697 | -0.094 | -0.96 | -0.4 | 0.062 | 0.174 | 0.098 | -0.382 | -0.543 | -0.352 (0.071) | ne | odbaceno |
| reverse:3d:14d | 148 | -1.782 | -3.2 | -1.34 | -0.91 | -0.542 | -2.79 | -0.304 | 0.889 | -0.321 (0.392) | da | odbaceno |
| reverse:7d:14d | 148 | -1.555 | -3.51 | -1.47 | -0.655 | -0.57 | -1.862 | -1.105 | 0.592 | -0.314 (0.437) | da | odbaceno |
| reverse:3d:7d | 298 | -0.995 | -4.18 | -1.75 | -0.324 | -0.342 | -1.398 | -0.398 | 0.92 | -0.384 (0.266) | da | odbaceno |
| reverse:7d:7d | 298 | -1.058 | -4.3 | -1.8 | -0.38 | -0.347 | -1.258 | -0.76 | 0.783 | -0.358 (0.239) | da | odbaceno |
| reverse:3d:3d | 698 | -0.627 | -5.76 | -2.41 | -0.126 | -0.171 | -0.847 | -0.299 | -0.19 | -0.343 (0.089) | da | odbaceno |
| reverse:7d:3d | 697 | -0.566 | -5.8 | -2.42 | -0.062 | -0.174 | -0.758 | -0.278 | -0.117 | -0.308 (0.071) | da | odbaceno |

Kandidata: 0 od 12. Kad je komponenta fonding pozitivna a komponenta cena negativna, pomaci cene jedu fonding.

- carry:3d:14d po godinama (srednje neto %): {'2021': 5.733, '2022': -0.563, '2023': 1.284, '2024': 1.681, '2025': -0.387, '2026': -1.549}; pomereni početak (ofseti): [1.122, 1.045, 0.748]
- carry:7d:14d po godinama (srednje neto %): {'2021': 2.617, '2022': -0.22, '2023': 0.859, '2024': 2.681, '2025': 0.188, '2026': -1.252}; pomereni početak (ofseti): [0.895, 1.092, 1.507]
- carry:7d:7d po godinama (srednje neto %): {'2021': 1.946, '2022': -0.043, '2023': 0.058, '2024': 1.296, '2025': 0.143, '2026': -1.443}; pomereni početak (ofseti): [0.398, 0.405, 0.177]

Ograničenja: cena je spot, a fonding je sa perpetuala (razlika je zanemarena); fonding trenutnog meseca nije u arhivi pa studija ide do poslednjeg punog meseca; uzorak 2021-2026 ukljucuje dva velika tržišna režima; nema gledanja unapred (signal na dan d koristi fonding do kraja dana d, ulaz na otvaranju dana d+1).
