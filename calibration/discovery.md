# Lovac: studija na sirem univerzumu (2026-10-11)

Univerzumi: stocks 44 instrumenata (2020-10-12 do 2026-10-09); crypto 413 instrumenata (2020-06-25 do 2026-10-10); commodities 20 instrumenata (2020-10-12 do 2026-10-09).
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
| crypto:BRK20:2w:short | 161 | 2.9764 | 3.4346 | 2.8328 | 5.12 | 0.0 | 2.72 | 5.08 | 5.399 | 2.7064 | 161 | 0.6279 | 0.81 | da | nagovestaj |
| crypto:BRK20:1w:short | 323 | 1.5032 | 1.6978 | 1.4267 | 4.9 | 0.0 | 3.01 | 4.43 | 2.839 | 1.2332 | 323 | 0.4647 | 1.32 | da | kandidat |
| crypto:LOWVOL:2w:short | 159 | 3.5754 | 3.4955 | 3.3586 | 4.89 | 0.0 | 2.94 | 4.24 | 10.3796 | 3.3054 | 159 | 0.015 | 0.02 | da | nagovestaj |
| crypto:BRK20:4w:short | 80 | 5.2193 | 4.3084 | 4.7663 | 4.52 | 1e-05 | 2.12 | 4.92 | 8.004 | 4.9493 | 80 | 1.7164 | 1.28 | da | kandidat |
| crypto:SPIKE_DN:14d:short | 69 | 10.9198 | 12.8656 | 9.9636 | 4.03 | 6e-05 | 1.27 | 5.81 | 23.8974 | 10.6498 | 28 | 5.3446 | 1.49 | da | kandidat |
| crypto:LOWVOL:1w:short | 318 | 1.4342 | 1.6011 | 1.3659 | 3.6 | 0.00032 | 1.93 | 3.85 | 4.4677 | 1.1642 | 318 | -0.1143 | -0.26 | da | nagovestaj |
| crypto:SPIKE_DN:28d:short | 37 | 18.5927 | 22.4138 | 17.1764 | 3.53 | 0.00042 | 1.67 | 4.64 | 31.1919 | 18.3227 | 11 | 0.6494 | 0.23 | da | nagovestaj |
| crypto:BRK20:2w:long | 161 | 1.8113 | 1.3302 | 1.5847 | 3.12 | 0.00181 | 2.86 | 1.32 | 0.8359 | 1.5413 | 161 | 0.7937 | 1.0 | da | kandidat |
| crypto:LOWVOL:4w:short | 79 | 4.4454 | 4.7566 | 3.94 | 3.02 | 0.00253 | 1.24 | 3.87 | 14.6478 | 4.1754 | 79 | -2.1023 | -0.73 | da | nagovestaj |
| crypto:LOWVOL:2w:long | 159 | 1.3611 | 1.5536 | 1.2512 | 2.95 | 0.00318 | 1.07 | 4.04 | 2.2205 | 1.0911 | 159 | 0.0001 | 0.0 | da | nagovestaj |
| stocks:SPIKE_UP:10d:long | 86 | 6.1791 | 0.0463 | 4.8698 | 2.78 | 0.00544 | 2.37 | 1.44 | -0.5185 | 5.9091 | - | - | - | da | nagovestaj |
| crypto:SPIKE_DN:7d:short | 129 | 5.1756 | 6.9939 | 4.6578 | 2.56 | 0.01047 | 0.72 | 2.9 | 11.1288 | 4.9056 | 53 | -2.7023 | -0.78 | da | nagovestaj |
| crypto:LOWVOL:4w:long | 79 | 3.0496 | 4.1021 | 2.7381 | 2.48 | 0.01314 | 0.76 | 4.19 | 2.5473 | 2.7796 | 79 | 0.5563 | 0.31 | da | nagovestaj |
| crypto:LOWVOL:1w:long | 318 | 0.5621 | 0.5828 | 0.4805 | 2.05 | 0.04036 | 0.97 | 2.2 | 0.7376 | 0.2921 | 318 | -0.1806 | -0.54 | ne | nagovestaj |
| crypto:VOLUP:4w:short | 80 | 1.9549 | 1.0824 | 1.6254 | 1.82 | 0.06876 | 1.17 | 1.63 | 1.2785 | 1.6849 | 80 | -0.7577 | -0.49 | ne | odbaceno |
| commodities:HIGH_BRK:20d:long | 13 | 5.0768 | 2.0248 | 2.9489 | 1.81 | None | 1.18 | 1.35 | 1.4103 | 4.8068 | 0 | None | None | ne | premalo |
| crypto:HIGH52:2w:short | 145 | 1.0769 | 0.9505 | 0.8554 | 1.79 | 0.07345 | 1.5 | 0.96 | 1.1174 | 0.8069 | 143 | 0.1374 | 0.21 | ne | odbaceno |
| crypto:SPIKE_UP:7d:short | 227 | 1.6187 | 2.9781 | 1.4349 | 1.63 | 0.1031 | -0.24 | 3.68 | 6.8476 | 1.3487 | 155 | 0.1851 | 0.13 | ne | odbaceno |
| commodities:SPIKE_UP:5d:short | 71 | 0.7684 | 1.285 | 0.6418 | 1.54 | 0.12356 | 0.57 | 1.83 | 2.2727 | 0.4984 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:14d:short | 112 | 2.5918 | 2.3824 | 2.0957 | 1.53 | 0.12602 | 0.13 | 2.3 | 6.739 | 2.3218 | 71 | -1.3529 | -0.57 | ne | odbaceno |
| commodities:HIGH_BRK:10d:long | 24 | 1.9487 | 0.8253 | 1.1922 | 1.5 | None | 1.52 | 0.34 | 0.6237 | 1.6787 | 0 | None | None | ne | premalo |
| stocks:MOM12_1:4w:long | 64 | 1.233 | 0.7364 | 0.8561 | 1.37 | 0.17069 | -0.66 | 2.55 | 2.4059 | 0.963 | - | - | - | ne | odbaceno |
| crypto:VOLUP:2w:short | 161 | 0.7985 | 0.9294 | 0.6146 | 1.37 | 0.17069 | 1.38 | 0.43 | 2.6303 | 0.5285 | 161 | -0.2267 | -0.31 | ne | odbaceno |
| crypto:BRK20:1w:long | 323 | 0.5035 | 0.4 | 0.3623 | 1.34 | 0.18025 | 1.25 | 0.53 | -0.4972 | 0.2335 | 323 | 0.2439 | 0.6 | ne | odbaceno |
| crypto:HIGH52:2w:long | 145 | 0.7913 | 0.4797 | 0.5869 | 1.3 | 0.1936 | 1.51 | 0.05 | -1.8479 | 0.5213 | 143 | 0.2117 | 0.31 | ne | odbaceno |
| stocks:VOLUP:4w:long | 76 | 1.2704 | 0.8939 | 0.7591 | 1.27 | 0.20408 | 0.66 | 1.19 | -0.0799 | 1.0004 | - | - | - | ne | odbaceno |
| stocks:ATTN:2w:long | 149 | 0.6328 | -0.3237 | 0.2715 | 1.25 | 0.2113 | 0.86 | 1.11 | 0.3472 | 0.3628 | - | - | - | ne | odbaceno |
| crypto:ATTN:2w:short | 159 | 0.6207 | 0.2006 | 0.4841 | 1.23 | 0.2187 | 0.43 | 1.96 | 0.3965 | 0.3507 | 159 | 0.2352 | 0.38 | ne | odbaceno |
| stocks:VOLUP:2w:long | 153 | 0.4462 | -0.3376 | 0.3247 | 1.19 | 0.23405 | 0.82 | 0.86 | 1.0869 | 0.1762 | - | - | - | ne | odbaceno |
| stocks:MOM12_1:2w:long | 129 | 0.5197 | 0.2242 | 0.3727 | 1.13 | 0.25848 | -0.95 | 2.34 | 1.4287 | 0.2497 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:short | 38 | 2.7019 | 5.6091 | 2.0408 | 1.11 | 0.267 | 0.81 | 0.73 | 9.4291 | 2.4319 | - | - | - | ne | odbaceno |
| crypto:HIGH52:1w:short | 291 | 0.3423 | 0.6462 | 0.2534 | 1.1 | 0.27133 | 1.6 | -0.31 | -0.2325 | 0.0723 | 286 | -0.1476 | -0.48 | ne | odbaceno |
| crypto:BRK20:4w:long | 80 | 1.2084 | 2.7674 | 0.8172 | 0.98 | 0.32709 | 0.09 | 1.8 | -1.2494 | 0.9384 | 80 | -0.5642 | -0.32 | ne | odbaceno |
| crypto:MOM12_1:4w:short | 72 | 1.1704 | 2.9601 | 0.8961 | 0.97 | 0.33205 | -0.07 | 2.31 | 4.0695 | 0.9004 | 71 | 1.0047 | 0.91 | ne | odbaceno |
| stocks:SPIKE_UP:5d:long | 178 | 0.6713 | -0.3363 | 0.4427 | 0.92 | 0.35757 | 1.2 | -0.13 | -2.7206 | 0.4013 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:long | 53 | 1.4373 | 0.1846 | 0.7096 | 0.91 | 0.36282 | 1.02 | 0.19 | 1.2027 | 1.1673 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:14d:short | 61 | 2.529 | 4.0441 | 1.2704 | 0.73 | 0.46539 | 0.56 | 0.46 | 13.1142 | 2.259 | 36 | -2.457 | -0.79 | ne | odbaceno |
| crypto:ATTN:1w:short | 319 | 0.2019 | 0.3089 | 0.1416 | 0.71 | 0.4777 | -0.26 | 2.09 | 0.2494 | -0.0681 | 319 | 0.0511 | 0.14 | ne | odbaceno |
| crypto:REV5:4w:short | 80 | 1.0772 | 1.242 | 0.6081 | 0.69 | 0.49019 | 1.09 | -0.43 | 6.2689 | 0.8072 | 80 | -1.598 | -0.72 | ne | odbaceno |
| crypto:SPIKE_UP:28d:short | 54 | 2.592 | 5.8182 | 0.8616 | 0.69 | 0.49019 | -1.32 | 2.92 | 19.138 | 2.322 | 27 | 0.0743 | 0.02 | ne | odbaceno |
| crypto:HIGH_BRK:7d:short | 118 | 1.2303 | 1.6309 | 0.643 | 0.6 | 0.54851 | 0.87 | -0.15 | 12.6245 | 0.9603 | 70 | -3.5223 | -2.07 | ne | odbaceno |
| commodities:SPIKE_UP:10d:short | 35 | 0.689 | 2.4613 | 0.3705 | 0.59 | 0.55519 | 0.39 | 0.44 | -0.0295 | 0.419 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_DN:5d:short | 139 | 0.3506 | 0.812 | 0.061 | 0.52 | 0.60306 | -0.35 | 1.1 | 1.8762 | 0.0806 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:10d:long | 67 | 0.8324 | 0.0197 | -0.4483 | 0.41 | 0.68181 | 0.71 | -0.52 | -6.3599 | 0.5624 | - | - | - | ne | odbaceno |
| crypto:HIGH52:4w:short | 72 | 0.5574 | 2.2465 | 0.3728 | 0.41 | 0.68181 | -0.16 | 1.46 | 1.3108 | 0.2874 | 71 | 0.5512 | 0.46 | ne | odbaceno |
| crypto:VOLUP:1w:short | 323 | 0.1214 | 0.503 | 0.0482 | 0.41 | 0.68181 | 0.88 | -0.49 | 0.8388 | -0.1486 | 323 | -0.417 | -1.19 | ne | odbaceno |
| stocks:MOM12_1:1w:long | 260 | 0.081 | -0.2157 | 0.0311 | 0.35 | 0.72634 | -0.93 | 1.25 | 0.4266 | -0.189 | - | - | - | ne | odbaceno |
| crypto:HIGH52:4w:long | 72 | 0.4573 | 0.4927 | -0.1455 | 0.34 | 0.73386 | 0.35 | 0.08 | -3.6514 | 0.1873 | 71 | 0.3116 | 0.18 | ne | odbaceno |
| crypto:MOM12_1:2w:short | 145 | 0.2356 | 1.2706 | 0.0596 | 0.33 | 0.7414 | -0.58 | 1.8 | 0.8365 | -0.0344 | 143 | 0.0691 | 0.12 | ne | odbaceno |
| commodities:ATTN:4w:short | 74 | 0.164 | -0.4157 | -0.0926 | 0.3 | 0.76418 | -0.09 | 0.49 | 3.7603 | -0.106 | 0 | None | None | ne | odbaceno |
| commodities:BRK20:4w:short | 76 | 0.1771 | 0.0179 | -0.03 | 0.28 | 0.77948 | 1.29 | -0.67 | 0.2918 | -0.0929 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:1w:long | 308 | 0.0443 | -0.1448 | -0.0323 | 0.24 | 0.81033 | 0.42 | -0.11 | 0.0413 | -0.2257 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:28d:short | 27 | 1.809 | 6.4546 | -0.4864 | 0.22 | None | 0.15 | 0.15 | 23.5027 | 1.539 | 15 | -4.3479 | -0.59 | ne | premalo |
| stocks:ATTN:1w:long | 300 | 0.0349 | -0.1543 | -0.0584 | 0.18 | 0.85715 | -0.22 | 0.67 | 0.1477 | -0.2351 | - | - | - | ne | odbaceno |
| commodities:SPIKE_DN:5d:long | 72 | 0.1091 | 0.0606 | -0.0807 | 0.18 | 0.85715 | -0.14 | 0.39 | -1.7522 | -0.1609 | 0 | None | None | ne | odbaceno |
| crypto:HIGH52:1w:long | 291 | 0.068 | -0.1524 | -0.1979 | 0.16 | 0.87288 | 0.59 | -0.85 | -1.6374 | -0.202 | 286 | -0.0476 | -0.14 | ne | odbaceno |
| crypto:MOM12_1:4w:long | 72 | 0.1827 | -1.5434 | -0.327 | 0.13 | 0.89657 | 0.43 | -0.53 | -0.6009 | -0.0873 | 71 | 1.2271 | 0.77 | ne | odbaceno |
| stocks:VOLUP:1w:long | 308 | 0.0241 | -0.157 | -0.0522 | 0.12 | 0.90448 | 0.29 | -0.17 | -0.1525 | -0.2459 | - | - | - | ne | odbaceno |
| crypto:ATTN:4w:short | 79 | 0.1201 | 0.8914 | -0.1562 | 0.12 | 0.90448 | -0.67 | 1.68 | 0.9923 | -0.1499 | 79 | 0.8859 | 0.5 | ne | odbaceno |
| stocks:REV5:4w:long | 77 | 0.204 | -1.0362 | -1.7632 | 0.1 | 0.92034 | 0.63 | -1.88 | -4.5457 | -0.066 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:4w:long | 64 | 0.0627 | 0.4103 | -0.1461 | 0.08 | 0.93624 | -0.05 | 0.17 | -2.8153 | -0.2073 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:4w:long | 76 | 0.0326 | 1.1246 | -0.1788 | 0.04 | 0.96809 | -0.28 | 0.39 | 0.4412 | -0.2374 | - | - | - | ne | odbaceno |
| commodities:REV5:2w:long | 155 | 0.007 | 0.0608 | -0.077 | 0.02 | 0.98404 | -0.72 | 0.77 | -0.4597 | -0.263 | 0 | None | None | ne | odbaceno |
| commodities:LOWVOL:4w:short | 74 | 0.0016 | 0.4913 | -0.2569 | 0.0 | 1.0 | 0.31 | -0.29 | 1.4522 | -0.2684 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:20d:short | 45 | -0.1229 | 1.6821 | -0.9813 | -0.04 | 0.96809 | -0.6 | 0.88 | 8.9655 | -0.3929 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:20d:long | 27 | -0.1387 | -0.8921 | -1.3524 | -0.05 | None | 0.04 | -0.22 | 1.8999 | -0.4087 | - | - | - | ne | premalo |
| stocks:BRK20:2w:long | 153 | -0.0176 | -0.2706 | -0.0883 | -0.06 | 0.95216 | -0.99 | 0.78 | -0.2208 | -0.2876 | - | - | - | ne | odbaceno |
| stocks:SPIKE_UP:20d:long | 45 | -0.3371 | -2.1421 | -2.0031 | -0.11 | 0.91241 | 0.5 | -0.99 | -9.4255 | -0.6071 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:20d:short | 27 | -0.3213 | 0.4321 | -1.9916 | -0.11 | None | -0.14 | 0.05 | -2.3599 | -0.5913 | - | - | - | ne | premalo |
| commodities:SPIKE_UP:20d:short | 21 | -0.2964 | 1.5262 | -0.8578 | -0.12 | None | 1.31 | -0.79 | -2.1662 | -0.5664 | 0 | None | None | ne | premalo |
| commodities:SPIKE_DN:20d:short | 14 | -0.2824 | 0.8551 | -1.3234 | -0.14 | None | -0.3 | 0.72 | 1.3198 | -0.5524 | 0 | None | None | ne | premalo |
| crypto:REV5:2w:short | 161 | -0.1132 | 0.2227 | -0.2853 | -0.18 | 0.85715 | -0.71 | 0.79 | 3.5431 | -0.3832 | 161 | -1.2111 | -1.54 | ne | odbaceno |
| commodities:SPIKE_UP:20d:long | 21 | -0.4636 | -2.2862 | -2.5735 | -0.19 | None | -1.71 | 0.64 | 1.4062 | -0.7336 | 0 | None | None | ne | premalo |
| stocks:MOM12_1:4w:short | 64 | -0.1962 | 0.244 | -0.4092 | -0.22 | 0.82587 | -0.64 | 0.64 | 1.4996 | -0.4662 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:5d:short | 109 | -0.1684 | 0.2965 | -0.513 | -0.22 | 0.82587 | -0.31 | 0.02 | 0.2999 | -0.4384 | - | - | - | ne | odbaceno |
| crypto:REV5:1w:short | 323 | -0.0898 | 0.2969 | -0.1548 | -0.23 | 0.81809 | -0.82 | 1.26 | 1.2624 | -0.3598 | 323 | -0.8298 | -1.84 | ne | odbaceno |
| stocks:HIGH52:4w:long | 64 | -0.1757 | -0.1934 | -0.453 | -0.24 | 0.81033 | -0.95 | 0.45 | 1.981 | -0.4457 | - | - | - | ne | odbaceno |
| commodities:SPIKE_DN:20d:long | 14 | -0.4776 | -1.6151 | -1.833 | -0.24 | None | 0.09 | -1.44 | -2.0798 | -0.7476 | 0 | None | None | ne | premalo |
| commodities:SPIKE_DN:10d:short | 37 | -0.2994 | 0.3949 | -1.0546 | -0.27 | 0.78716 | -1.05 | 0.56 | -1.1201 | -0.5694 | 0 | None | None | ne | odbaceno |
| crypto:VOLUP:2w:long | 161 | -0.2156 | -1.3223 | -0.709 | -0.28 | 0.77948 | 0.38 | -1.3 | -0.6118 | -0.4856 | 161 | 0.4723 | 0.6 | ne | odbaceno |
| crypto:HIGH_BRK:28d:long | 27 | -2.469 | -7.1146 | -7.9446 | -0.3 | None | -0.22 | -0.2 | -24.1627 | -2.739 | 15 | 3.6879 | 0.5 | ne | premalo |
| stocks:HIGH_BRK:5d:long | 109 | -0.2916 | -0.7565 | -0.5843 | -0.38 | 0.70395 | -0.17 | -0.38 | -0.7599 | -0.5616 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:short | 50 | -0.2726 | -0.3989 | -0.6397 | -0.38 | 0.70395 | -1.15 | 0.64 | 0.4767 | -0.5426 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:10d:long | 37 | -0.4606 | -1.1549 | -0.8895 | -0.41 | 0.68181 | 0.44 | -0.92 | 0.3601 | -0.7306 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:4w:long | 64 | -0.2593 | 0.5698 | -0.5166 | -0.44 | 0.65994 | 0.66 | -1.22 | -6.208 | -0.5293 | 0 | None | None | ne | odbaceno |
| stocks:REV5:1w:long | 311 | -0.1059 | -0.4578 | -0.1659 | -0.56 | 0.57548 | -0.32 | -0.49 | 0.0315 | -0.3759 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:2w:long | 129 | -0.2204 | 0.2037 | -0.2934 | -0.59 | 0.55519 | -0.52 | -0.28 | -1.3036 | -0.4904 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:2w:long | 149 | -0.1421 | 0.0313 | -0.1885 | -0.59 | 0.55519 | -1.21 | 0.41 | 1.1323 | -0.4121 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:2w:short | 149 | -0.2015 | -0.2451 | -0.2645 | -0.61 | 0.54186 | 0.98 | -2.42 | -0.2422 | -0.4715 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:10d:short | 67 | -1.2924 | -0.4797 | -1.8578 | -0.63 | 0.52869 | -0.86 | 0.32 | 5.8999 | -1.5624 | - | - | - | ne | odbaceno |
| stocks:HIGH52:2w:long | 129 | -0.2253 | -0.1537 | -0.3167 | -0.64 | 0.52217 | -1.67 | 0.64 | 0.5468 | -0.4953 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:long | 50 | -0.4874 | -0.3611 | -0.8464 | -0.69 | 0.49019 | 0.25 | -1.26 | -1.2367 | -0.7574 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:2w:short | 129 | -0.2908 | -0.6588 | -0.3793 | -0.7 | 0.48393 | -1.15 | 0.42 | 1.1697 | -0.5608 | - | - | - | ne | odbaceno |
| commodities:ATTN:4w:long | 74 | -0.3416 | -0.4571 | -0.4588 | -0.72 | 0.47152 | -0.46 | -0.55 | 0.5758 | -0.6116 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:1w:short | 300 | -0.1335 | 0.1094 | -0.1619 | -0.82 | 0.41222 | -0.57 | -0.64 | 0.2901 | -0.4035 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:1w:short | 291 | -0.306 | 0.1861 | -0.3568 | -0.85 | 0.39533 | -1.34 | 0.68 | -0.3121 | -0.576 | 286 | -0.1448 | -0.52 | ne | odbaceno |
| commodities:LOWVOL:4w:long | 74 | -0.3721 | -0.4446 | -0.5057 | -0.86 | 0.38979 | -0.36 | -0.85 | -1.845 | -0.6421 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:28d:long | 54 | -3.252 | -6.4782 | -4.6409 | -0.87 | 0.3843 | 1.18 | -3.05 | -19.798 | -3.522 | 27 | -0.7343 | -0.19 | ne | odbaceno |
| commodities:REV5:4w:short | 77 | -0.549 | -0.2415 | -0.748 | -0.88 | 0.37886 | -0.28 | -0.93 | 0.6233 | -0.819 | 0 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:7d:long | 118 | -1.8903 | -2.2909 | -2.7855 | -0.92 | 0.35757 | -1.11 | -0.07 | -13.2845 | -2.1603 | 70 | 2.8623 | 1.68 | ne | odbaceno |
| crypto:HIGH_BRK:14d:long | 61 | -3.189 | -4.7041 | -4.6618 | -0.92 | 0.35757 | -0.71 | -0.58 | -13.7742 | -3.459 | 36 | 1.797 | 0.58 | ne | odbaceno |
| stocks:VOLUP:4w:short | 76 | -1.7875 | 0.6651 | -1.9919 | -0.93 | 0.35237 | -0.74 | -0.79 | -5.4568 | -2.0575 | - | - | - | ne | odbaceno |
| stocks:MOM12_1:1w:short | 260 | -0.1906 | 0.1243 | -0.2228 | -0.94 | 0.34722 | -1.04 | -0.15 | 0.2007 | -0.4606 | - | - | - | ne | odbaceno |
| stocks:REV5:2w:long | 155 | -0.4013 | -0.8701 | -0.5337 | -0.96 | 0.33706 | 0.26 | -1.94 | -1.6169 | -0.6713 | - | - | - | ne | odbaceno |
| stocks:REV5:4w:short | 77 | -0.8642 | 0.1258 | -1.2169 | -0.96 | 0.33706 | 0.06 | -1.31 | 0.4032 | -1.1342 | - | - | - | ne | odbaceno |
| commodities:LOWVOL:2w:short | 149 | -0.3783 | -0.3715 | -0.4727 | -0.99 | 0.32217 | -0.5 | -0.88 | 0.8349 | -0.6483 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:2w:short | 153 | -0.6075 | -0.1117 | -0.6914 | -1.03 | 0.30301 | -1.42 | 0.39 | -0.5051 | -0.8775 | - | - | - | ne | odbaceno |
| commodities:ATTN:2w:short | 149 | -0.3109 | -0.5223 | -0.3768 | -1.11 | 0.267 | -1.81 | 0.22 | 1.1271 | -0.5809 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:1w:long | 260 | -0.2196 | -0.2976 | -0.2529 | -1.18 | 0.238 | -1.95 | 0.1 | 0.0436 | -0.4896 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:short | 53 | -1.8973 | -0.6446 | -2.5284 | -1.2 | 0.23014 | -1.24 | -0.38 | -1.6627 | -2.1673 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:5d:long | 139 | -0.8106 | -1.272 | -1.038 | -1.21 | 0.22628 | -0.23 | -1.5 | -2.3362 | -1.0806 | - | - | - | ne | odbaceno |
| commodities:SPIKE_UP:10d:long | 35 | -1.449 | -3.2213 | -2.0425 | -1.24 | 0.21498 | -1.12 | -0.74 | -0.7305 | -1.719 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:4w:long | 74 | -0.7918 | -1.1915 | -0.9864 | -1.25 | 0.2113 | -2.47 | 0.76 | 1.5189 | -1.0618 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:long | 38 | -3.1619 | -6.0691 | -4.2905 | -1.3 | 0.1936 | -0.97 | -0.84 | -9.8891 | -3.4319 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:2w:long | 145 | -0.8607 | -0.6011 | -1.0959 | -1.31 | 0.1902 | -1.54 | -0.22 | -1.6883 | -1.1307 | 143 | 0.2463 | 0.38 | ne | odbaceno |
| stocks:VOLUP:2w:short | 153 | -0.6462 | -0.1409 | -0.7396 | -1.33 | 0.18352 | -1.02 | -0.88 | -1.9491 | -0.9162 | - | - | - | ne | odbaceno |
| commodities:HIGH52:2w:long | 129 | -0.3908 | -0.359 | -0.4809 | -1.36 | 0.17383 | -0.76 | -1.16 | -1.9442 | -0.6608 | 0 | None | None | ne | odbaceno |
| commodities:VOLUP:4w:long | 76 | -0.7502 | -0.8067 | -0.9119 | -1.37 | 0.17069 | -1.24 | -0.68 | -3.03 | -1.0202 | 0 | None | None | ne | odbaceno |
| commodities:BRK20:4w:long | 76 | -0.6903 | -0.1651 | -0.7984 | -1.4 | 0.16151 | -0.97 | -1.0 | -4.4455 | -0.9603 | 0 | None | None | ne | odbaceno |
| commodities:REV5:1w:long | 311 | -0.2158 | -0.1908 | -0.2598 | -1.43 | 0.15272 | -1.11 | -0.92 | -0.7706 | -0.4858 | 0 | None | None | ne | odbaceno |
| crypto:ATTN:2w:long | 159 | -1.0134 | -0.903 | -1.2488 | -1.45 | 0.14706 | -0.63 | -1.66 | -6.1444 | -1.2834 | 159 | 1.2853 | 1.63 | ne | odbaceno |
| commodities:SPIKE_DN:5d:short | 72 | -0.8691 | -0.8206 | -1.0873 | -1.47 | 0.14156 | -0.96 | -1.1 | 0.9922 | -1.1391 | 0 | None | None | ne | odbaceno |
| commodities:REV5:2w:short | 155 | -0.444 | -0.5687 | -0.5332 | -1.49 | 0.13622 | -1.55 | -0.53 | -0.5095 | -0.714 | 0 | None | None | ne | odbaceno |
| commodities:BRK20:2w:short | 153 | -0.5023 | -0.2632 | -0.5672 | -1.55 | 0.12114 | -0.42 | -1.68 | -0.7121 | -0.7723 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:5d:short | 178 | -1.1313 | -0.1237 | -1.2642 | -1.56 | 0.11876 | -1.66 | -0.32 | 2.2606 | -1.4013 | - | - | - | ne | odbaceno |
| commodities:LOWVOL:2w:long | 149 | -0.3282 | -0.2343 | -0.3768 | -1.56 | 0.11876 | -1.03 | -1.17 | -0.6447 | -0.5982 | 0 | None | None | ne | odbaceno |
| crypto:VOLUP:1w:long | 323 | -0.6441 | -1.1141 | -0.8323 | -1.59 | 0.11183 | -0.31 | -2.96 | -1.4811 | -0.9141 | 323 | -0.1974 | -0.45 | ne | odbaceno |
| stocks:BRK20:4w:short | 76 | -3.4219 | -0.3163 | -3.6834 | -1.6 | 0.1096 | -1.42 | -0.86 | -2.4091 | -3.6919 | - | - | - | ne | odbaceno |
| commodities:ATTN:1w:short | 300 | -0.2172 | -0.2468 | -0.2544 | -1.61 | 0.1074 | -1.09 | -1.21 | -0.0654 | -0.4872 | 0 | None | None | ne | odbaceno |
| commodities:VOLUP:2w:short | 153 | -0.511 | -0.1704 | -0.5943 | -1.64 | 0.10101 | 0.14 | -2.24 | -0.9948 | -0.781 | 0 | None | None | ne | odbaceno |
| commodities:REV5:4w:long | 77 | -0.9504 | -1.4552 | -1.113 | -1.67 | 0.09492 | -1.19 | -1.18 | -0.2743 | -1.2204 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:4w:short | 64 | -1.9433 | -1.0605 | -2.2773 | -1.69 | 0.09103 | -2.01 | -0.14 | 1.6344 | -2.2133 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:1w:long | 260 | -0.3073 | -0.2551 | -0.337 | -1.78 | 0.07508 | -0.96 | -1.69 | -0.9109 | -0.5773 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:1w:short | 308 | -0.395 | 0.2104 | -0.4295 | -1.82 | 0.06876 | -1.28 | -1.29 | -1.0461 | -0.665 | - | - | - | ne | odbaceno |
| stocks:HIGH52:2w:short | 129 | -0.9177 | -0.2232 | -1.0082 | -1.84 | 0.06577 | -2.39 | 0.15 | 1.2331 | -1.1877 | - | - | - | ne | odbaceno |
| crypto:VOLUP:4w:long | 80 | -2.2432 | -1.1287 | -2.803 | -1.86 | 0.06289 | -1.91 | -0.39 | -4.6403 | -2.5132 | 80 | -2.2162 | -1.11 | ne | odbaceno |
| commodities:MOM12_1:4w:short | 64 | -1.135 | -1.1068 | -1.297 | -1.87 | 0.06148 | -2.14 | -0.26 | -2.3585 | -1.405 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:14d:long | 112 | -3.2518 | -3.0424 | -3.7226 | -1.92 | 0.05486 | -0.43 | -2.55 | -7.399 | -3.5218 | 71 | 0.6929 | 0.29 | ne | odbaceno |
| stocks:HIGH52:1w:short | 260 | -0.46 | -0.1392 | -0.4875 | -1.99 | 0.04659 | -2.58 | 0.03 | 0.2134 | -0.73 | - | - | - | ne | odbaceno |
| crypto:ATTN:1w:long | 319 | -0.8395 | -1.1507 | -0.9628 | -2.09 | 0.03662 | -1.45 | -1.71 | -1.7539 | -1.1095 | 319 | 0.4267 | 0.94 | ne | odbaceno |
| commodities:HIGH_BRK:10d:short | 24 | -2.7087 | -1.5853 | -3.2452 | -2.09 | None | -1.91 | -0.86 | -1.3837 | -2.9787 | 0 | None | None | ne | premalo |
| commodities:HIGH_BRK:20d:short | 13 | -5.8368 | -2.7848 | -6.7604 | -2.09 | None | -1.35 | -1.56 | -2.1703 | -6.1068 | 0 | None | None | ne | premalo |
| commodities:VOLUP:2w:long | 153 | -0.5601 | -0.5897 | -0.6324 | -2.11 | 0.03486 | -1.33 | -1.66 | -1.022 | -0.8301 | 0 | None | None | ne | odbaceno |
| stocks:LOWVOL:4w:short | 74 | -3.1447 | -1.5384 | -3.4984 | -2.14 | 0.03235 | -0.9 | -2.07 | -4.3076 | -3.4147 | - | - | - | ne | odbaceno |
| commodities:REV5:1w:short | 311 | -0.3355 | -0.3074 | -0.3655 | -2.14 | 0.03235 | -1.88 | -1.09 | -0.6836 | -0.6055 | 0 | None | None | ne | odbaceno |
| commodities:LOWVOL:1w:short | 300 | -0.4164 | -0.2677 | -0.4437 | -2.21 | 0.02711 | -1.46 | -1.66 | -0.4328 | -0.6864 | 0 | None | None | da | odbaceno |
| commodities:MOM12_1:2w:short | 129 | -0.6464 | -0.6018 | -0.7428 | -2.22 | 0.02642 | -3.11 | -0.04 | -0.7499 | -0.9164 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:4w:long | 74 | -1.7766 | -0.5485 | -1.9545 | -2.24 | 0.02509 | -0.83 | -2.32 | -3.8932 | -2.0466 | - | - | - | da | odbaceno |
| commodities:HIGH52:4w:short | 64 | -1.3651 | -1.2699 | -1.5348 | -2.25 | 0.02445 | -2.01 | -1.03 | -1.3911 | -1.6351 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_UP:7d:long | 227 | -2.2787 | -3.6381 | -2.6478 | -2.29 | 0.02202 | -0.23 | -4.21 | -7.5076 | -2.5487 | 155 | -0.8451 | -0.58 | da | odbaceno |
| commodities:VOLUP:4w:short | 76 | -1.4318 | -0.8652 | -1.5984 | -2.34 | 0.01928 | -2.46 | -0.92 | -3.9554 | -1.7018 | 0 | None | None | da | odbaceno |
| stocks:REV5:2w:short | 155 | -1.3012 | -0.4543 | -1.3917 | -2.35 | 0.01877 | -1.54 | -2.02 | -0.0889 | -1.5712 | - | - | - | da | odbaceno |
| stocks:VOLUP:1w:short | 308 | -0.4394 | -0.105 | -0.4724 | -2.39 | 0.01685 | -2.11 | -1.16 | -1.149 | -0.7094 | - | - | - | da | odbaceno |
| commodities:ATTN:1w:long | 300 | -0.2776 | -0.2992 | -0.298 | -2.4 | 0.0164 | -2.08 | -1.29 | -0.0865 | -0.5476 | 0 | None | None | da | odbaceno |
| stocks:ATTN:4w:short | 74 | -1.5177 | -1.2599 | -1.6674 | -2.44 | 0.01469 | -1.16 | -2.38 | -0.1885 | -1.7877 | - | - | - | da | odbaceno |
| crypto:REV5:4w:long | 80 | -3.0006 | -2.5461 | -3.401 | -2.48 | 0.01314 | -0.98 | -3.08 | -3.4586 | -3.2706 | 80 | 0.9762 | 0.79 | da | odbaceno |
| stocks:REV5:1w:short | 311 | -0.5579 | -0.3127 | -0.5928 | -2.54 | 0.01109 | -2.12 | -1.43 | -0.0775 | -0.8279 | - | - | - | da | odbaceno |
| stocks:LOWVOL:2w:short | 149 | -1.9737 | -0.6449 | -2.0973 | -2.79 | 0.00527 | -1.74 | -2.38 | -2.0247 | -2.2437 | - | - | - | da | odbaceno |
| crypto:MOM12_1:1w:long | 291 | -0.8847 | -0.9698 | -0.9382 | -2.79 | 0.00527 | -2.14 | -1.82 | -1.75 | -1.1547 | 286 | -0.0801 | -0.26 | da | odbaceno |
| crypto:ATTN:4w:long | 79 | -3.3897 | -3.0239 | -3.7526 | -2.79 | 0.00527 | -2.56 | -1.31 | -11.5316 | -3.6597 | 79 | -0.2453 | -0.16 | da | odbaceno |
| commodities:BRK20:2w:long | 153 | -0.6849 | -0.7177 | -0.7434 | -2.8 | 0.00511 | -1.31 | -2.8 | -1.8085 | -0.9549 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:1w:short | 308 | -0.3848 | -0.4479 | -0.4111 | -2.86 | 0.00424 | -3.17 | -0.72 | 0.3136 | -0.6548 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:7d:long | 129 | -5.8356 | -7.6539 | -6.8416 | -2.89 | 0.00385 | -1.01 | -3.08 | -11.7888 | -6.1056 | 53 | 2.0423 | 0.59 | da | odbaceno |
| stocks:LOWVOL:1w:long | 300 | -0.508 | -0.2172 | -0.5365 | -2.91 | 0.00361 | -1.51 | -2.59 | -1.0361 | -0.778 | - | - | - | da | odbaceno |
| commodities:HIGH52:1w:long | 260 | -0.3785 | -0.1781 | -0.401 | -2.93 | 0.00339 | -2.33 | -1.79 | -0.8616 | -0.6485 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:2w:long | 149 | -1.0586 | -0.7005 | -1.1292 | -2.94 | 0.00328 | -1.3 | -2.86 | -2.4359 | -1.3286 | - | - | - | da | odbaceno |
| commodities:BRK20:1w:short | 308 | -0.4334 | -0.3532 | -0.4642 | -2.94 | 0.00328 | -2.37 | -1.79 | -0.1078 | -0.7034 | 0 | None | None | da | odbaceno |
| stocks:SPIKE_UP:10d:short | 86 | -6.6391 | -0.5063 | -6.944 | -2.99 | 0.00279 | -2.52 | -1.6 | 0.0585 | -6.9091 | - | - | - | da | odbaceno |
| commodities:MOM12_1:1w:short | 260 | -0.4581 | -0.3307 | -0.4925 | -3.02 | 0.00253 | -3.19 | -0.92 | -0.3367 | -0.7281 | 0 | None | None | da | odbaceno |
| commodities:SPIKE_UP:5d:long | 71 | -1.5284 | -2.045 | -1.7932 | -3.07 | 0.00214 | -1.69 | -2.9 | -3.0327 | -1.7984 | 0 | None | None | da | odbaceno |
| commodities:BRK20:1w:long | 308 | -0.4229 | -0.2883 | -0.4522 | -3.12 | 0.00181 | -2.68 | -1.72 | -0.2133 | -0.6929 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:1w:short | 300 | -0.9795 | -0.2405 | -1.0267 | -3.21 | 0.00133 | -2.02 | -2.61 | -0.973 | -1.2495 | - | - | - | da | odbaceno |
| commodities:LOWVOL:1w:long | 300 | -0.3307 | -0.2804 | -0.348 | -3.26 | 0.00111 | -2.72 | -1.79 | -0.4359 | -0.6007 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:1w:long | 308 | -0.4676 | -0.3943 | -0.4976 | -3.52 | 0.00043 | -3.23 | -1.59 | -0.268 | -0.7376 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:28d:long | 37 | -19.2527 | -23.0738 | -22.506 | -3.66 | 0.00025 | -1.76 | -4.76 | -31.8519 | -19.5227 | 11 | -1.3094 | -0.46 | da | odbaceno |
| crypto:REV5:2w:long | 161 | -2.0024 | -2.3483 | -2.1844 | -3.73 | 0.00019 | -2.2 | -3.7 | -2.8177 | -2.2724 | 161 | -0.4499 | -0.75 | da | odbaceno |
| crypto:SPIKE_DN:14d:long | 69 | -11.5798 | -13.5256 | -12.4866 | -4.27 | 2e-05 | -1.45 | -6.0 | -24.5574 | -11.8498 | 28 | -6.0046 | -1.68 | da | odbaceno |
| commodities:HIGH52:2w:short | 129 | -1.4332 | -1.4189 | -1.5062 | -4.38 | 1e-05 | -3.42 | -2.72 | -1.0818 | -1.7032 | 0 | None | None | da | odbaceno |
| commodities:HIGH52:1w:short | 260 | -0.732 | -0.7807 | -0.7588 | -4.62 | 0.0 | -3.78 | -2.69 | -1.0217 | -1.002 | 0 | None | None | da | odbaceno |
| crypto:REV5:1w:long | 323 | -1.437 | -1.5817 | -1.5144 | -5.31 | 0.0 | -4.1 | -3.45 | -2.3733 | -1.707 | 323 | -0.7642 | -2.31 | da | odbaceno |

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
