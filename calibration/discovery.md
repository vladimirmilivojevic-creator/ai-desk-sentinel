# Lovac: studija na sirem univerzumu (2026-10-10)

Univerzumi: stocks 44 instrumenata (2020-10-12 do 2026-10-09); crypto 413 instrumenata (2020-06-24 do 2026-10-09); commodities 20 instrumenata (2020-10-12 do 2026-10-09).
Testova: 180 (rang-porodice x horizonti x noge, dogadjaji x horizonti x noge), FDR 10% preko svih. Trosak 0.23% po krugu (strogo 0.50%). Mera = prosecan neto prinos ODABRANE grupe minus prosek univerzuma; nepreklapajuci periodi; t preko perioda.
Status: kandidat 4, nagovestaj 10, odbaceno 154, premalo 12.

Izvedivost: kolone 'izvedivo' su isti test samo na simbolima koje Liquid ima SADA (pristrasno prema preziveloj listi); kandidat mora da bude pozitivan i tamo (t >= 1).

Ogranicenja (cita se pre brojeva): nema stopova u testu; ulaz je otvaranje sledece svece, a uzivo se ulazi sat-dva kasnije. Zato jedino 'potvrdjen' (posle prolaska unapred) ima ikakvu tezinu.
- stocks: spisak je prema SADASNJOJ listi Liquid-a (preziveli i popularni), pa su istorijski rezultati verovatno prelepi.
- crypto: clanstvo je point-in-time (prvih 40 po prometu na dan, ukljucuje i kasnije ugasene kovanice), ali se trguje samo kovanicama koje Liquid sada ima; podaci su Binance spot, ne Liquid; uzivo se ulazi sat-dva posle otvaranja dnevne svece (dodato 0.10% troska).
- commodities: Yahoo futures serije NISU ispravljene za zamenu ugovora (skokovi pri roll-u), pa je rezultat zasumljen i dodato je 0.15% troska; platinum, paladijum i aluminijum nisu u studiji (Yahoo nema obim).

## Svi testovi, poredjani po t

| pravilo | n | neto % | medijana % | bez najboljeg % | t | p | t prvi deo | t zadnji deo | zadnjih 270 d % | strogi trosak % | izvedivo n | izvedivo neto % | izvedivo t | FDR | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crypto:BRK20:2w:short | 161 | 2.9764 | 3.4346 | 2.8328 | 5.12 | 0.0 | 2.72 | 5.08 | 5.399 | 2.7064 | 161 | 0.4719 | 0.62 | da | nagovestaj |
| crypto:BRK20:1w:short | 323 | 1.5032 | 1.6978 | 1.4267 | 4.9 | 0.0 | 3.01 | 4.43 | 2.839 | 1.2332 | 323 | 0.3913 | 1.24 | da | kandidat |
| crypto:LOWVOL:2w:short | 159 | 3.5754 | 3.4955 | 3.3586 | 4.89 | 0.0 | 2.94 | 4.24 | 10.3796 | 3.3054 | 159 | -0.3432 | -0.35 | da | nagovestaj |
| crypto:BRK20:4w:short | 80 | 5.2193 | 4.3084 | 4.7663 | 4.52 | 1e-05 | 2.12 | 4.92 | 8.004 | 4.9493 | 80 | 2.2199 | 1.71 | da | kandidat |
| crypto:SPIKE_DN:14d:short | 69 | 10.9198 | 12.8656 | 9.9636 | 4.03 | 6e-05 | 1.27 | 5.81 | 23.8974 | 10.6498 | 28 | 5.1396 | 1.4 | da | kandidat |
| crypto:LOWVOL:1w:short | 319 | 1.4183 | 1.593 | 1.3501 | 3.57 | 0.00036 | 1.89 | 3.85 | 4.4677 | 1.1483 | 319 | -0.237 | -0.53 | da | nagovestaj |
| crypto:SPIKE_DN:28d:short | 37 | 18.5927 | 22.4138 | 17.1764 | 3.53 | 0.00042 | 1.67 | 4.64 | 31.1919 | 18.3227 | 11 | 0.4642 | 0.17 | da | nagovestaj |
| crypto:BRK20:2w:long | 161 | 1.8113 | 1.3302 | 1.5847 | 3.12 | 0.00181 | 2.86 | 1.32 | 0.8359 | 1.5413 | 161 | 1.0315 | 1.24 | da | kandidat |
| crypto:LOWVOL:4w:short | 79 | 4.4454 | 4.7566 | 3.94 | 3.02 | 0.00253 | 1.24 | 3.87 | 14.6478 | 4.1754 | 79 | -3.3869 | -1.14 | da | nagovestaj |
| crypto:LOWVOL:2w:long | 159 | 1.3611 | 1.5536 | 1.2512 | 2.95 | 0.00318 | 1.07 | 4.04 | 2.2205 | 1.0911 | 159 | 0.1046 | 0.15 | da | nagovestaj |
| stocks:SPIKE_UP:10d:long | 86 | 6.1791 | 0.0463 | 4.8698 | 2.78 | 0.00544 | 2.37 | 1.44 | -0.5185 | 5.9091 | - | - | - | da | nagovestaj |
| crypto:SPIKE_DN:7d:short | 129 | 5.1756 | 6.9939 | 4.6578 | 2.56 | 0.01047 | 0.72 | 2.9 | 11.1288 | 4.9056 | 54 | -2.6872 | -0.78 | da | nagovestaj |
| crypto:LOWVOL:4w:long | 79 | 3.0496 | 4.1021 | 2.7381 | 2.48 | 0.01314 | 0.76 | 4.19 | 2.5473 | 2.7796 | 79 | 1.0511 | 0.56 | da | nagovestaj |
| crypto:LOWVOL:1w:long | 319 | 0.5673 | 0.5866 | 0.486 | 2.08 | 0.03753 | 1.0 | 2.2 | 0.7376 | 0.2973 | 319 | -0.1491 | -0.44 | ne | nagovestaj |
| crypto:VOLUP:4w:short | 80 | 1.9549 | 1.0824 | 1.6254 | 1.82 | 0.06876 | 1.17 | 1.63 | 1.2785 | 1.6849 | 80 | -0.9369 | -0.63 | ne | odbaceno |
| commodities:HIGH_BRK:20d:long | 13 | 5.0768 | 2.0248 | 2.9489 | 1.81 | None | 1.18 | 1.35 | 1.4103 | 4.8068 | 0 | None | None | ne | premalo |
| crypto:HIGH52:2w:short | 145 | 1.0769 | 0.9505 | 0.8554 | 1.79 | 0.07345 | 1.5 | 0.96 | 1.1174 | 0.8069 | 143 | 0.2019 | 0.34 | ne | odbaceno |
| crypto:SPIKE_UP:7d:short | 227 | 1.6187 | 2.9781 | 1.4349 | 1.63 | 0.1031 | -0.24 | 3.68 | 5.7873 | 1.3487 | 157 | 0.1435 | 0.1 | ne | odbaceno |
| commodities:SPIKE_UP:5d:short | 71 | 0.7742 | 1.285 | 0.6477 | 1.55 | 0.12114 | 0.57 | 1.86 | 2.3022 | 0.5042 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:14d:short | 112 | 2.5918 | 2.3824 | 2.0957 | 1.53 | 0.12602 | 0.13 | 2.3 | 6.739 | 2.3218 | 74 | -1.2316 | -0.53 | ne | odbaceno |
| commodities:HIGH_BRK:10d:long | 24 | 1.9496 | 0.8253 | 1.1931 | 1.5 | None | 1.52 | 0.34 | 0.6289 | 1.6796 | 0 | None | None | ne | premalo |
| stocks:MOM12_1:4w:long | 64 | 1.233 | 0.7364 | 0.8561 | 1.37 | 0.17069 | -0.66 | 2.55 | 2.4059 | 0.963 | - | - | - | ne | odbaceno |
| crypto:VOLUP:2w:short | 161 | 0.7985 | 0.9294 | 0.6146 | 1.37 | 0.17069 | 1.38 | 0.43 | 2.6303 | 0.5285 | 161 | -0.2908 | -0.4 | ne | odbaceno |
| crypto:BRK20:1w:long | 323 | 0.5035 | 0.4 | 0.3623 | 1.34 | 0.18025 | 1.25 | 0.53 | -0.4972 | 0.2335 | 323 | 0.359 | 0.81 | ne | odbaceno |
| crypto:HIGH52:2w:long | 145 | 0.7913 | 0.4797 | 0.5869 | 1.3 | 0.1936 | 1.51 | 0.05 | -1.8479 | 0.5213 | 143 | 0.1114 | 0.17 | ne | odbaceno |
| stocks:VOLUP:4w:long | 76 | 1.2704 | 0.8939 | 0.7591 | 1.27 | 0.20408 | 0.66 | 1.19 | -0.0799 | 1.0004 | - | - | - | ne | odbaceno |
| stocks:ATTN:2w:long | 149 | 0.6328 | -0.3237 | 0.2715 | 1.25 | 0.2113 | 0.86 | 1.11 | 0.3472 | 0.3628 | - | - | - | ne | odbaceno |
| crypto:ATTN:2w:short | 159 | 0.6207 | 0.2006 | 0.4841 | 1.23 | 0.2187 | 0.43 | 1.96 | 0.3965 | 0.3507 | 159 | 0.1761 | 0.29 | ne | odbaceno |
| stocks:VOLUP:2w:long | 153 | 0.4462 | -0.3376 | 0.3247 | 1.19 | 0.23405 | 0.82 | 0.86 | 1.0869 | 0.1762 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:7d:short | 117 | 2.1255 | 1.7949 | 1.5409 | 1.14 | 0.25429 | 1.6 | -0.05 | 12.6245 | 1.8555 | 76 | -2.5508 | -1.62 | ne | odbaceno |
| stocks:MOM12_1:2w:long | 129 | 0.5197 | 0.2242 | 0.3727 | 1.13 | 0.25848 | -0.95 | 2.34 | 1.4287 | 0.2497 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:short | 38 | 2.7019 | 5.6091 | 2.0408 | 1.11 | 0.267 | 0.81 | 0.73 | 9.4291 | 2.4319 | - | - | - | ne | odbaceno |
| crypto:HIGH52:1w:short | 291 | 0.3423 | 0.6462 | 0.2534 | 1.1 | 0.27133 | 1.6 | -0.31 | -0.2325 | 0.0723 | 286 | -0.1565 | -0.52 | ne | odbaceno |
| crypto:BRK20:4w:long | 80 | 1.2084 | 2.7674 | 0.8172 | 0.98 | 0.32709 | 0.09 | 1.8 | -1.2494 | 0.9384 | 80 | -0.7687 | -0.5 | ne | odbaceno |
| crypto:MOM12_1:4w:short | 72 | 1.1704 | 2.9601 | 0.8961 | 0.97 | 0.33205 | -0.07 | 2.31 | 4.0695 | 0.9004 | 71 | 1.4648 | 1.33 | ne | odbaceno |
| stocks:SPIKE_UP:5d:long | 178 | 0.6713 | -0.3363 | 0.4427 | 0.92 | 0.35757 | 1.2 | -0.13 | -2.7206 | 0.4013 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:long | 53 | 1.4373 | 0.1846 | 0.7096 | 0.91 | 0.36282 | 1.02 | 0.19 | 1.2027 | 1.1673 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:14d:short | 61 | 2.529 | 4.0441 | 1.2704 | 0.73 | 0.46539 | 0.56 | 0.46 | 13.1142 | 2.259 | 38 | -2.0291 | -0.68 | ne | odbaceno |
| crypto:ATTN:1w:short | 319 | 0.2019 | 0.3089 | 0.1416 | 0.71 | 0.4777 | -0.26 | 2.09 | 0.2494 | -0.0681 | 319 | -0.007 | -0.02 | ne | odbaceno |
| crypto:REV5:4w:short | 80 | 1.0772 | 1.242 | 0.6081 | 0.69 | 0.49019 | 1.09 | -0.43 | 6.2689 | 0.8072 | 80 | -1.1403 | -0.5 | ne | odbaceno |
| crypto:SPIKE_UP:28d:short | 54 | 2.592 | 5.8182 | 0.8616 | 0.69 | 0.49019 | -1.32 | 2.92 | 19.138 | 2.322 | 28 | -2.1005 | -0.51 | ne | odbaceno |
| commodities:SPIKE_UP:10d:short | 35 | 0.689 | 2.4613 | 0.3705 | 0.59 | 0.55519 | 0.39 | 0.44 | -0.0295 | 0.419 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_DN:5d:short | 139 | 0.3506 | 0.812 | 0.061 | 0.52 | 0.60306 | -0.35 | 1.1 | 1.8762 | 0.0806 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:10d:long | 67 | 0.8324 | 0.0197 | -0.4483 | 0.41 | 0.68181 | 0.71 | -0.52 | -6.3599 | 0.5624 | - | - | - | ne | odbaceno |
| crypto:HIGH52:4w:short | 72 | 0.5574 | 2.2465 | 0.3728 | 0.41 | 0.68181 | -0.16 | 1.46 | 1.3108 | 0.2874 | 71 | 0.778 | 0.67 | ne | odbaceno |
| crypto:VOLUP:1w:short | 323 | 0.1214 | 0.503 | 0.0482 | 0.41 | 0.68181 | 0.88 | -0.49 | 0.8388 | -0.1486 | 323 | -0.4772 | -1.46 | ne | odbaceno |
| stocks:MOM12_1:1w:long | 260 | 0.081 | -0.2158 | 0.0311 | 0.35 | 0.72634 | -0.93 | 1.25 | 0.4266 | -0.189 | - | - | - | ne | odbaceno |
| crypto:HIGH52:4w:long | 72 | 0.4573 | 0.4927 | -0.1455 | 0.34 | 0.73386 | 0.35 | 0.08 | -3.6514 | 0.1873 | 71 | -0.2198 | -0.13 | ne | odbaceno |
| crypto:MOM12_1:2w:short | 145 | 0.2356 | 1.2706 | 0.0596 | 0.33 | 0.7414 | -0.58 | 1.8 | 0.8365 | -0.0344 | 143 | 0.2596 | 0.45 | ne | odbaceno |
| commodities:ATTN:4w:short | 74 | 0.1643 | -0.4157 | -0.0923 | 0.3 | 0.76418 | -0.09 | 0.49 | 3.7626 | -0.1057 | 0 | None | None | ne | odbaceno |
| commodities:BRK20:4w:short | 76 | 0.176 | 0.0179 | -0.0311 | 0.28 | 0.77948 | 1.29 | -0.67 | 0.2826 | -0.094 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:1w:long | 308 | 0.0443 | -0.1448 | -0.0323 | 0.24 | 0.81033 | 0.42 | -0.11 | 0.0413 | -0.2257 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:28d:short | 27 | 1.809 | 6.4546 | -0.4864 | 0.22 | None | 0.15 | 0.15 | 23.5027 | 1.539 | 16 | -4.3068 | -0.62 | ne | premalo |
| stocks:ATTN:1w:long | 300 | 0.0349 | -0.1543 | -0.0584 | 0.18 | 0.85715 | -0.22 | 0.67 | 0.1477 | -0.2351 | - | - | - | ne | odbaceno |
| commodities:SPIKE_DN:5d:long | 72 | 0.1088 | 0.0606 | -0.081 | 0.18 | 0.85715 | -0.14 | 0.39 | -1.7537 | -0.1612 | 0 | None | None | ne | odbaceno |
| crypto:HIGH52:1w:long | 291 | 0.068 | -0.1524 | -0.1979 | 0.16 | 0.87288 | 0.59 | -0.85 | -1.6374 | -0.202 | 286 | -0.0896 | -0.28 | ne | odbaceno |
| crypto:MOM12_1:4w:long | 72 | 0.1827 | -1.5434 | -0.327 | 0.13 | 0.89657 | 0.43 | -0.53 | -0.6009 | -0.0873 | 71 | 1.3232 | 0.89 | ne | odbaceno |
| stocks:VOLUP:1w:long | 308 | 0.0241 | -0.157 | -0.0522 | 0.12 | 0.90448 | 0.29 | -0.17 | -0.1525 | -0.2459 | - | - | - | ne | odbaceno |
| crypto:ATTN:4w:short | 79 | 0.1201 | 0.8914 | -0.1562 | 0.12 | 0.90448 | -0.67 | 1.68 | 0.9923 | -0.1499 | 79 | 0.4673 | 0.28 | ne | odbaceno |
| stocks:REV5:4w:long | 77 | 0.204 | -1.0362 | -1.7632 | 0.1 | 0.92034 | 0.63 | -1.88 | -4.5457 | -0.066 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:4w:long | 64 | 0.0624 | 0.4103 | -0.1464 | 0.08 | 0.93624 | -0.05 | 0.16 | -2.8176 | -0.2076 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:4w:long | 76 | 0.0326 | 1.1246 | -0.1788 | 0.04 | 0.96809 | -0.28 | 0.39 | 0.4412 | -0.2374 | - | - | - | ne | odbaceno |
| commodities:REV5:2w:long | 155 | 0.0103 | 0.0608 | -0.0737 | 0.03 | 0.97607 | -0.72 | 0.79 | -0.4314 | -0.2597 | 0 | None | None | ne | odbaceno |
| commodities:LOWVOL:4w:short | 74 | 0.0019 | 0.4913 | -0.2566 | 0.0 | 1.0 | 0.31 | -0.29 | 1.4545 | -0.2681 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:20d:short | 45 | -0.1229 | 1.6821 | -0.9813 | -0.04 | 0.96809 | -0.6 | 0.88 | 8.9655 | -0.3929 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:20d:long | 27 | -0.1387 | -0.8921 | -1.3524 | -0.05 | None | 0.04 | -0.22 | 1.8999 | -0.4087 | - | - | - | ne | premalo |
| stocks:BRK20:2w:long | 153 | -0.0176 | -0.2706 | -0.0883 | -0.06 | 0.95216 | -0.99 | 0.78 | -0.2208 | -0.2876 | - | - | - | ne | odbaceno |
| stocks:SPIKE_UP:20d:long | 45 | -0.3371 | -2.1421 | -2.0031 | -0.11 | 0.91241 | 0.5 | -0.99 | -9.4255 | -0.6071 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:20d:short | 27 | -0.3213 | 0.4321 | -1.9916 | -0.11 | None | -0.14 | 0.05 | -2.3599 | -0.5913 | - | - | - | ne | premalo |
| commodities:SPIKE_UP:20d:short | 21 | -0.2964 | 1.5262 | -0.8578 | -0.12 | None | 1.31 | -0.79 | -2.1662 | -0.5664 | 0 | None | None | ne | premalo |
| commodities:SPIKE_DN:20d:short | 14 | -0.3284 | 0.8551 | -1.3729 | -0.16 | None | -0.3 | 0.65 | 1.1052 | -0.5984 | 0 | None | None | ne | premalo |
| crypto:REV5:2w:short | 161 | -0.1132 | 0.2227 | -0.2853 | -0.18 | 0.85715 | -0.71 | 0.79 | 3.5431 | -0.3832 | 161 | -1.2557 | -1.57 | ne | odbaceno |
| commodities:SPIKE_UP:20d:long | 21 | -0.4636 | -2.2862 | -2.5735 | -0.19 | None | -1.71 | 0.64 | 1.4062 | -0.7336 | 0 | None | None | ne | premalo |
| commodities:SPIKE_DN:20d:long | 14 | -0.4316 | -1.6151 | -1.7835 | -0.21 | None | 0.09 | -1.39 | -1.8652 | -0.7016 | 0 | None | None | ne | premalo |
| stocks:MOM12_1:4w:short | 64 | -0.1962 | 0.244 | -0.4092 | -0.22 | 0.82587 | -0.64 | 0.64 | 1.4996 | -0.4662 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:5d:short | 109 | -0.1684 | 0.2965 | -0.513 | -0.22 | 0.82587 | -0.31 | 0.02 | 0.2999 | -0.4384 | - | - | - | ne | odbaceno |
| crypto:REV5:1w:short | 323 | -0.0898 | 0.2969 | -0.1548 | -0.23 | 0.81809 | -0.82 | 1.26 | 1.2624 | -0.3598 | 323 | -0.7553 | -1.7 | ne | odbaceno |
| stocks:HIGH52:4w:long | 64 | -0.1757 | -0.1934 | -0.453 | -0.24 | 0.81033 | -0.95 | 0.45 | 1.981 | -0.4457 | - | - | - | ne | odbaceno |
| commodities:SPIKE_DN:10d:short | 37 | -0.2959 | 0.3949 | -1.051 | -0.26 | 0.79486 | -1.05 | 0.56 | -1.0988 | -0.5659 | 0 | None | None | ne | odbaceno |
| crypto:VOLUP:2w:long | 161 | -0.2156 | -1.3223 | -0.709 | -0.28 | 0.77948 | 0.38 | -1.3 | -0.6118 | -0.4856 | 161 | 0.1117 | 0.14 | ne | odbaceno |
| crypto:HIGH_BRK:28d:long | 27 | -2.469 | -7.1146 | -7.9446 | -0.3 | None | -0.22 | -0.2 | -24.1627 | -2.739 | 16 | 3.6468 | 0.52 | ne | premalo |
| stocks:HIGH_BRK:5d:long | 109 | -0.2916 | -0.7565 | -0.5843 | -0.38 | 0.70395 | -0.17 | -0.38 | -0.7599 | -0.5616 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:short | 50 | -0.2726 | -0.3989 | -0.6397 | -0.38 | 0.70395 | -1.15 | 0.64 | 0.4767 | -0.5426 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:10d:long | 37 | -0.4641 | -1.1549 | -0.893 | -0.41 | 0.68181 | 0.44 | -0.93 | 0.3388 | -0.7341 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:4w:long | 64 | -0.2596 | 0.5698 | -0.517 | -0.44 | 0.65994 | 0.66 | -1.22 | -6.2103 | -0.5296 | 0 | None | None | ne | odbaceno |
| stocks:REV5:1w:long | 311 | -0.1059 | -0.4578 | -0.1659 | -0.56 | 0.57548 | -0.32 | -0.49 | 0.0315 | -0.3759 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:2w:long | 129 | -0.2214 | 0.2037 | -0.2944 | -0.59 | 0.55519 | -0.52 | -0.29 | -1.3107 | -0.4914 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:2w:long | 149 | -0.1441 | 0.0313 | -0.1906 | -0.6 | 0.54851 | -1.21 | 0.4 | 1.1156 | -0.4141 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:2w:short | 149 | -0.2015 | -0.2451 | -0.2645 | -0.61 | 0.54186 | 0.98 | -2.42 | -0.2422 | -0.4715 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:10d:short | 67 | -1.2924 | -0.4797 | -1.8578 | -0.63 | 0.52869 | -0.86 | 0.32 | 5.8999 | -1.5624 | - | - | - | ne | odbaceno |
| stocks:HIGH52:2w:long | 129 | -0.2253 | -0.1537 | -0.3167 | -0.64 | 0.52217 | -1.67 | 0.64 | 0.5468 | -0.4953 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:long | 50 | -0.4874 | -0.3611 | -0.8464 | -0.69 | 0.49019 | 0.25 | -1.26 | -1.2367 | -0.7574 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:2w:short | 129 | -0.2908 | -0.6588 | -0.3793 | -0.7 | 0.48393 | -1.15 | 0.42 | 1.1697 | -0.5608 | - | - | - | ne | odbaceno |
| commodities:ATTN:4w:long | 74 | -0.367 | -0.4571 | -0.4845 | -0.78 | 0.43539 | -0.46 | -0.63 | 0.3673 | -0.637 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:1w:short | 300 | -0.1335 | 0.1094 | -0.1619 | -0.82 | 0.41222 | -0.57 | -0.64 | 0.2901 | -0.4035 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:1w:short | 291 | -0.306 | 0.1861 | -0.3568 | -0.85 | 0.39533 | -1.34 | 0.68 | -0.3121 | -0.576 | 286 | -0.0931 | -0.33 | ne | odbaceno |
| commodities:LOWVOL:4w:long | 74 | -0.3724 | -0.4446 | -0.506 | -0.86 | 0.38979 | -0.36 | -0.85 | -1.8473 | -0.6424 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:28d:long | 54 | -3.252 | -6.4782 | -4.6409 | -0.87 | 0.3843 | 1.18 | -3.05 | -19.798 | -3.522 | 28 | 1.4405 | 0.35 | ne | odbaceno |
| commodities:REV5:4w:short | 77 | -0.5488 | -0.2415 | -0.7477 | -0.88 | 0.37886 | -0.28 | -0.93 | 0.6256 | -0.8188 | 0 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:14d:long | 61 | -3.189 | -4.7041 | -4.6618 | -0.92 | 0.35757 | -0.71 | -0.58 | -13.7742 | -3.459 | 38 | 1.3691 | 0.46 | ne | odbaceno |
| stocks:VOLUP:4w:short | 76 | -1.7875 | 0.6651 | -1.9919 | -0.93 | 0.35237 | -0.74 | -0.79 | -5.4568 | -2.0575 | - | - | - | ne | odbaceno |
| stocks:MOM12_1:1w:short | 260 | -0.1906 | 0.1243 | -0.2228 | -0.94 | 0.34722 | -1.04 | -0.15 | 0.2007 | -0.4606 | - | - | - | ne | odbaceno |
| stocks:REV5:2w:long | 155 | -0.4013 | -0.8701 | -0.5337 | -0.96 | 0.33706 | 0.26 | -1.94 | -1.6169 | -0.6713 | - | - | - | ne | odbaceno |
| stocks:REV5:4w:short | 77 | -0.8642 | 0.1258 | -1.2169 | -0.96 | 0.33706 | 0.06 | -1.31 | 0.4032 | -1.1342 | - | - | - | ne | odbaceno |
| commodities:LOWVOL:2w:short | 149 | -0.3774 | -0.3715 | -0.4718 | -0.99 | 0.32217 | -0.5 | -0.88 | 0.842 | -0.6474 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:2w:short | 153 | -0.6075 | -0.1117 | -0.6914 | -1.03 | 0.30301 | -1.42 | 0.39 | -0.5051 | -0.8775 | - | - | - | ne | odbaceno |
| commodities:ATTN:2w:short | 149 | -0.31 | -0.5223 | -0.3759 | -1.11 | 0.267 | -1.81 | 0.22 | 1.1342 | -0.58 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:1w:long | 260 | -0.2196 | -0.2976 | -0.2529 | -1.18 | 0.238 | -1.95 | 0.1 | 0.0436 | -0.4896 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:short | 53 | -1.8973 | -0.6446 | -2.5284 | -1.2 | 0.23014 | -1.24 | -0.38 | -1.6627 | -2.1673 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:5d:long | 139 | -0.8106 | -1.272 | -1.038 | -1.21 | 0.22628 | -0.23 | -1.5 | -2.3362 | -1.0806 | - | - | - | ne | odbaceno |
| commodities:SPIKE_UP:10d:long | 35 | -1.449 | -3.2213 | -2.0425 | -1.24 | 0.21498 | -1.12 | -0.74 | -0.7305 | -1.719 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:4w:long | 74 | -0.7918 | -1.1915 | -0.9864 | -1.25 | 0.2113 | -2.47 | 0.76 | 1.5189 | -1.0618 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:long | 38 | -3.1619 | -6.0691 | -4.2905 | -1.3 | 0.1936 | -0.97 | -0.84 | -9.8891 | -3.4319 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:2w:long | 145 | -0.8607 | -0.6011 | -1.0959 | -1.31 | 0.1902 | -1.54 | -0.22 | -1.6883 | -1.1307 | 143 | 0.1967 | 0.31 | ne | odbaceno |
| stocks:VOLUP:2w:short | 153 | -0.6462 | -0.1409 | -0.7396 | -1.33 | 0.18352 | -1.02 | -0.88 | -1.9491 | -0.9162 | - | - | - | ne | odbaceno |
| commodities:HIGH52:2w:long | 129 | -0.3918 | -0.359 | -0.4819 | -1.37 | 0.17069 | -0.76 | -1.16 | -1.9513 | -0.6618 | 0 | None | None | ne | odbaceno |
| commodities:VOLUP:4w:long | 76 | -0.7505 | -0.8067 | -0.9121 | -1.37 | 0.17069 | -1.24 | -0.68 | -3.0323 | -1.0205 | 0 | None | None | ne | odbaceno |
| commodities:BRK20:4w:long | 76 | -0.6905 | -0.1651 | -0.7987 | -1.4 | 0.16151 | -0.97 | -1.0 | -4.4478 | -0.9605 | 0 | None | None | ne | odbaceno |
| crypto:ATTN:2w:long | 159 | -1.0134 | -0.903 | -1.2488 | -1.45 | 0.14706 | -0.63 | -1.66 | -6.1444 | -1.2834 | 159 | 1.3917 | 1.87 | ne | odbaceno |
| commodities:REV5:1w:long | 311 | -0.2182 | -0.1908 | -0.2622 | -1.45 | 0.14706 | -1.11 | -0.94 | -0.7897 | -0.4882 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:5d:short | 72 | -0.8688 | -0.8206 | -1.087 | -1.47 | 0.14156 | -0.96 | -1.1 | 0.9937 | -1.1388 | 0 | None | None | ne | odbaceno |
| commodities:REV5:2w:short | 155 | -0.4432 | -0.5687 | -0.5323 | -1.49 | 0.13622 | -1.55 | -0.53 | -0.5024 | -0.7132 | 0 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:7d:long | 117 | -2.7855 | -2.4549 | -3.3559 | -1.5 | 0.13361 | -1.88 | -0.17 | -13.2845 | -3.0555 | 76 | 1.8908 | 1.2 | ne | odbaceno |
| stocks:SPIKE_UP:5d:short | 178 | -1.1313 | -0.1237 | -1.2642 | -1.56 | 0.11876 | -1.66 | -0.32 | 2.2606 | -1.4013 | - | - | - | ne | odbaceno |
| commodities:BRK20:2w:short | 153 | -0.5056 | -0.2632 | -0.5706 | -1.56 | 0.11876 | -0.42 | -1.69 | -0.7405 | -0.7756 | 0 | None | None | ne | odbaceno |
| commodities:LOWVOL:2w:long | 149 | -0.329 | -0.2343 | -0.3777 | -1.56 | 0.11876 | -1.03 | -1.18 | -0.6518 | -0.599 | 0 | None | None | ne | odbaceno |
| crypto:VOLUP:1w:long | 323 | -0.6441 | -1.1141 | -0.8323 | -1.59 | 0.11183 | -0.31 | -2.96 | -1.4811 | -0.9141 | 323 | -0.3712 | -0.83 | ne | odbaceno |
| stocks:BRK20:4w:short | 76 | -3.4219 | -0.3163 | -3.6834 | -1.6 | 0.1096 | -1.42 | -0.86 | -2.4091 | -3.6919 | - | - | - | ne | odbaceno |
| commodities:VOLUP:2w:short | 153 | -0.5038 | -0.1704 | -0.587 | -1.62 | 0.10523 | 0.14 | -2.21 | -0.9335 | -0.7738 | 0 | None | None | ne | odbaceno |
| commodities:REV5:4w:long | 77 | -0.9493 | -1.4552 | -1.1119 | -1.67 | 0.09492 | -1.19 | -1.18 | -0.265 | -1.2193 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:1w:short | 300 | -0.2248 | -0.2535 | -0.262 | -1.67 | 0.09492 | -1.09 | -1.3 | -0.1252 | -0.4948 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:4w:short | 64 | -1.9433 | -1.0605 | -2.2773 | -1.69 | 0.09103 | -2.01 | -0.14 | 1.6344 | -2.2133 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:1w:long | 260 | -0.3063 | -0.2551 | -0.336 | -1.78 | 0.07508 | -0.96 | -1.68 | -0.9037 | -0.5763 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:1w:short | 308 | -0.395 | 0.2104 | -0.4295 | -1.82 | 0.06876 | -1.28 | -1.29 | -1.0461 | -0.665 | - | - | - | ne | odbaceno |
| stocks:HIGH52:2w:short | 129 | -0.9177 | -0.2232 | -1.0082 | -1.84 | 0.06577 | -2.39 | 0.15 | 1.2331 | -1.1877 | - | - | - | ne | odbaceno |
| crypto:VOLUP:4w:long | 80 | -2.2432 | -1.1287 | -2.803 | -1.86 | 0.06289 | -1.91 | -0.39 | -4.6403 | -2.5132 | 80 | -2.2618 | -1.14 | ne | odbaceno |
| commodities:MOM12_1:4w:short | 64 | -1.1347 | -1.1068 | -1.2966 | -1.87 | 0.06148 | -2.14 | -0.26 | -2.3562 | -1.4047 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:14d:long | 112 | -3.2518 | -3.0424 | -3.7226 | -1.92 | 0.05486 | -0.43 | -2.55 | -7.399 | -3.5218 | 74 | 0.5716 | 0.25 | ne | odbaceno |
| stocks:HIGH52:1w:short | 260 | -0.46 | -0.1392 | -0.4875 | -1.99 | 0.04659 | -2.58 | 0.03 | 0.2134 | -0.73 | - | - | - | ne | odbaceno |
| crypto:ATTN:1w:long | 319 | -0.8395 | -1.1507 | -0.9628 | -2.09 | 0.03662 | -1.45 | -1.71 | -1.7539 | -1.1095 | 319 | 0.3073 | 0.69 | ne | odbaceno |
| commodities:HIGH_BRK:10d:short | 24 | -2.7096 | -1.5853 | -3.2461 | -2.09 | None | -1.91 | -0.86 | -1.3889 | -2.9796 | 0 | None | None | ne | premalo |
| commodities:HIGH_BRK:20d:short | 13 | -5.8368 | -2.7848 | -6.7604 | -2.09 | None | -1.35 | -1.56 | -2.1703 | -6.1068 | 0 | None | None | ne | premalo |
| commodities:VOLUP:2w:long | 153 | -0.5609 | -0.5897 | -0.6332 | -2.11 | 0.03486 | -1.33 | -1.67 | -1.0291 | -0.8309 | 0 | None | None | ne | odbaceno |
| stocks:LOWVOL:4w:short | 74 | -3.1447 | -1.5384 | -3.4984 | -2.14 | 0.03235 | -0.9 | -2.07 | -4.3076 | -3.4147 | - | - | - | ne | odbaceno |
| commodities:REV5:1w:short | 311 | -0.335 | -0.3074 | -0.365 | -2.14 | 0.03235 | -1.88 | -1.09 | -0.6796 | -0.605 | 0 | None | None | ne | odbaceno |
| commodities:LOWVOL:1w:short | 300 | -0.4137 | -0.2677 | -0.4409 | -2.19 | 0.02852 | -1.46 | -1.64 | -0.4111 | -0.6837 | 0 | None | None | da | odbaceno |
| commodities:MOM12_1:2w:short | 129 | -0.6454 | -0.6018 | -0.7418 | -2.21 | 0.02711 | -3.11 | -0.04 | -0.7428 | -0.9154 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:4w:long | 74 | -1.7766 | -0.5485 | -1.9545 | -2.24 | 0.02509 | -0.83 | -2.32 | -3.8932 | -2.0466 | - | - | - | da | odbaceno |
| commodities:HIGH52:4w:short | 64 | -1.3647 | -1.2699 | -1.5344 | -2.25 | 0.02445 | -2.01 | -1.03 | -1.3888 | -1.6347 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:4w:short | 76 | -1.399 | -0.8652 | -1.5652 | -2.28 | 0.02261 | -2.46 | -0.84 | -3.6784 | -1.669 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_UP:7d:long | 227 | -2.2787 | -3.6381 | -2.6478 | -2.29 | 0.02202 | -0.23 | -4.21 | -6.4473 | -2.5487 | 157 | -0.8035 | -0.55 | da | odbaceno |
| stocks:REV5:2w:short | 155 | -1.3012 | -0.4543 | -1.3917 | -2.35 | 0.01877 | -1.54 | -2.02 | -0.0889 | -1.5712 | - | - | - | da | odbaceno |
| stocks:VOLUP:1w:short | 308 | -0.4394 | -0.105 | -0.4724 | -2.39 | 0.01685 | -2.11 | -1.16 | -1.149 | -0.7094 | - | - | - | da | odbaceno |
| commodities:ATTN:1w:long | 300 | -0.2791 | -0.2992 | -0.2995 | -2.41 | 0.01595 | -2.08 | -1.31 | -0.0987 | -0.5491 | 0 | None | None | da | odbaceno |
| stocks:ATTN:4w:short | 74 | -1.5177 | -1.2599 | -1.6674 | -2.44 | 0.01469 | -1.16 | -2.38 | -0.1885 | -1.7877 | - | - | - | da | odbaceno |
| crypto:REV5:4w:long | 80 | -3.0006 | -2.5461 | -3.401 | -2.48 | 0.01314 | -0.98 | -3.08 | -3.4586 | -3.2706 | 80 | 0.1585 | 0.13 | da | odbaceno |
| stocks:REV5:1w:short | 311 | -0.5579 | -0.3127 | -0.5928 | -2.54 | 0.01109 | -2.12 | -1.43 | -0.0775 | -0.8279 | - | - | - | da | odbaceno |
| stocks:LOWVOL:2w:short | 149 | -1.9737 | -0.6449 | -2.0973 | -2.79 | 0.00527 | -1.74 | -2.38 | -2.0247 | -2.2437 | - | - | - | da | odbaceno |
| crypto:MOM12_1:1w:long | 291 | -0.8847 | -0.9698 | -0.9382 | -2.79 | 0.00527 | -2.14 | -1.82 | -1.75 | -1.1547 | 286 | -0.1657 | -0.58 | da | odbaceno |
| crypto:ATTN:4w:long | 79 | -3.3897 | -3.0239 | -3.7526 | -2.79 | 0.00527 | -2.56 | -1.31 | -11.5316 | -3.6597 | 79 | 0.7523 | 0.5 | da | odbaceno |
| commodities:BRK20:2w:long | 153 | -0.6857 | -0.7177 | -0.7442 | -2.8 | 0.00511 | -1.31 | -2.8 | -1.8156 | -0.9557 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:1w:short | 308 | -0.3781 | -0.4249 | -0.4045 | -2.81 | 0.00495 | -3.17 | -0.64 | 0.3675 | -0.6481 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:7d:long | 129 | -5.8356 | -7.6539 | -6.8416 | -2.89 | 0.00385 | -1.01 | -3.08 | -11.7888 | -6.1056 | 54 | 2.0272 | 0.59 | da | odbaceno |
| stocks:LOWVOL:1w:long | 300 | -0.508 | -0.2172 | -0.5365 | -2.91 | 0.00361 | -1.51 | -2.59 | -1.0361 | -0.778 | - | - | - | da | odbaceno |
| commodities:BRK20:1w:short | 308 | -0.4329 | -0.3532 | -0.4637 | -2.93 | 0.00339 | -2.37 | -1.78 | -0.1033 | -0.7029 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:2w:long | 149 | -1.0586 | -0.7005 | -1.1292 | -2.94 | 0.00328 | -1.3 | -2.86 | -2.4359 | -1.3286 | - | - | - | da | odbaceno |
| commodities:HIGH52:1w:long | 260 | -0.3823 | -0.2022 | -0.4048 | -2.96 | 0.00308 | -2.33 | -1.83 | -0.8876 | -0.6523 | 0 | None | None | da | odbaceno |
| stocks:SPIKE_UP:10d:short | 86 | -6.6391 | -0.5063 | -6.944 | -2.99 | 0.00279 | -2.52 | -1.6 | 0.0585 | -6.9091 | - | - | - | da | odbaceno |
| commodities:MOM12_1:1w:short | 260 | -0.4651 | -0.347 | -0.4995 | -3.07 | 0.00214 | -3.19 | -1.0 | -0.3845 | -0.7351 | 0 | None | None | da | odbaceno |
| commodities:SPIKE_UP:5d:long | 71 | -1.5342 | -2.045 | -1.7991 | -3.08 | 0.00207 | -1.69 | -2.92 | -3.0622 | -1.8042 | 0 | None | None | da | odbaceno |
| commodities:BRK20:1w:long | 308 | -0.4258 | -0.2883 | -0.4551 | -3.15 | 0.00163 | -2.68 | -1.76 | -0.2368 | -0.6958 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:1w:short | 300 | -0.9795 | -0.2405 | -1.0267 | -3.21 | 0.00133 | -2.02 | -2.61 | -0.973 | -1.2495 | - | - | - | da | odbaceno |
| commodities:LOWVOL:1w:long | 300 | -0.3343 | -0.2804 | -0.3516 | -3.3 | 0.00097 | -2.72 | -1.86 | -0.4644 | -0.6043 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:1w:long | 308 | -0.4716 | -0.3943 | -0.5017 | -3.55 | 0.00039 | -3.23 | -1.65 | -0.301 | -0.7416 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:28d:long | 37 | -19.2527 | -23.0738 | -22.506 | -3.66 | 0.00025 | -1.76 | -4.76 | -31.8519 | -19.5227 | 11 | -1.1242 | -0.42 | da | odbaceno |
| crypto:REV5:2w:long | 161 | -2.0024 | -2.3483 | -2.1844 | -3.73 | 0.00019 | -2.2 | -3.7 | -2.8177 | -2.2724 | 161 | -0.8948 | -1.58 | da | odbaceno |
| crypto:SPIKE_DN:14d:long | 69 | -11.5798 | -13.5256 | -12.4866 | -4.27 | 2e-05 | -1.45 | -6.0 | -24.5574 | -11.8498 | 28 | -5.7996 | -1.57 | da | odbaceno |
| commodities:HIGH52:2w:short | 129 | -1.4322 | -1.4189 | -1.5052 | -4.38 | 1e-05 | -3.42 | -2.72 | -1.0748 | -1.7022 | 0 | None | None | da | odbaceno |
| commodities:HIGH52:1w:short | 260 | -0.7379 | -0.7807 | -0.7647 | -4.67 | 0.0 | -3.78 | -2.76 | -1.0617 | -1.0079 | 0 | None | None | da | odbaceno |
| crypto:REV5:1w:long | 323 | -1.437 | -1.5817 | -1.5144 | -5.31 | 0.0 | -4.1 | -3.45 | -2.3733 | -1.707 | 323 | -0.9606 | -3.25 | da | odbaceno |

## Opisni slucaj: GME (vlasnikov ulaz 2026-10-03)

Gde je GME po svakoj rang-porodici na poslednjoj sveci pre ulaza (2026-10-02). Percentil 1.0 = najvise u univerzumu (od 44 clanova).

| porodica | ocena | percentil |
|---|---|---|
| MOM12_1 | -0.3149 | 0.116 |
| HIGH52 | 0.9074 | 0.698 |
| REV5 | -0.056 | 0.14 |
| VOLUP | 0.0326 | 0.767 |
| BRK20 | -0.0128 | 0.628 |
| LOWVOL | -0.0261 | 0.721 |
| ATTN | 1.4911 | 0.953 |

Dogadjaji u poslednjih 10 svecâ: nijedan.
