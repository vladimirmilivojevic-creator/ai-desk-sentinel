# Lovac: studija na sirem univerzumu (2026-11-08)

Univerzumi: stocks 66 instrumenata (2020-11-09 do 2026-11-06); crypto 415 instrumenata (2020-07-23 do 2026-11-07); alts 566 instrumenata (2020-07-23 do 2026-11-07); commodities 20 instrumenata (2020-11-09 do 2026-11-06).
Testova: 240 (rang-porodice x horizonti x noge, dogadjaji x horizonti x noge), FDR 10% preko svih. Trosak 0.23% po krugu (strogo 0.50%). Mera = prosecan neto prinos ODABRANE grupe minus prosek univerzuma; nepreklapajuci periodi; t preko perioda.
Status: kandidat 5, nagovestaj 13, odbaceno 212, premalo 10.

Izvedivost: kolone 'izvedivo' su isti test samo na simbolima koje Liquid ima SADA (pristrasno prema preziveloj listi); kandidat mora da bude pozitivan i tamo (t >= 1).

Ogranicenja (cita se pre brojeva): nema stopova u testu; ulaz je otvaranje sledece svece, a uzivo se ulazi sat-dva kasnije. Zato jedino 'potvrdjen' (posle prolaska unapred) ima ikakvu tezinu.
- stocks: spisak je prema SADASNJOJ listi Liquid-a (preziveli i popularni), pa su istorijski rezultati verovatno prelepi.
- crypto: clanstvo je point-in-time (prvih 40 po prometu na dan, ukljucuje i kasnije ugasene kovanice), ali se trguje samo kovanicama koje Liquid sada ima; podaci su Binance spot, ne Liquid; uzivo se ulazi sat-dva posle otvaranja dnevne svece (dodato 0.10% troska).
- alts: tanje knjige i veci skokovi nego kod velikih kovanica (dodato 0.20% troska); mnoge kovanice nemaju HL trziste, pa se trguje samo delom studiranog skupa; skokovi su cesto vesti (listing, partnerstvo) koje podaci cene i obima ne mogu da predvide, pa je pitanje samo da li se posle prvog skoka isplati pratiti ili obrnuto; podaci su Binance spot, ne Liquid.
- commodities: Yahoo futures serije NISU ispravljene za zamenu ugovora (skokovi pri roll-u), pa je rezultat zasumljen i dodato je 0.15% troska; platinum, paladijum i aluminijum nisu u studiji (Yahoo nema obim).

## Svi testovi, poredjani po t

| pravilo | n | neto % | medijana % | bez najboljeg % | t | p | t prvi deo | t zadnji deo | zadnjih 270 d % | strogi trosak % | izvedivo n | izvedivo neto % | izvedivo t | FDR | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crypto:BRK20:2w:short | 161 | 3.2396 | 3.4741 | 3.0976 | 6.16 | 0.0 | 3.85 | 5.04 | 5.4762 | 2.9696 | 148 | 0.4068 | 0.47 | da | nagovestaj |
| crypto:BRK20:1w:short | 323 | 1.5398 | 1.6532 | 1.4635 | 5.34 | 0.0 | 3.47 | 4.45 | 2.6102 | 1.2698 | 299 | 0.4751 | 1.38 | da | kandidat |
| crypto:LOWVOL:2w:short | 159 | 3.4713 | 3.4856 | 3.2759 | 4.8 | 0.0 | 2.69 | 4.5 | 10.4375 | 3.2013 | 142 | 0.5235 | 0.46 | da | nagovestaj |
| crypto:BRK20:4w:short | 80 | 5.1302 | 4.3084 | 4.6761 | 4.44 | 1e-05 | 2.18 | 4.68 | 8.154 | 4.8602 | 74 | 2.225 | 1.68 | da | kandidat |
| alts:SPIKE_UP:3d:short | 323 | 1.9549 | 2.8208 | 1.8467 | 4.08 | 5e-05 | 4.97 | 1.02 | 4.0352 | 1.6849 | 1 | None | None | da | kandidat |
| crypto:SPIKE_DN:14d:short | 69 | 10.6532 | 12.1051 | 9.6931 | 3.97 | 7e-05 | 1.44 | 5.49 | 23.0272 | 10.3832 | 21 | 4.4648 | 0.94 | da | kandidat |
| crypto:LOWVOL:1w:short | 318 | 1.3846 | 1.5841 | 1.3161 | 3.52 | 0.00043 | 1.69 | 4.14 | 4.5052 | 1.1146 | 286 | -0.0352 | -0.07 | da | nagovestaj |
| crypto:SPIKE_DN:28d:short | 37 | 17.6468 | 16.8187 | 16.2042 | 3.38 | 0.00072 | 1.72 | 4.21 | 24.031 | 17.3768 | 9 | 4.3577 | 1.88 | da | nagovestaj |
| crypto:BRK20:2w:long | 161 | 1.8606 | 1.3302 | 1.6343 | 3.27 | 0.00108 | 3.11 | 1.24 | 0.4668 | 1.5906 | 148 | -0.368 | -0.55 | da | nagovestaj |
| alts:SPIKE_UP:7d:short | 321 | 1.9789 | 3.5775 | 1.8495 | 3.23 | 0.00124 | 2.63 | 1.9 | 6.2691 | 1.7089 | 1 | None | None | da | kandidat |
| stocks:SPIKE_UP:10d:long | 96 | 5.867 | 1.7371 | 4.6863 | 3.07 | 0.00214 | 2.2 | 2.17 | -1.155 | 5.597 | - | - | - | da | nagovestaj |
| crypto:LOWVOL:4w:short | 79 | 4.4097 | 4.7955 | 3.9374 | 3.02 | 0.00253 | 1.16 | 4.14 | 14.336 | 4.1397 | 70 | 0.1451 | 0.06 | da | nagovestaj |
| alts:LOWVOL:4w:long | 79 | 2.1637 | 1.0111 | 1.7865 | 2.98 | 0.00288 | 2.64 | 1.54 | -0.7739 | 1.8937 | 0 | None | None | da | nagovestaj |
| crypto:LOWVOL:2w:long | 159 | 1.2855 | 1.5536 | 1.1752 | 2.83 | 0.00465 | 0.82 | 4.22 | 2.5843 | 1.0155 | 142 | -0.448 | -0.57 | da | nagovestaj |
| crypto:SPIKE_DN:7d:short | 128 | 5.1276 | 6.6866 | 4.6054 | 2.52 | 0.01174 | 0.6 | 2.95 | 13.0567 | 4.8576 | 40 | -0.4297 | -0.1 | da | nagovestaj |
| crypto:LOWVOL:4w:long | 79 | 2.958 | 4.1021 | 2.6453 | 2.42 | 0.01552 | 0.62 | 4.39 | 3.2025 | 2.688 | 70 | -0.2454 | -0.1 | da | nagovestaj |
| alts:SPIKE_DN:7d:short | 272 | 2.5967 | 5.8287 | 2.3154 | 2.02 | 0.04338 | 1.19 | 1.96 | 5.2055 | 2.3267 | 0 | None | None | ne | nagovestaj |
| crypto:LOWVOL:1w:long | 318 | 0.5388 | 0.5828 | 0.4571 | 1.98 | 0.0477 | 0.77 | 2.36 | 0.9525 | 0.2688 | 286 | -0.3314 | -0.96 | ne | nagovestaj |
| alts:LOWVOL:4w:short | 79 | 1.8819 | 1.8639 | 1.639 | 1.93 | 0.05361 | 0.36 | 3.23 | 5.1861 | 1.6119 | 0 | None | None | ne | odbaceno |
| crypto:HIGH52:2w:short | 145 | 1.1618 | 0.8325 | 0.9409 | 1.89 | 0.05876 | 1.51 | 1.12 | 1.6121 | 0.8918 | 125 | 1.0096 | 1.65 | ne | odbaceno |
| crypto:SPIKE_UP:7d:short | 223 | 1.7942 | 3.0381 | 1.6079 | 1.8 | 0.07186 | 0.04 | 3.5 | 6.3831 | 1.5242 | 118 | 2.5109 | 2.43 | ne | odbaceno |
| commodities:HIGH_BRK:20d:long | 12 | 5.1793 | 1.824 | 2.8673 | 1.7 | None | 1.55 | 0.94 | 1.4103 | 4.9093 | 0 | None | None | ne | premalo |
| crypto:VOLUP:4w:short | 80 | 1.7675 | 1.0824 | 1.4356 | 1.69 | 0.09103 | 1.23 | 1.3 | 0.5782 | 1.4975 | 74 | -0.7857 | -0.54 | ne | odbaceno |
| commodities:SPIKE_UP:5d:short | 72 | 0.7658 | 1.2812 | 0.641 | 1.56 | 0.11876 | 0.61 | 1.81 | 2.1685 | 0.4958 | 0 | None | None | ne | odbaceno |
| commodities:HIGH_BRK:10d:long | 23 | 2.077 | 1.2638 | 1.2919 | 1.54 | None | 1.57 | 0.34 | 0.6237 | 1.807 | 0 | None | None | ne | premalo |
| alts:SPIKE_UP:14d:short | 159 | 2.0546 | 6.011 | 1.8351 | 1.53 | 0.12602 | 1.91 | 0.18 | 4.9305 | 1.7846 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:4w:long | 64 | 1.3616 | 1.0761 | 1.0464 | 1.5 | 0.13361 | 0.1 | 1.81 | 0.8953 | 1.0916 | - | - | - | ne | odbaceno |
| alts:LOWVOL:2w:long | 159 | 0.6323 | 0.3511 | 0.3709 | 1.44 | 0.14987 | 0.87 | 1.5 | 0.5687 | 0.3623 | 1 | None | None | ne | odbaceno |
| alts:LOWVOL:2w:short | 159 | 0.7575 | 1.1143 | 0.634 | 1.4 | 0.16151 | -0.19 | 2.93 | 1.9866 | 0.4875 | 1 | None | None | ne | odbaceno |
| crypto:BRK20:1w:long | 323 | 0.4845 | 0.4804 | 0.3433 | 1.31 | 0.1902 | 1.18 | 0.59 | -0.5383 | 0.2145 | 299 | -0.1585 | -0.48 | ne | odbaceno |
| crypto:SPIKE_UP:14d:short | 111 | 2.0962 | 2.2411 | 1.591 | 1.26 | 0.20767 | -0.04 | 2.09 | 5.3364 | 1.8262 | 56 | -1.5297 | -0.85 | ne | odbaceno |
| alts:HIGH_BRK:14d:short | 79 | 3.3215 | 3.1251 | 2.5654 | 1.26 | 0.20767 | 0.39 | 1.34 | 11.8497 | 3.0515 | 0 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:7d:short | 116 | 2.3178 | 1.6326 | 1.7345 | 1.25 | 0.2113 | 1.67 | 0.02 | 10.3 | 2.0478 | 60 | -2.3862 | -1.52 | ne | odbaceno |
| crypto:HIGH52:2w:long | 145 | 0.7294 | 0.4479 | 0.5245 | 1.22 | 0.22246 | 1.42 | 0.04 | -1.3517 | 0.4594 | 125 | 0.3172 | 0.47 | ne | odbaceno |
| stocks:VOLUP:2w:long | 153 | 0.3796 | 0.2006 | 0.2536 | 1.18 | 0.238 | 0.77 | 0.89 | 0.4376 | 0.1096 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:5d:short | 170 | 0.6595 | 1.4172 | 0.4296 | 1.15 | 0.25014 | 0.61 | 1.1 | -0.4555 | 0.3895 | - | - | - | ne | odbaceno |
| crypto:HIGH52:4w:short | 72 | 1.3955 | 2.3369 | 1.0864 | 1.11 | 0.267 | 0.32 | 1.75 | 3.4049 | 1.1255 | 62 | 2.8469 | 2.76 | ne | odbaceno |
| crypto:ATTN:2w:short | 159 | 0.5518 | 0.1157 | 0.4148 | 1.1 | 0.27133 | 0.3 | 1.94 | 0.618 | 0.2818 | 143 | -0.1986 | -0.23 | ne | odbaceno |
| stocks:MOM12_1:2w:long | 129 | 0.4694 | 0.0959 | 0.336 | 1.05 | 0.29372 | -0.17 | 1.45 | 0.4779 | 0.1994 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:4w:short | 72 | 1.2561 | 3.1999 | 0.983 | 1.05 | 0.29372 | 0.01 | 2.38 | 3.3736 | 0.9861 | 62 | 2.5345 | 2.11 | ne | odbaceno |
| crypto:VOLUP:2w:short | 161 | 0.5671 | 0.9294 | 0.3927 | 1.04 | 0.29834 | 1.01 | 0.39 | 2.1393 | 0.2971 | 148 | -1.1571 | -1.55 | ne | odbaceno |
| stocks:HIGH_BRK:10d:long | 70 | 1.2218 | 0.0377 | 0.6666 | 1.02 | 0.30773 | 0.83 | 0.58 | -1.3145 | 0.9518 | - | - | - | ne | odbaceno |
| stocks:VOLUP:4w:long | 76 | 0.7789 | 0.0239 | 0.3472 | 1.01 | 0.3125 | 0.98 | 0.46 | -1.6054 | 0.5089 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:short | 42 | 2.1059 | 3.1751 | 1.5191 | 0.99 | 0.32217 | 0.89 | 0.48 | 4.7873 | 1.8359 | - | - | - | ne | odbaceno |
| alts:LOWVOL:1w:short | 318 | 0.254 | 0.4072 | 0.2108 | 0.96 | 0.33706 | -1.31 | 3.5 | 1.6678 | -0.016 | 1 | None | None | ne | odbaceno |
| alts:BRK20:4w:short | 80 | 0.8871 | 0.0093 | 0.3428 | 0.88 | 0.37886 | 0.56 | 0.99 | -0.5537 | 0.6171 | 1 | None | None | ne | odbaceno |
| crypto:BRK20:4w:long | 80 | 1.0768 | 2.6786 | 0.6839 | 0.87 | 0.3843 | 0.07 | 1.58 | -2.1528 | 0.8068 | 74 | -0.7395 | -0.37 | ne | odbaceno |
| crypto:HIGH_BRK:14d:short | 61 | 2.9706 | 4.3501 | 1.7315 | 0.87 | 0.3843 | 0.71 | 0.49 | 11.8317 | 2.7006 | 31 | -2.8437 | -0.98 | ne | odbaceno |
| stocks:SPIKE_UP:5d:long | 198 | 0.5654 | 0.4049 | 0.2772 | 0.8 | 0.42371 | 0.15 | 0.94 | -2.3069 | 0.2954 | - | - | - | ne | odbaceno |
| crypto:HIGH52:1w:short | 291 | 0.2375 | 0.6019 | 0.1483 | 0.8 | 0.42371 | 1.15 | -0.15 | 0.0273 | -0.0325 | 253 | 0.1528 | 0.49 | ne | odbaceno |
| crypto:REV5:4w:short | 80 | 1.1412 | 1.6261 | 0.709 | 0.74 | 0.4593 | 1.06 | -0.34 | 7.3877 | 0.8712 | 74 | -3.0421 | -1.18 | ne | odbaceno |
| alts:ATTN:4w:short | 79 | 0.6959 | 0.8724 | 0.2523 | 0.74 | 0.4593 | 0.42 | 1.04 | 2.413 | 0.4259 | 0 | None | None | ne | odbaceno |
| crypto:ATTN:1w:short | 319 | 0.1953 | 0.2422 | 0.1349 | 0.69 | 0.49019 | -0.35 | 2.13 | 0.5395 | -0.0747 | 288 | -0.5444 | -1.15 | ne | odbaceno |
| commodities:SPIKE_UP:10d:short | 36 | 0.6842 | 2.0844 | 0.3747 | 0.6 | 0.54851 | 0.39 | 0.46 | 0.0485 | 0.4142 | 0 | None | None | ne | odbaceno |
| crypto:MOM12_1:2w:short | 145 | 0.4077 | 1.2938 | 0.2329 | 0.58 | 0.56191 | -0.27 | 1.73 | 0.6286 | 0.1377 | 125 | 0.6827 | 1.16 | ne | odbaceno |
| crypto:SPIKE_UP:28d:short | 54 | 2.1913 | 6.3574 | 0.4534 | 0.58 | 0.56191 | -1.22 | 2.44 | 14.455 | 1.9213 | 23 | -1.9464 | -0.44 | ne | odbaceno |
| alts:VOLUP:4w:short | 80 | 0.3976 | 0.4796 | 0.1751 | 0.56 | 0.57548 | -0.16 | 1.32 | 2.798 | 0.1276 | 1 | None | None | ne | odbaceno |
| commodities:ATTN:4w:short | 74 | 0.3019 | -0.2451 | 0.0471 | 0.55 | 0.58232 | 0.13 | 0.62 | 4.1922 | 0.0319 | 0 | None | None | ne | odbaceno |
| alts:SPIKE_DN:14d:short | 133 | 1.5793 | 6.3028 | 1.2621 | 0.54 | 0.5892 | 2.67 | -0.49 | 7.6006 | 1.3093 | 0 | None | None | ne | odbaceno |
| crypto:HIGH52:4w:long | 72 | 0.6623 | 0.4927 | 0.0623 | 0.49 | 0.62413 | 0.55 | 0.04 | -3.4029 | 0.3923 | 62 | 1.1228 | 0.62 | ne | odbaceno |
| stocks:SPIKE_UP:20d:long | 49 | 1.2089 | 0.4327 | -0.3398 | 0.41 | 0.68181 | 0.71 | -0.27 | -11.3875 | 0.9389 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:4w:long | 64 | 0.2858 | 0.4189 | 0.0806 | 0.37 | 0.71138 | 0.34 | 0.18 | -2.0756 | 0.0158 | 0 | None | None | ne | odbaceno |
| alts:BRK20:4w:long | 80 | 0.3758 | -0.2257 | -0.3133 | 0.34 | 0.73386 | 0.8 | -0.81 | -0.6354 | 0.1058 | 1 | None | None | ne | odbaceno |
| alts:ATTN:2w:short | 159 | 0.1416 | -0.025 | -0.0762 | 0.33 | 0.7414 | 0.18 | 0.38 | -0.5303 | -0.1284 | 1 | None | None | ne | odbaceno |
| alts:HIGH_BRK:7d:long | 160 | 0.6334 | -2.3611 | -0.2734 | 0.32 | 0.74897 | 0.71 | -0.21 | 3.0903 | 0.3634 | 0 | None | None | ne | odbaceno |
| alts:SPIKE_DN:3d:short | 273 | 0.4139 | 3.5573 | 0.2222 | 0.28 | 0.77948 | 0.44 | -0.21 | 0.5054 | 0.1439 | 0 | None | None | ne | odbaceno |
| stocks:REV5:4w:long | 77 | 0.2827 | -1.2319 | -0.9673 | 0.2 | 0.84148 | 0.52 | -0.83 | -1.0971 | 0.0127 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:10d:short | 81 | 0.3187 | 1.2602 | -0.1096 | 0.18 | 0.85715 | -0.63 | 1.54 | 5.1813 | 0.0487 | - | - | - | ne | odbaceno |
| alts:REV5:1w:short | 323 | 0.0484 | 0.2126 | -0.013 | 0.18 | 0.85715 | -0.24 | 0.65 | 1.6126 | -0.2216 | 3 | 5.6969 | 0.71 | ne | odbaceno |
| commodities:BRK20:4w:short | 76 | 0.1043 | -0.2831 | -0.1037 | 0.17 | 0.86501 | 0.8 | -0.49 | -1.2151 | -0.1657 | 0 | None | None | ne | odbaceno |
| alts:BRK20:1w:short | 323 | 0.0297 | -0.0684 | -0.0302 | 0.15 | 0.88076 | -0.44 | 0.94 | 0.6147 | -0.2403 | 3 | 0.9559 | 0.55 | ne | odbaceno |
| commodities:SPIKE_DN:20d:short | 15 | 0.2857 | 1.4465 | -0.6404 | 0.15 | None | -0.3 | 1.3 | 3.0496 | 0.0157 | 0 | None | None | ne | premalo |
| commodities:SPIKE_DN:5d:long | 73 | 0.0783 | -0.0847 | -0.1092 | 0.13 | 0.89657 | -0.14 | 0.32 | -1.7797 | -0.1917 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:4w:short | 64 | 0.0791 | 0.7729 | -0.0845 | 0.11 | 0.91241 | -0.41 | 0.9 | 0.5216 | -0.1909 | - | - | - | ne | odbaceno |
| crypto:ATTN:4w:short | 79 | 0.0929 | 0.8914 | -0.1839 | 0.1 | 0.92034 | -0.58 | 1.45 | 1.4917 | -0.1771 | 71 | -1.3316 | -0.72 | ne | odbaceno |
| stocks:HIGH_BRK:20d:short | 32 | 0.222 | -0.2946 | -1.0601 | 0.09 | 0.92829 | -0.22 | 0.68 | -4.5643 | -0.048 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:28d:short | 27 | 0.7223 | 6.4546 | -1.615 | 0.09 | None | -0.09 | 0.24 | 21.0613 | 0.4523 | 14 | -4.229 | -0.57 | ne | premalo |
| crypto:VOLUP:1w:short | 323 | 0.0109 | 0.4939 | -0.0395 | 0.04 | 0.96809 | 0.45 | -0.51 | 0.6066 | -0.2591 | 299 | -0.7167 | -2.12 | ne | odbaceno |
| stocks:ATTN:1w:short | 300 | 0.0002 | 0.1397 | -0.0295 | 0.0 | 1.0 | -0.13 | 0.17 | 0.2222 | -0.2698 | - | - | - | ne | odbaceno |
| commodities:REV5:2w:long | 155 | -0.0059 | 0.0042 | -0.09 | -0.02 | 0.98404 | -0.34 | 0.33 | -0.8377 | -0.2759 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:1w:long | 260 | -0.0079 | 0.1379 | -0.0609 | -0.04 | 0.96809 | -0.18 | 0.09 | -0.4573 | -0.2779 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:5d:short | 136 | -0.0351 | -0.0415 | -0.3599 | -0.05 | 0.96012 | -0.47 | 0.35 | 1.5231 | -0.3051 | - | - | - | ne | odbaceno |
| stocks:ATTN:2w:long | 149 | -0.0157 | -0.2911 | -0.0937 | -0.06 | 0.95216 | -0.31 | 0.33 | -0.0875 | -0.2857 | - | - | - | ne | odbaceno |
| stocks:BRK20:4w:long | 76 | -0.0775 | 0.6763 | -0.2265 | -0.12 | 0.90448 | 0.11 | -0.28 | -1.0728 | -0.3475 | - | - | - | ne | odbaceno |
| alts:LOWVOL:1w:long | 318 | -0.0231 | 0.1118 | -0.09 | -0.12 | 0.90448 | -1.55 | 2.32 | 0.5051 | -0.2931 | 1 | None | None | ne | odbaceno |
| alts:HIGH_BRK:3d:long | 160 | -0.1579 | -1.0953 | -0.5151 | -0.12 | 0.90448 | 0.24 | -0.41 | -4.9612 | -0.4279 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_UP:20d:long | 22 | -0.3317 | -2.0889 | -2.3349 | -0.14 | None | -1.85 | 0.76 | 1.6125 | -0.6017 | 0 | None | None | ne | premalo |
| crypto:HIGH_BRK:28d:long | 27 | -1.3823 | -7.1146 | -6.816 | -0.17 | None | 0.03 | -0.29 | -21.7213 | -1.6523 | 14 | 3.569 | 0.48 | ne | premalo |
| commodities:SPIKE_DN:10d:short | 38 | -0.1897 | 0.5893 | -0.9215 | -0.17 | 0.86501 | -1.05 | 0.68 | -0.4072 | -0.4597 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_UP:20d:short | 22 | -0.4283 | 1.3289 | -0.9692 | -0.18 | None | 1.41 | -0.92 | -2.3725 | -0.6983 | 0 | None | None | ne | premalo |
| commodities:LOWVOL:4w:short | 74 | -0.1394 | 0.4913 | -0.3999 | -0.19 | 0.84931 | 0.41 | -0.65 | -1.8484 | -0.4094 | 0 | None | None | ne | odbaceno |
| stocks:REV5:4w:short | 77 | -0.1438 | -0.2102 | -0.3998 | -0.2 | 0.84148 | 0.17 | -0.42 | 1.4424 | -0.4138 | - | - | - | ne | odbaceno |
| stocks:BRK20:1w:long | 308 | -0.0297 | 0.125 | -0.0779 | -0.2 | 0.84148 | 0.12 | -0.41 | -0.0748 | -0.2997 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:2w:long | 129 | -0.0735 | 0.3275 | -0.1453 | -0.2 | 0.84148 | -0.14 | -0.13 | -0.6878 | -0.3435 | 0 | None | None | ne | odbaceno |
| alts:REV5:2w:short | 161 | -0.1411 | 0.7363 | -0.2616 | -0.27 | 0.78716 | -0.74 | 0.62 | 1.8441 | -0.4111 | 2 | None | None | ne | odbaceno |
| stocks:HIGH_BRK:20d:long | 32 | -0.682 | -0.1654 | -1.7695 | -0.28 | 0.77948 | 0.1 | -0.86 | 4.1043 | -0.952 | - | - | - | ne | odbaceno |
| crypto:REV5:1w:short | 323 | -0.1064 | 0.3076 | -0.1714 | -0.28 | 0.77948 | -0.76 | 1.03 | 1.4036 | -0.3764 | 299 | -0.4368 | -1.2 | ne | odbaceno |
| stocks:ATTN:2w:short | 149 | -0.0791 | -0.373 | -0.1388 | -0.3 | 0.76418 | 0.44 | -1.14 | -0.0564 | -0.3491 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:4w:long | 72 | -0.375 | -1.5434 | -0.8235 | -0.3 | 0.76418 | -0.06 | -0.48 | -1.0526 | -0.645 | 62 | 1.2817 | 0.9 | ne | odbaceno |
| alts:VOLUP:4w:long | 80 | -0.3122 | -0.345 | -0.9603 | -0.3 | 0.76418 | 0.11 | -0.99 | 0.5782 | -0.5822 | 1 | None | None | ne | odbaceno |
| commodities:HIGH_BRK:5d:short | 50 | -0.2323 | -0.1831 | -0.5986 | -0.33 | 0.7414 | -1.07 | 0.64 | 0.2112 | -0.5023 | 0 | None | None | ne | odbaceno |
| crypto:REV5:2w:short | 161 | -0.2363 | 0.2227 | -0.4091 | -0.39 | 0.69654 | -0.86 | 0.65 | 3.5309 | -0.5063 | 148 | -0.742 | -1.1 | ne | odbaceno |
| alts:VOLUP:2w:short | 161 | -0.1615 | 0.0072 | -0.2667 | -0.41 | 0.68181 | 0.21 | -0.99 | 0.2989 | -0.4315 | 2 | None | None | ne | odbaceno |
| stocks:SPIKE_DN:10d:long | 81 | -0.7787 | -1.7202 | -1.8542 | -0.43 | 0.6672 | 0.46 | -1.76 | -5.6413 | -1.0487 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:1w:short | 291 | -0.1353 | 0.1835 | -0.1855 | -0.45 | 0.65271 | -0.77 | 0.32 | -0.7214 | -0.4053 | 253 | -0.078 | -0.27 | ne | odbaceno |
| alts:MOM12_1:4w:long | 72 | -0.4184 | -0.0263 | -0.7475 | -0.45 | 0.65271 | -0.17 | -0.51 | -3.044 | -0.6884 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:4w:long | 64 | -0.3046 | -0.2234 | -0.5318 | -0.47 | 0.63836 | -1.13 | 0.43 | 1.7274 | -0.5746 | - | - | - | ne | odbaceno |
| stocks:MOM12_1:2w:short | 129 | -0.1836 | -0.0763 | -0.2502 | -0.5 | 0.61708 | -0.91 | 0.48 | 0.1691 | -0.4536 | - | - | - | ne | odbaceno |
| commodities:ATTN:2w:long | 149 | -0.1215 | 0.0313 | -0.1678 | -0.51 | 0.61005 | -1.07 | 0.39 | 1.0126 | -0.3915 | 0 | None | None | ne | odbaceno |
| alts:REV5:2w:long | 161 | -0.2046 | -0.7171 | -0.3679 | -0.52 | 0.60306 | 0.42 | -2.34 | -0.1832 | -0.4746 | 2 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:10d:long | 38 | -0.5703 | -1.3493 | -0.9906 | -0.52 | 0.60306 | 0.44 | -1.07 | -0.3528 | -0.8403 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:20d:long | 15 | -1.0457 | -2.2065 | -2.3448 | -0.53 | None | 0.05 | -1.76 | -3.8096 | -1.3157 | 0 | None | None | ne | premalo |
| alts:HIGH_BRK:3d:short | 160 | -0.7021 | 0.2353 | -0.922 | -0.54 | 0.5892 | -0.81 | 0.04 | 4.1012 | -0.9721 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:4w:long | 64 | -0.3267 | 0.3541 | -0.5851 | -0.55 | 0.58232 | 0.69 | -1.42 | -4.8339 | -0.5967 | 0 | None | None | ne | odbaceno |
| alts:BRK20:2w:short | 161 | -0.2326 | -0.2213 | -0.4062 | -0.56 | 0.57548 | -0.77 | 0.25 | -0.4004 | -0.5026 | 2 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:20d:short | 49 | -1.6689 | -0.8927 | -2.3155 | -0.57 | 0.56868 | -0.83 | 0.17 | 10.9275 | -1.9389 | - | - | - | ne | odbaceno |
| stocks:VOLUP:1w:long | 308 | -0.1057 | -0.1978 | -0.1516 | -0.63 | 0.52869 | -0.2 | -0.69 | -0.2143 | -0.3757 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:5d:long | 136 | -0.4249 | -0.4185 | -0.6606 | -0.63 | 0.52869 | -0.14 | -0.71 | -1.9831 | -0.6949 | - | - | - | ne | odbaceno |
| stocks:REV5:1w:long | 311 | -0.1124 | -0.2188 | -0.1512 | -0.69 | 0.49019 | -0.15 | -0.85 | 0.0146 | -0.3824 | - | - | - | ne | odbaceno |
| commodities:REV5:4w:short | 77 | -0.4321 | -0.225 | -0.6295 | -0.71 | 0.4777 | 0.12 | -1.04 | -0.5533 | -0.7021 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:2w:long | 153 | -0.1866 | -0.133 | -0.2383 | -0.72 | 0.47152 | -0.7 | -0.35 | -1.4823 | -0.4566 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:long | 50 | -0.5277 | -0.5769 | -0.8874 | -0.74 | 0.4593 | 0.18 | -1.26 | -0.9712 | -0.7977 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:28d:long | 54 | -2.8513 | -7.0174 | -4.2327 | -0.75 | 0.45325 | 1.07 | -2.56 | -15.115 | -3.1213 | 23 | 1.2864 | 0.29 | ne | odbaceno |
| alts:HIGH_BRK:7d:short | 160 | -1.4934 | 1.5011 | -1.8134 | -0.75 | 0.45325 | -1.1 | -0.02 | -3.9503 | -1.7634 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:2w:long | 129 | -0.2416 | -0.3996 | -0.3202 | -0.77 | 0.4413 | -1.7 | 0.6 | 0.1054 | -0.5116 | - | - | - | ne | odbaceno |
| commodities:LOWVOL:4w:long | 74 | -0.3404 | -0.4446 | -0.4736 | -0.78 | 0.43539 | -0.32 | -0.77 | -2.1364 | -0.6104 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:4w:long | 74 | -0.3693 | -0.4571 | -0.4869 | -0.78 | 0.43539 | -0.62 | -0.47 | 0.9254 | -0.6393 | 0 | None | None | ne | odbaceno |
| alts:SPIKE_DN:14d:long | 133 | -2.4393 | -7.1628 | -4.9987 | -0.83 | 0.40654 | -3.14 | 0.36 | -8.4606 | -2.7093 | 0 | None | None | ne | odbaceno |
| crypto:HIGH52:1w:long | 291 | -0.2835 | -0.2516 | -0.3712 | -0.85 | 0.39533 | -0.49 | -0.78 | -1.4006 | -0.5535 | 253 | -0.0965 | -0.29 | ne | odbaceno |
| alts:SPIKE_DN:3d:long | 273 | -1.2739 | -4.4173 | -2.348 | -0.88 | 0.37886 | -0.84 | -0.28 | -1.3654 | -1.5439 | 0 | None | None | ne | odbaceno |
| alts:MOM12_1:2w:long | 145 | -0.3959 | -0.2939 | -0.5589 | -0.9 | 0.36812 | -0.28 | -1.17 | -2.4333 | -0.6659 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:2w:short | 149 | -0.2632 | -0.3752 | -0.3288 | -0.94 | 0.34722 | -1.59 | 0.29 | 1.279 | -0.5332 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:1w:long | 300 | -0.1206 | -0.1466 | -0.1535 | -0.96 | 0.33706 | -1.0 | -0.3 | -0.0124 | -0.3906 | - | - | - | ne | odbaceno |
| stocks:REV5:2w:long | 155 | -0.3377 | -0.7528 | -0.4347 | -0.99 | 0.32217 | 0.39 | -2.01 | -0.6766 | -0.6077 | - | - | - | ne | odbaceno |
| alts:MOM12_1:2w:short | 145 | -0.4476 | 0.2394 | -0.5285 | -1.01 | 0.3125 | -0.97 | -0.34 | -0.7839 | -0.7176 | 0 | None | None | ne | odbaceno |
| stocks:VOLUP:4w:short | 76 | -1.2979 | -0.1766 | -1.5235 | -1.02 | 0.30773 | -0.8 | -0.81 | -2.5047 | -1.5679 | - | - | - | ne | odbaceno |
| alts:REV5:4w:long | 80 | -0.7237 | -1.1187 | -1.0319 | -1.02 | 0.30773 | 0.04 | -1.88 | -0.457 | -0.9937 | 1 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:14d:long | 61 | -3.6306 | -5.0101 | -5.1108 | -1.06 | 0.28914 | -0.86 | -0.62 | -12.4917 | -3.9006 | 31 | 2.1837 | 0.75 | ne | odbaceno |
| commodities:LOWVOL:2w:short | 149 | -0.4164 | -0.418 | -0.5111 | -1.09 | 0.27571 | -0.24 | -1.27 | -0.8097 | -0.6864 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:1w:short | 260 | -0.2033 | -0.1113 | -0.2335 | -1.1 | 0.27133 | -1.03 | -0.41 | -0.0979 | -0.4733 | - | - | - | ne | odbaceno |
| alts:MOM12_1:4w:short | 72 | -1.1016 | 0.5401 | -1.3177 | -1.12 | 0.26271 | -0.59 | -1.07 | -1.6918 | -1.3716 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:2w:short | 153 | -0.519 | -0.0771 | -0.5922 | -1.14 | 0.25429 | -1.17 | -0.3 | -1.0406 | -0.789 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:long | 42 | -2.5659 | -3.6351 | -3.5926 | -1.21 | 0.22628 | -1.07 | -0.61 | -5.2473 | -2.8359 | - | - | - | ne | odbaceno |
| stocks:ATTN:4w:long | 74 | -0.5964 | -1.1031 | -0.7409 | -1.22 | 0.22246 | -2.25 | 0.82 | 0.7713 | -0.8664 | - | - | - | ne | odbaceno |
| alts:REV5:4w:short | 80 | -1.6089 | -1.1937 | -1.957 | -1.25 | 0.2113 | -1.08 | -0.65 | 0.4118 | -1.8789 | 1 | None | None | ne | odbaceno |
| stocks:HIGH52:2w:short | 129 | -0.5832 | 0.0889 | -0.6627 | -1.27 | 0.20408 | -1.43 | -0.25 | 0.7683 | -0.8532 | - | - | - | ne | odbaceno |
| commodities:SPIKE_UP:10d:long | 36 | -1.4442 | -2.8444 | -2.0206 | -1.27 | 0.20408 | -1.12 | -0.78 | -0.8085 | -1.7142 | 0 | None | None | ne | odbaceno |
| alts:MOM12_1:1w:short | 291 | -0.2592 | 0.0344 | -0.3012 | -1.28 | 0.20055 | -1.75 | 0.21 | 0.1789 | -0.5292 | 0 | None | None | ne | odbaceno |
| alts:HIGH52:4w:long | 72 | -1.261 | -0.2601 | -1.5234 | -1.28 | 0.20055 | -0.55 | -1.29 | -4.7164 | -1.531 | 0 | None | None | ne | odbaceno |
| crypto:MOM12_1:2w:long | 145 | -0.8466 | -0.5767 | -1.0816 | -1.3 | 0.1936 | -1.49 | -0.28 | -1.6516 | -1.1166 | 125 | 0.5957 | 0.92 | ne | odbaceno |
| commodities:BRK20:4w:long | 76 | -0.6508 | -0.0816 | -0.7584 | -1.32 | 0.18684 | -1.11 | -0.78 | -2.9578 | -0.9208 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:2w:long | 129 | -0.3783 | -0.3896 | -0.4683 | -1.33 | 0.18352 | -0.52 | -1.34 | -1.3766 | -0.6483 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:4w:short | 64 | -1.3777 | -0.4089 | -1.6674 | -1.34 | 0.18025 | -1.25 | -0.59 | 0.891 | -1.6477 | - | - | - | ne | odbaceno |
| crypto:VOLUP:2w:long | 161 | -0.8069 | -1.3898 | -1.0035 | -1.34 | 0.18025 | -0.59 | -1.45 | -1.0879 | -1.0769 | 148 | -0.9438 | -1.49 | ne | odbaceno |
| commodities:VOLUP:4w:long | 76 | -0.7431 | -0.5578 | -0.9047 | -1.36 | 0.17383 | -1.26 | -0.64 | -2.4635 | -1.0131 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:1w:short | 260 | -0.3026 | -0.0578 | -0.329 | -1.37 | 0.17069 | -1.63 | -0.14 | 0.3087 | -0.5726 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:short | 70 | -1.6818 | -0.4977 | -2.1259 | -1.4 | 0.16151 | -1.12 | -0.84 | 0.8545 | -1.9518 | - | - | - | ne | odbaceno |
| stocks:ATTN:4w:short | 74 | -0.7288 | -0.8184 | -0.8707 | -1.41 | 0.15854 | -0.8 | -1.17 | 0.307 | -0.9988 | - | - | - | ne | odbaceno |
| commodities:SPIKE_DN:5d:short | 73 | -0.8383 | -0.6753 | -1.053 | -1.43 | 0.15272 | -0.96 | -1.06 | 1.0197 | -1.1083 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:1w:long | 260 | -0.2378 | -0.2435 | -0.2671 | -1.44 | 0.14987 | -2.41 | 0.31 | -0.1594 | -0.5078 | - | - | - | ne | odbaceno |
| commodities:LOWVOL:2w:long | 149 | -0.3037 | -0.2098 | -0.3522 | -1.44 | 0.14987 | -1.0 | -1.03 | -0.8391 | -0.5737 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:5d:short | 198 | -1.0254 | -0.8649 | -1.1619 | -1.45 | 0.14706 | -0.72 | -1.3 | 1.8469 | -1.2954 | - | - | - | ne | odbaceno |
| crypto:ATTN:2w:long | 159 | -0.9923 | -0.9068 | -1.2276 | -1.47 | 0.14156 | -0.78 | -1.57 | -5.4537 | -1.2623 | 143 | 1.6007 | 2.1 | ne | odbaceno |
| alts:MOM12_1:1w:long | 291 | -0.3158 | -0.3728 | -0.3559 | -1.47 | 0.14156 | -1.33 | -0.68 | -1.1229 | -0.5858 | 0 | None | None | ne | odbaceno |
| commodities:MOM12_1:1w:long | 260 | -0.2703 | -0.1339 | -0.2999 | -1.54 | 0.12356 | -0.83 | -1.44 | -0.6255 | -0.5403 | 0 | None | None | ne | odbaceno |
| commodities:REV5:2w:short | 155 | -0.4618 | -0.5759 | -0.5511 | -1.55 | 0.12114 | -1.48 | -0.69 | -1.4028 | -0.7318 | 0 | None | None | ne | odbaceno |
| alts:HIGH52:4w:short | 72 | -1.658 | 0.1091 | -1.9046 | -1.56 | 0.11876 | -0.53 | -1.84 | -5.578 | -1.928 | 0 | None | None | ne | odbaceno |
| commodities:REV5:1w:long | 311 | -0.2368 | -0.1908 | -0.2809 | -1.56 | 0.11876 | -0.99 | -1.2 | -1.2037 | -0.5068 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:1w:short | 308 | -0.2934 | -0.0303 | -0.3272 | -1.57 | 0.11642 | -1.19 | -1.02 | -0.6478 | -0.5634 | - | - | - | ne | odbaceno |
| alts:HIGH_BRK:14d:long | 79 | -4.1815 | -3.9851 | -5.0402 | -1.58 | 0.11411 | -0.68 | -1.52 | -12.7097 | -4.4515 | 0 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:7d:long | 116 | -2.9778 | -2.2926 | -3.5549 | -1.6 | 0.1096 | -1.96 | -0.24 | -10.96 | -3.2478 | 60 | 1.7262 | 1.1 | ne | odbaceno |
| commodities:ATTN:1w:short | 300 | -0.217 | -0.2535 | -0.2542 | -1.61 | 0.1074 | -1.1 | -1.19 | -0.1801 | -0.487 | 0 | None | None | ne | odbaceno |
| commodities:REV5:4w:long | 77 | -0.9113 | -1.4552 | -1.0734 | -1.62 | 0.10523 | -0.73 | -1.74 | 0.104 | -1.1813 | 0 | None | None | ne | odbaceno |
| alts:ATTN:1w:short | 319 | -0.3389 | -0.1131 | -0.4258 | -1.63 | 0.1031 | -1.46 | -0.71 | -0.4369 | -0.6089 | 1 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:14d:long | 111 | -2.7562 | -2.9011 | -3.2267 | -1.66 | 0.09691 | -0.26 | -2.35 | -5.9964 | -3.0262 | 56 | 0.8697 | 0.48 | ne | odbaceno |
| commodities:BRK20:2w:short | 153 | -0.5373 | -0.3188 | -0.6025 | -1.66 | 0.09691 | -0.89 | -1.42 | -1.3175 | -0.8073 | 0 | None | None | ne | odbaceno |
| stocks:VOLUP:2w:short | 153 | -0.6378 | -0.2103 | -0.7215 | -1.67 | 0.09492 | -1.55 | -0.69 | -0.9606 | -0.9078 | - | - | - | ne | odbaceno |
| alts:BRK20:2w:long | 161 | -0.8389 | -1.1936 | -1.1058 | -1.67 | 0.09492 | -0.25 | -2.92 | -0.5852 | -1.1089 | 2 | None | None | ne | odbaceno |
| commodities:MOM12_1:4w:short | 64 | -1.0137 | -0.9552 | -1.1738 | -1.67 | 0.09492 | -2.04 | -0.07 | -2.0439 | -1.2837 | 0 | None | None | ne | odbaceno |
| commodities:VOLUP:2w:short | 153 | -0.5276 | -0.2341 | -0.6109 | -1.7 | 0.08913 | -0.24 | -2.03 | -1.0337 | -0.7976 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:4w:short | 64 | -1.1231 | -1.103 | -1.289 | -1.8 | 0.07186 | -1.82 | -0.58 | -0.6003 | -1.3931 | 0 | None | None | ne | odbaceno |
| stocks:REV5:2w:short | 155 | -0.7761 | -0.4528 | -0.8573 | -1.83 | 0.06725 | -1.34 | -1.25 | 0.4779 | -1.0461 | - | - | - | ne | odbaceno |
| stocks:LOWVOL:1w:short | 300 | -0.4762 | -0.0087 | -0.516 | -1.85 | 0.06431 | -1.19 | -1.43 | 0.0056 | -0.7462 | - | - | - | ne | odbaceno |
| stocks:LOWVOL:4w:short | 74 | -2.4596 | -0.1734 | -2.7389 | -1.88 | 0.06011 | -0.66 | -1.89 | -1.1319 | -2.7296 | - | - | - | ne | odbaceno |
| stocks:BRK20:4w:short | 76 | -2.8456 | -0.4241 | -3.0794 | -1.94 | 0.05238 | -1.46 | -1.45 | -2.6972 | -3.1156 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:5d:long | 170 | -1.1195 | -1.8772 | -1.3131 | -1.95 | 0.05118 | -1.21 | -1.64 | -0.0045 | -1.3895 | - | - | - | ne | odbaceno |
| crypto:VOLUP:4w:long | 80 | -2.3533 | -1.2836 | -2.9146 | -1.95 | 0.05118 | -1.8 | -0.75 | -5.8543 | -2.6233 | 74 | -3.7275 | -1.79 | ne | odbaceno |
| commodities:HIGH_BRK:20d:short | 12 | -5.9393 | -2.584 | -6.9562 | -1.95 | None | -1.71 | -1.4 | -2.1703 | -6.2093 | 0 | None | None | ne | premalo |
| alts:HIGH52:2w:short | 145 | -0.9635 | -0.5089 | -1.0879 | -2.02 | 0.04338 | -1.11 | -1.82 | -2.8084 | -1.2335 | 0 | None | None | ne | odbaceno |
| crypto:ATTN:1w:long | 319 | -0.8142 | -1.1507 | -0.9374 | -2.03 | 0.04236 | -1.41 | -1.67 | -1.6296 | -1.0842 | 288 | 0.0345 | 0.08 | ne | odbaceno |
| stocks:LOWVOL:4w:long | 74 | -1.49 | -1.5461 | -1.6905 | -2.04 | 0.04135 | -1.09 | -1.77 | -0.728 | -1.76 | - | - | - | ne | odbaceno |
| commodities:VOLUP:2w:long | 153 | -0.5446 | -0.5897 | -0.6168 | -2.04 | 0.04135 | -1.46 | -1.41 | -0.3318 | -0.8146 | 0 | None | None | ne | odbaceno |
| commodities:MOM12_1:2w:short | 129 | -0.5991 | -0.5984 | -0.6951 | -2.06 | 0.0394 | -2.76 | -0.12 | -0.6498 | -0.8691 | 0 | None | None | ne | odbaceno |
| commodities:REV5:1w:short | 311 | -0.325 | -0.301 | -0.355 | -2.08 | 0.03753 | -1.75 | -1.16 | -0.7973 | -0.595 | 0 | None | None | ne | odbaceno |
| commodities:HIGH_BRK:10d:short | 23 | -2.837 | -2.0238 | -3.4036 | -2.11 | None | -1.94 | -0.86 | -1.3837 | -3.107 | 0 | None | None | ne | premalo |
| alts:ATTN:4w:long | 79 | -2.217 | -3.032 | -2.7105 | -2.12 | 0.03401 | -0.51 | -3.03 | -4.9181 | -2.487 | 0 | None | None | ne | odbaceno |
| stocks:LOWVOL:2w:short | 149 | -1.1569 | -0.6127 | -1.2606 | -2.13 | 0.03317 | -1.11 | -1.88 | 0.039 | -1.4269 | - | - | - | ne | odbaceno |
| alts:SPIKE_UP:14d:long | 159 | -2.9146 | -6.871 | -3.4478 | -2.17 | 0.03001 | -2.43 | -0.56 | -5.7905 | -3.1846 | 0 | None | None | ne | odbaceno |
| alts:HIGH52:1w:short | 291 | -0.4918 | -0.2589 | -0.5265 | -2.22 | 0.02642 | -2.12 | -0.96 | -0.2592 | -0.7618 | 0 | None | None | ne | odbaceno |
| stocks:REV5:1w:short | 311 | -0.3992 | -0.2291 | -0.4272 | -2.23 | 0.02575 | -1.83 | -1.29 | 0.0394 | -0.6692 | - | - | - | ne | odbaceno |
| commodities:VOLUP:4w:short | 76 | -1.4494 | -0.8652 | -1.6162 | -2.35 | 0.01877 | -2.55 | -0.85 | -4.711 | -1.7194 | 0 | None | None | da | odbaceno |
| stocks:LOWVOL:2w:long | 149 | -0.7697 | -0.9084 | -0.8519 | -2.37 | 0.01779 | -1.43 | -1.91 | -0.7023 | -1.0397 | - | - | - | da | odbaceno |
| commodities:LOWVOL:1w:short | 300 | -0.454 | -0.2677 | -0.4814 | -2.38 | 0.01731 | -1.37 | -2.0 | -0.5291 | -0.724 | 0 | None | None | da | odbaceno |
| crypto:REV5:4w:long | 80 | -2.8928 | -2.2545 | -3.2919 | -2.4 | 0.0164 | -0.97 | -2.93 | -2.5747 | -3.1628 | 74 | 0.2449 | 0.21 | da | odbaceno |
| stocks:LOWVOL:1w:long | 300 | -0.393 | -0.208 | -0.4224 | -2.43 | 0.0151 | -1.84 | -1.6 | -0.1316 | -0.663 | - | - | - | da | odbaceno |
| commodities:ATTN:1w:long | 300 | -0.2801 | -0.2856 | -0.3005 | -2.43 | 0.0151 | -2.18 | -1.22 | 0.1326 | -0.5501 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_UP:7d:long | 223 | -2.4542 | -3.6981 | -2.8308 | -2.47 | 0.01351 | -0.5 | -4.03 | -7.0431 | -2.7242 | 118 | -3.1709 | -3.07 | da | odbaceno |
| crypto:VOLUP:1w:long | 323 | -0.8888 | -1.0497 | -1.0384 | -2.49 | 0.01277 | -1.15 | -2.97 | -1.6862 | -1.1588 | 299 | -0.4701 | -1.25 | da | odbaceno |
| alts:HIGH52:2w:long | 145 | -1.1987 | -0.8292 | -1.3087 | -2.51 | 0.01207 | -1.45 | -2.1 | -3.1404 | -1.4687 | 0 | None | None | da | odbaceno |
| alts:REV5:1w:long | 323 | -0.5397 | -0.9198 | -0.6469 | -2.51 | 0.01207 | -0.88 | -3.33 | -0.6026 | -0.8097 | 3 | 3.0111 | 1.02 | da | odbaceno |
| crypto:MOM12_1:1w:long | 291 | -0.7527 | -0.96 | -0.8058 | -2.54 | 0.01109 | -1.66 | -2.04 | -1.7567 | -1.0227 | 253 | -0.0879 | -0.29 | da | odbaceno |
| alts:VOLUP:1w:short | 323 | -0.5412 | -0.2247 | -0.5925 | -2.65 | 0.00805 | -2.43 | -1.17 | -0.2238 | -0.8112 | 3 | 0.1022 | 0.06 | da | odbaceno |
| alts:SPIKE_DN:7d:long | 272 | -3.4567 | -6.6887 | -4.2632 | -2.69 | 0.00715 | -1.65 | -2.49 | -6.0655 | -3.7267 | 0 | None | None | da | odbaceno |
| commodities:BRK20:2w:long | 153 | -0.6714 | -0.7177 | -0.7298 | -2.73 | 0.00633 | -1.54 | -2.39 | -0.8309 | -0.9414 | 0 | None | None | da | odbaceno |
| alts:HIGH52:1w:long | 291 | -0.7178 | -0.8434 | -0.8163 | -2.78 | 0.00544 | -1.83 | -2.13 | -1.6775 | -0.9878 | 0 | None | None | da | odbaceno |
| alts:BRK20:1w:long | 323 | -0.6162 | -0.8342 | -0.6849 | -2.78 | 0.00544 | -1.61 | -2.57 | -0.8055 | -0.8862 | 3 | -3.798 | -0.67 | da | odbaceno |
| crypto:ATTN:4w:long | 79 | -3.2565 | -3.0239 | -3.6177 | -2.79 | 0.00527 | -2.42 | -1.41 | -10.5631 | -3.5265 | 71 | 3.0175 | 1.55 | da | odbaceno |
| crypto:SPIKE_DN:7d:long | 128 | -5.7876 | -7.3466 | -6.8012 | -2.84 | 0.00451 | -0.89 | -3.14 | -13.7167 | -6.0576 | 40 | -0.2303 | -0.06 | da | odbaceno |
| commodities:VOLUP:1w:short | 308 | -0.3978 | -0.4479 | -0.4242 | -2.93 | 0.00339 | -2.9 | -1.11 | 0.2746 | -0.6678 | 0 | None | None | da | odbaceno |
| commodities:MOM12_1:1w:short | 260 | -0.4448 | -0.328 | -0.4791 | -2.95 | 0.00318 | -2.94 | -1.09 | -0.6065 | -0.7148 | 0 | None | None | da | odbaceno |
| commodities:HIGH52:1w:long | 260 | -0.3907 | -0.2352 | -0.4132 | -3.01 | 0.00261 | -2.23 | -2.02 | -0.8111 | -0.6607 | 0 | None | None | da | odbaceno |
| alts:VOLUP:2w:long | 161 | -1.4633 | -1.7199 | -1.6417 | -3.03 | 0.00245 | -1.48 | -3.55 | -2.5292 | -1.7333 | 2 | None | None | da | odbaceno |
| commodities:BRK20:1w:short | 308 | -0.4524 | -0.4479 | -0.4833 | -3.07 | 0.00214 | -2.59 | -1.73 | -0.0789 | -0.7224 | 0 | None | None | da | odbaceno |
| commodities:LOWVOL:1w:long | 300 | -0.3113 | -0.2604 | -0.3286 | -3.07 | 0.00214 | -2.49 | -1.79 | -0.3262 | -0.5813 | 0 | None | None | da | odbaceno |
| stocks:VOLUP:1w:short | 308 | -0.4831 | -0.2834 | -0.5131 | -3.1 | 0.00194 | -2.64 | -1.64 | -0.8565 | -0.7531 | - | - | - | da | odbaceno |
| commodities:SPIKE_UP:5d:long | 72 | -1.5258 | -2.0412 | -1.7868 | -3.1 | 0.00194 | -1.75 | -2.88 | -2.9285 | -1.7958 | 0 | None | None | da | odbaceno |
| commodities:BRK20:1w:long | 308 | -0.4395 | -0.2883 | -0.469 | -3.21 | 0.00133 | -2.79 | -1.74 | 0.1472 | -0.7095 | 0 | None | None | da | odbaceno |
| stocks:SPIKE_UP:10d:short | 96 | -6.327 | -2.1971 | -6.5819 | -3.31 | 0.00093 | -2.37 | -2.33 | 0.695 | -6.597 | - | - | - | da | odbaceno |
| crypto:SPIKE_DN:28d:long | 37 | -18.3068 | -17.4787 | -21.5337 | -3.51 | 0.00045 | -1.81 | -4.33 | -24.691 | -18.5768 | 9 | -5.0177 | -2.16 | da | odbaceno |
| commodities:VOLUP:1w:long | 308 | -0.4788 | -0.3943 | -0.5089 | -3.57 | 0.00036 | -3.05 | -1.91 | -0.0237 | -0.7488 | 0 | None | None | da | odbaceno |
| alts:ATTN:2w:long | 159 | -1.5736 | -1.7247 | -1.6743 | -3.8 | 0.00014 | -1.3 | -4.35 | -4.7945 | -1.8436 | 1 | None | None | da | odbaceno |
| alts:ATTN:1w:long | 319 | -1.0192 | -1.0847 | -1.153 | -3.85 | 0.00012 | -1.9 | -4.12 | -2.3399 | -1.2892 | 1 | None | None | da | odbaceno |
| commodities:HIGH52:2w:short | 129 | -1.3192 | -1.142 | -1.3913 | -3.97 | 7e-05 | -3.4 | -2.13 | -0.8207 | -1.5892 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:14d:long | 69 | -11.3132 | -12.7651 | -12.2162 | -4.21 | 3e-05 | -1.62 | -5.68 | -23.6872 | -11.5832 | 21 | -5.1248 | -1.08 | da | odbaceno |
| crypto:REV5:2w:long | 161 | -2.1928 | -2.6114 | -2.3418 | -4.36 | 1e-05 | -2.78 | -3.83 | -3.2057 | -2.4628 | 148 | -0.988 | -1.77 | da | odbaceno |
| commodities:HIGH52:1w:short | 260 | -0.7053 | -0.7538 | -0.732 | -4.44 | 1e-05 | -3.72 | -2.5 | -0.7422 | -0.9753 | 0 | None | None | da | odbaceno |
| alts:SPIKE_UP:7d:long | 321 | -2.8389 | -4.4375 | -2.9936 | -4.63 | 0.0 | -3.77 | -2.73 | -7.1291 | -3.1089 | 1 | None | None | da | odbaceno |
| alts:VOLUP:1w:long | 323 | -1.1419 | -1.2203 | -1.1993 | -5.25 | 0.0 | -3.46 | -4.14 | -1.8676 | -1.4119 | 3 | -2.1165 | -0.32 | da | odbaceno |
| crypto:REV5:1w:long | 323 | -1.4894 | -1.5817 | -1.565 | -5.77 | 0.0 | -4.45 | -3.7 | -2.3993 | -1.7594 | 299 | -0.9135 | -2.9 | da | odbaceno |
| alts:SPIKE_UP:3d:long | 323 | -2.8149 | -3.6808 | -2.9748 | -5.87 | 0.0 | -6.57 | -2.0 | -4.8952 | -3.0849 | 1 | None | None | da | odbaceno |

## Opisni slucaj: GME (vlasnikov ulaz 2026-10-03)

Gde je GME po svakoj rang-porodici na poslednjoj sveci pre ulaza (2026-10-02). Percentil 1.0 = najvise u univerzumu (od 66 clanova).

| porodica | ocena | percentil |
|---|---|---|
| MOM12_1 | -0.3149 | 0.092 |
| HIGH52 | 0.9074 | 0.708 |
| REV5 | -0.056 | 0.138 |
| VOLUP | 0.0326 | 0.831 |
| BRK20 | -0.0128 | 0.631 |
| LOWVOL | -0.0261 | 0.692 |
| ATTN | 1.4911 | 0.969 |

Dogadjaji u poslednjih 10 svecâ: nijedan.
