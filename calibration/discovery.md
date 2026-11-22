# Lovac: studija na sirem univerzumu (2026-11-22)

Univerzumi: stocks 64 instrumenata (2020-11-23 do 2026-11-20); crypto 417 instrumenata (2020-08-06 do 2026-11-21); alts 571 instrumenata (2020-08-06 do 2026-11-21); commodities 20 instrumenata (2020-11-23 do 2026-11-20).
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
| crypto:BRK20:2w:short | 161 | 3.2464 | 3.4741 | 3.1045 | 6.16 | 0.0 | 3.84 | 5.06 | 6.0092 | 2.9764 | 160 | 0.4196 | 0.5 | da | nagovestaj |
| crypto:BRK20:1w:short | 323 | 1.5635 | 1.6532 | 1.4873 | 5.48 | 0.0 | 3.67 | 4.39 | 2.8182 | 1.2935 | 321 | 0.3388 | 1.0 | da | kandidat |
| crypto:LOWVOL:2w:short | 159 | 3.5118 | 3.4856 | 3.3167 | 4.85 | 0.0 | 2.58 | 4.79 | 10.205 | 3.2418 | 156 | -0.4497 | -0.41 | da | nagovestaj |
| crypto:BRK20:4w:short | 80 | 5.1302 | 4.3084 | 4.6761 | 4.44 | 1e-05 | 2.18 | 4.68 | 9.1731 | 4.8602 | 79 | 1.7745 | 1.25 | da | kandidat |
| crypto:SPIKE_DN:14d:short | 69 | 10.6532 | 12.1051 | 9.6931 | 3.97 | 7e-05 | 1.44 | 5.49 | 23.0272 | 10.3832 | 24 | 2.5859 | 0.68 | da | kandidat |
| alts:SPIKE_UP:3d:short | 322 | 1.8795 | 2.7414 | 1.7708 | 3.91 | 9e-05 | 4.79 | 1.01 | 3.8427 | 1.6095 | 1 | None | None | da | kandidat |
| crypto:LOWVOL:1w:short | 318 | 1.4176 | 1.6011 | 1.3492 | 3.61 | 0.00031 | 1.59 | 4.57 | 4.3031 | 1.1476 | 312 | -0.4018 | -0.89 | da | nagovestaj |
| crypto:SPIKE_DN:28d:short | 37 | 17.6468 | 16.8187 | 16.2042 | 3.38 | 0.00072 | 1.72 | 4.21 | 24.031 | 17.3768 | 11 | 2.6057 | 1.09 | da | nagovestaj |
| alts:SPIKE_UP:7d:short | 320 | 1.9713 | 3.6483 | 1.8414 | 3.22 | 0.00128 | 2.45 | 2.08 | 6.1715 | 1.7013 | 1 | None | None | da | kandidat |
| crypto:BRK20:2w:long | 161 | 1.7976 | 1.3058 | 1.5709 | 3.17 | 0.00152 | 2.97 | 1.26 | 0.6787 | 1.5276 | 160 | 0.4565 | 0.54 | da | nagovestaj |
| crypto:LOWVOL:4w:short | 79 | 4.4097 | 4.7955 | 3.9374 | 3.02 | 0.00253 | 1.16 | 4.14 | 14.4873 | 4.1397 | 77 | -2.086 | -0.85 | da | nagovestaj |
| alts:LOWVOL:4w:long | 79 | 2.1556 | 1.0111 | 1.7783 | 2.97 | 0.00298 | 2.64 | 1.53 | -0.8295 | 1.8856 | 0 | None | None | da | nagovestaj |
| crypto:LOWVOL:2w:long | 159 | 1.2907 | 1.5536 | 1.1804 | 2.84 | 0.00451 | 0.74 | 4.39 | 2.7377 | 1.0207 | 156 | -0.5125 | -0.7 | da | nagovestaj |
| stocks:SPIKE_UP:10d:long | 96 | 5.3105 | 1.6268 | 4.1185 | 2.83 | 0.00465 | 2.27 | 1.66 | -1.0948 | 5.0405 | - | - | - | da | nagovestaj |
| crypto:SPIKE_DN:7d:short | 130 | 5.0039 | 6.3693 | 4.4889 | 2.49 | 0.01277 | 0.82 | 2.7 | 11.4602 | 4.7339 | 47 | -2.0351 | -0.57 | da | nagovestaj |
| crypto:LOWVOL:4w:long | 79 | 2.958 | 4.1021 | 2.6453 | 2.42 | 0.01552 | 0.62 | 4.39 | 3.1493 | 2.688 | 77 | 0.1767 | 0.08 | da | nagovestaj |
| alts:SPIKE_DN:7d:short | 272 | 2.7632 | 6.1286 | 2.4825 | 2.15 | 0.03156 | 1.05 | 2.48 | 6.0278 | 2.4932 | 0 | None | None | ne | nagovestaj |
| crypto:LOWVOL:1w:long | 318 | 0.5482 | 0.5916 | 0.4665 | 2.01 | 0.04443 | 0.7 | 2.52 | 0.9503 | 0.2782 | 312 | -0.4012 | -1.14 | ne | nagovestaj |
| alts:LOWVOL:4w:short | 79 | 1.8824 | 1.8639 | 1.6396 | 1.93 | 0.05361 | 0.36 | 3.24 | 4.8058 | 1.6124 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:7d:short | 220 | 1.846 | 3.0081 | 1.6574 | 1.85 | 0.06431 | 0.06 | 3.55 | 4.7855 | 1.576 | 134 | 0.5517 | 0.34 | ne | odbaceno |
| crypto:HIGH52:2w:short | 145 | 1.0676 | 0.8325 | 0.846 | 1.77 | 0.07673 | 1.16 | 1.4 | 1.9688 | 0.7976 | 144 | 0.644 | 1.0 | ne | odbaceno |
| commodities:HIGH_BRK:20d:long | 12 | 5.1793 | 1.824 | 2.8673 | 1.7 | None | 1.55 | 0.94 | 1.4103 | 4.9093 | 0 | None | None | ne | premalo |
| crypto:VOLUP:4w:short | 80 | 1.7675 | 1.0824 | 1.4356 | 1.69 | 0.09103 | 1.23 | 1.3 | 0.9321 | 1.4975 | 79 | -1.0503 | -0.66 | ne | odbaceno |
| alts:SPIKE_UP:14d:short | 159 | 2.1283 | 6.1115 | 1.9092 | 1.58 | 0.11411 | 1.78 | 0.4 | 4.9373 | 1.8583 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_UP:5d:short | 72 | 0.7658 | 1.2812 | 0.641 | 1.56 | 0.11876 | 0.61 | 1.81 | 2.1685 | 0.4958 | 0 | None | None | ne | odbaceno |
| commodities:HIGH_BRK:10d:long | 23 | 2.077 | 1.2638 | 1.2919 | 1.54 | None | 1.57 | 0.34 | 0.6237 | 1.807 | 0 | None | None | ne | premalo |
| stocks:VOLUP:2w:long | 153 | 0.4738 | 0.2205 | 0.3326 | 1.45 | 0.14706 | 0.96 | 1.07 | 0.7233 | 0.2038 | - | - | - | ne | odbaceno |
| alts:LOWVOL:2w:long | 159 | 0.6202 | 0.3326 | 0.3587 | 1.42 | 0.15561 | 0.68 | 1.88 | 0.5968 | 0.3502 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:4w:long | 64 | 1.17 | 0.2452 | 0.8519 | 1.35 | 0.17702 | 0.07 | 1.66 | 0.4947 | 0.9 | - | - | - | ne | odbaceno |
| crypto:BRK20:1w:long | 323 | 0.4917 | 0.4804 | 0.3505 | 1.33 | 0.18352 | 1.19 | 0.62 | -0.4075 | 0.2217 | 321 | 0.1805 | 0.42 | ne | odbaceno |
| alts:LOWVOL:2w:short | 159 | 0.7182 | 1.1143 | 0.5945 | 1.33 | 0.18352 | -0.35 | 3.06 | 1.8856 | 0.4482 | 0 | None | None | ne | odbaceno |
| crypto:HIGH52:2w:long | 145 | 0.7925 | 0.4797 | 0.588 | 1.32 | 0.18684 | 1.43 | 0.21 | -0.9954 | 0.5225 | 144 | -0.035 | -0.06 | ne | odbaceno |
| crypto:HIGH_BRK:7d:short | 114 | 2.4592 | 1.9095 | 1.8668 | 1.3 | 0.1936 | 1.84 | -0.07 | 10.2705 | 2.1892 | 71 | -3.3169 | -1.99 | ne | odbaceno |
| crypto:SPIKE_UP:14d:short | 110 | 2.1133 | 2.3824 | 1.6037 | 1.26 | 0.20767 | -0.04 | 2.1 | 3.7992 | 1.8433 | 63 | -3.1831 | -1.28 | ne | odbaceno |
| crypto:HIGH52:4w:short | 72 | 1.3955 | 2.3369 | 1.0864 | 1.11 | 0.267 | 0.32 | 1.75 | 3.2143 | 1.1255 | 71 | 1.6011 | 1.33 | ne | odbaceno |
| crypto:ATTN:2w:short | 159 | 0.5557 | 0.1157 | 0.4187 | 1.11 | 0.267 | 0.31 | 1.93 | 0.4113 | 0.2857 | 156 | 0.1573 | 0.2 | ne | odbaceno |
| crypto:VOLUP:2w:short | 161 | 0.5898 | 0.9674 | 0.4156 | 1.09 | 0.27571 | 1.08 | 0.36 | 2.4367 | 0.3198 | 160 | -1.1081 | -1.46 | ne | odbaceno |
| crypto:MOM12_1:4w:short | 72 | 1.2561 | 3.1999 | 0.983 | 1.05 | 0.29372 | 0.01 | 2.38 | 2.952 | 0.9861 | 71 | 1.2315 | 0.92 | ne | odbaceno |
| alts:HIGH_BRK:14d:short | 79 | 2.7574 | 3.1251 | 1.9941 | 1.02 | 0.30773 | 0.47 | 0.93 | 8.2069 | 2.4874 | 0 | None | None | ne | odbaceno |
| alts:BRK20:4w:short | 80 | 0.892 | 0.0093 | 0.3478 | 0.89 | 0.37347 | 0.56 | 1.0 | -1.1158 | 0.622 | 1 | None | None | ne | odbaceno |
| crypto:BRK20:4w:long | 80 | 1.0768 | 2.6786 | 0.6839 | 0.87 | 0.3843 | 0.07 | 1.58 | -1.5877 | 0.8068 | 79 | 0.466 | 0.27 | ne | odbaceno |
| alts:LOWVOL:1w:short | 318 | 0.2243 | 0.3494 | 0.181 | 0.84 | 0.40091 | -1.46 | 3.48 | 1.6559 | -0.0457 | 0 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:14d:short | 61 | 2.7781 | 4.0441 | 1.5358 | 0.81 | 0.41794 | 0.69 | 0.43 | 9.6958 | 2.5081 | 37 | -3.3755 | -1.18 | ne | odbaceno |
| stocks:SPIKE_DN:20d:short | 41 | 1.6355 | 3.0559 | 1.1005 | 0.78 | 0.43539 | 0.64 | 0.44 | 4.8286 | 1.3655 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:5d:short | 170 | 0.4501 | 1.3986 | 0.2182 | 0.77 | 0.4413 | 0.34 | 0.84 | -0.7132 | 0.1801 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:long | 67 | 0.961 | 0.4024 | 0.3762 | 0.77 | 0.4413 | 0.36 | 0.79 | -0.1846 | 0.691 | - | - | - | ne | odbaceno |
| stocks:VOLUP:4w:long | 76 | 0.6032 | 0.1442 | 0.1155 | 0.75 | 0.45325 | 0.82 | 0.29 | -2.5943 | 0.3332 | - | - | - | ne | odbaceno |
| crypto:REV5:4w:short | 80 | 1.1412 | 1.6261 | 0.709 | 0.74 | 0.4593 | 1.06 | -0.34 | 7.5154 | 0.8712 | 79 | -2.4946 | -1.02 | ne | odbaceno |
| alts:ATTN:4w:short | 79 | 0.6879 | 0.7107 | 0.2442 | 0.73 | 0.46539 | 0.42 | 1.02 | 2.6283 | 0.4179 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:5d:long | 199 | 0.501 | -0.2457 | 0.2144 | 0.71 | 0.4777 | 0.38 | 0.61 | -1.6705 | 0.231 | - | - | - | ne | odbaceno |
| stocks:MOM12_1:2w:long | 129 | 0.3001 | 0.0112 | 0.1699 | 0.7 | 0.48393 | 0.28 | 0.68 | 0.0815 | 0.0301 | - | - | - | ne | odbaceno |
| crypto:ATTN:1w:short | 319 | 0.2007 | 0.2422 | 0.1404 | 0.7 | 0.48393 | -0.41 | 2.29 | 0.3838 | -0.0693 | 313 | -0.3044 | -0.66 | ne | odbaceno |
| commodities:SPIKE_UP:10d:short | 36 | 0.6842 | 2.0844 | 0.3747 | 0.6 | 0.54851 | 0.39 | 0.46 | 0.0485 | 0.4142 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:28d:short | 54 | 2.1913 | 6.3574 | 0.4534 | 0.58 | 0.56191 | -1.22 | 2.44 | 11.3168 | 1.9213 | 24 | -2.5944 | -0.6 | ne | odbaceno |
| alts:VOLUP:4w:short | 80 | 0.4026 | 0.4796 | 0.1801 | 0.57 | 0.56868 | -0.16 | 1.33 | 2.5946 | 0.1326 | 1 | None | None | ne | odbaceno |
| alts:SPIKE_DN:14d:short | 134 | 1.6579 | 6.5421 | 1.3436 | 0.57 | 0.56868 | 2.67 | -0.45 | 7.4214 | 1.3879 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:4w:short | 74 | 0.3019 | -0.2451 | 0.0471 | 0.55 | 0.58232 | 0.13 | 0.62 | 2.3541 | 0.0319 | 0 | None | None | ne | odbaceno |
| crypto:MOM12_1:2w:short | 145 | 0.3749 | 1.2938 | 0.1999 | 0.54 | 0.5892 | -0.42 | 1.94 | 0.6873 | 0.1049 | 144 | 0.2846 | 0.48 | ne | odbaceno |
| crypto:HIGH52:1w:short | 291 | 0.1414 | 0.5963 | 0.0519 | 0.5 | 0.61708 | 0.89 | -0.29 | -0.2427 | -0.1286 | 286 | 0.072 | 0.24 | ne | odbaceno |
| crypto:HIGH52:4w:long | 72 | 0.6623 | 0.4927 | 0.0623 | 0.49 | 0.62413 | 0.55 | 0.04 | -3.7946 | 0.3923 | 71 | -0.413 | -0.25 | ne | odbaceno |
| stocks:SPIKE_UP:20d:long | 50 | 1.3308 | -0.6464 | -0.1855 | 0.47 | 0.63836 | 0.96 | -0.48 | -9.495 | 1.0608 | - | - | - | ne | odbaceno |
| alts:ATTN:2w:short | 159 | 0.1851 | 0.0031 | -0.0324 | 0.43 | 0.6672 | 0.3 | 0.37 | -0.3227 | -0.0849 | 0 | None | None | ne | odbaceno |
| stocks:HIGH_BRK:20d:short | 31 | 0.8768 | -0.5947 | -0.4335 | 0.39 | 0.69654 | 0.14 | 0.55 | -4.6969 | 0.6068 | - | - | - | ne | odbaceno |
| commodities:MOM12_1:4w:long | 64 | 0.2858 | 0.4189 | 0.0806 | 0.37 | 0.71138 | 0.34 | 0.18 | 0.6393 | 0.0158 | 0 | None | None | ne | odbaceno |
| alts:BRK20:4w:long | 80 | 0.3743 | -0.2257 | -0.3149 | 0.34 | 0.73386 | 0.8 | -0.82 | -0.9003 | 0.1043 | 1 | None | None | ne | odbaceno |
| alts:SPIKE_DN:3d:short | 273 | 0.4446 | 3.6929 | 0.253 | 0.31 | 0.75656 | 0.37 | -0.03 | 0.2812 | 0.1746 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:2w:long | 149 | 0.0747 | -0.4125 | -0.0048 | 0.3 | 0.76418 | 0.38 | -0.02 | -0.137 | -0.1953 | - | - | - | ne | odbaceno |
| stocks:REV5:4w:long | 77 | 0.3315 | -1.2402 | -0.9049 | 0.24 | 0.81033 | 0.57 | -0.85 | -0.9922 | 0.0615 | - | - | - | ne | odbaceno |
| alts:HIGH_BRK:7d:long | 159 | 0.4561 | -2.4756 | -0.4576 | 0.23 | 0.81809 | 0.69 | -0.3 | 2.3524 | 0.1861 | 0 | None | None | ne | odbaceno |
| alts:REV5:1w:short | 323 | 0.0511 | 0.1664 | -0.0102 | 0.19 | 0.84931 | -0.28 | 0.75 | 1.6301 | -0.2189 | 2 | None | None | ne | odbaceno |
| commodities:BRK20:4w:short | 76 | 0.1043 | -0.2831 | -0.1037 | 0.17 | 0.86501 | 0.8 | -0.49 | -3.3305 | -0.1657 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:5d:long | 72 | 0.1014 | 0.0606 | -0.0884 | 0.17 | 0.86501 | -0.03 | 0.27 | -1.7797 | -0.1686 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:20d:short | 15 | 0.2857 | 1.4465 | -0.6404 | 0.15 | None | -0.3 | 1.3 | 3.0496 | 0.0157 | 0 | None | None | ne | premalo |
| stocks:REV5:4w:short | 77 | 0.086 | -0.2115 | -0.1613 | 0.13 | 0.89657 | 0.13 | 0.04 | 2.8936 | -0.184 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:5d:short | 133 | 0.0895 | 0.1536 | -0.2421 | 0.13 | 0.89657 | -0.39 | 0.51 | 1.8046 | -0.1805 | - | - | - | ne | odbaceno |
| crypto:ATTN:4w:short | 79 | 0.0929 | 0.8914 | -0.1839 | 0.1 | 0.92034 | -0.58 | 1.45 | 1.0561 | -0.1771 | 77 | -2.3455 | -1.26 | ne | odbaceno |
| alts:BRK20:1w:short | 323 | 0.0191 | -0.0776 | -0.0407 | 0.1 | 0.92034 | -0.43 | 0.82 | 0.6775 | -0.2509 | 2 | None | None | ne | odbaceno |
| crypto:HIGH_BRK:28d:short | 27 | 0.7223 | 6.4546 | -1.615 | 0.09 | None | -0.09 | 0.24 | 21.0613 | 0.4523 | 15 | -6.1983 | -0.91 | ne | premalo |
| commodities:REV5:2w:long | 155 | 0.0111 | 0.0608 | -0.0729 | 0.04 | 0.96809 | -0.43 | 0.51 | -0.404 | -0.2589 | 0 | None | None | ne | odbaceno |
| crypto:VOLUP:1w:short | 323 | 0.0095 | 0.5 | -0.0409 | 0.03 | 0.97607 | 0.37 | -0.43 | 0.7078 | -0.2605 | 321 | -0.5658 | -1.76 | ne | odbaceno |
| stocks:SPIKE_DN:10d:short | 80 | -0.1002 | 0.6633 | -0.5438 | -0.05 | 0.96012 | -0.76 | 1.35 | 4.2782 | -0.3702 | - | - | - | ne | odbaceno |
| alts:LOWVOL:1w:long | 318 | -0.0216 | 0.1118 | -0.0885 | -0.11 | 0.91241 | -1.73 | 2.66 | 0.6043 | -0.2916 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:10d:short | 38 | -0.1177 | 0.5893 | -0.8475 | -0.11 | 0.91241 | -1.05 | 0.76 | 0.1184 | -0.3877 | 0 | None | None | ne | odbaceno |
| crypto:MOM12_1:1w:short | 291 | -0.0358 | 0.2493 | -0.0857 | -0.12 | 0.90448 | -0.58 | 0.6 | -0.5312 | -0.3058 | 286 | -0.171 | -0.59 | ne | odbaceno |
| commodities:SPIKE_UP:20d:long | 22 | -0.3317 | -2.0889 | -2.3349 | -0.14 | None | -1.85 | 0.76 | 1.6125 | -0.6017 | 0 | None | None | ne | premalo |
| crypto:HIGH_BRK:28d:long | 27 | -1.3823 | -7.1146 | -6.816 | -0.17 | None | 0.03 | -0.29 | -21.7213 | -1.6523 | 15 | 5.5383 | 0.82 | ne | premalo |
| commodities:SPIKE_UP:20d:short | 22 | -0.4283 | 1.3289 | -0.9692 | -0.18 | None | 1.41 | -0.92 | -2.3725 | -0.6983 | 0 | None | None | ne | premalo |
| commodities:LOWVOL:4w:short | 74 | -0.1394 | 0.4913 | -0.3999 | -0.19 | 0.84931 | 0.41 | -0.65 | -1.8424 | -0.4094 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_DN:10d:long | 80 | -0.3598 | -1.1233 | -1.4449 | -0.2 | 0.84148 | 0.59 | -1.58 | -4.7382 | -0.6298 | - | - | - | ne | odbaceno |
| alts:REV5:2w:short | 161 | -0.1098 | 0.7363 | -0.2301 | -0.21 | 0.83367 | -0.82 | 0.89 | 2.2286 | -0.3798 | 1 | None | None | ne | odbaceno |
| alts:HIGH_BRK:3d:long | 159 | -0.3032 | -1.0944 | -0.6637 | -0.23 | 0.81809 | 0.32 | -0.64 | -5.4668 | -0.5732 | 0 | None | None | ne | odbaceno |
| commodities:MOM12_1:2w:long | 129 | -0.0867 | 0.3275 | -0.1586 | -0.23 | 0.81809 | 0.22 | -0.62 | -0.6515 | -0.3567 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:4w:short | 64 | -0.211 | 0.3621 | -0.3581 | -0.28 | 0.77948 | -0.5 | 0.31 | 1.059 | -0.481 | - | - | - | ne | odbaceno |
| stocks:MOM12_1:1w:long | 260 | -0.0622 | 0.1202 | -0.1099 | -0.29 | 0.77182 | -0.17 | -0.23 | -0.7387 | -0.3322 | - | - | - | ne | odbaceno |
| crypto:REV5:1w:short | 323 | -0.1091 | 0.3076 | -0.1742 | -0.29 | 0.77182 | -0.83 | 1.18 | 1.2318 | -0.3791 | 321 | -0.9353 | -2.24 | ne | odbaceno |
| crypto:MOM12_1:4w:long | 72 | -0.375 | -1.5434 | -0.8235 | -0.3 | 0.76418 | -0.06 | -0.48 | -0.8959 | -0.645 | 71 | 0.9689 | 0.67 | ne | odbaceno |
| alts:VOLUP:4w:long | 80 | -0.3214 | -0.345 | -0.9696 | -0.3 | 0.76418 | 0.11 | -1.01 | -0.2527 | -0.5914 | 1 | None | None | ne | odbaceno |
| stocks:ATTN:1w:short | 300 | -0.0387 | 0.1438 | -0.0664 | -0.31 | 0.75656 | -0.2 | -0.25 | 0.1654 | -0.3087 | - | - | - | ne | odbaceno |
| stocks:BRK20:1w:long | 308 | -0.0466 | 0.0885 | -0.0946 | -0.32 | 0.74897 | 0.15 | -0.6 | -0.1885 | -0.3166 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:short | 49 | -0.2579 | -0.2967 | -0.6322 | -0.36 | 0.71885 | -1.11 | 0.64 | 0.2112 | -0.5279 | 0 | None | None | ne | odbaceno |
| crypto:REV5:2w:short | 161 | -0.2312 | 0.2227 | -0.404 | -0.38 | 0.70395 | -0.86 | 0.67 | 3.4465 | -0.5012 | 160 | -1.2058 | -1.57 | ne | odbaceno |
| stocks:BRK20:4w:long | 76 | -0.2763 | -0.0522 | -0.4123 | -0.43 | 0.6672 | 0.08 | -0.74 | -0.9404 | -0.5463 | - | - | - | ne | odbaceno |
| alts:VOLUP:2w:short | 161 | -0.1691 | 0.0072 | -0.2743 | -0.43 | 0.6672 | 0.26 | -1.09 | 0.0649 | -0.4391 | 1 | None | None | ne | odbaceno |
| alts:HIGH_BRK:3d:short | 159 | -0.5568 | 0.2344 | -0.7771 | -0.43 | 0.6672 | -0.88 | 0.27 | 4.6068 | -0.8268 | 0 | None | None | ne | odbaceno |
| alts:MOM12_1:4w:long | 72 | -0.4182 | -0.0263 | -0.7473 | -0.45 | 0.65271 | -0.17 | -0.51 | -3.3731 | -0.6882 | 0 | None | None | ne | odbaceno |
| stocks:VOLUP:1w:long | 308 | -0.0761 | -0.1621 | -0.1229 | -0.46 | 0.64552 | 0.13 | -0.76 | -0.2517 | -0.3461 | - | - | - | ne | odbaceno |
| stocks:ATTN:2w:short | 149 | -0.1318 | -0.0805 | -0.1899 | -0.52 | 0.60306 | 0.59 | -1.76 | -0.4286 | -0.4018 | - | - | - | ne | odbaceno |
| commodities:ATTN:2w:long | 149 | -0.1244 | 0.0313 | -0.1708 | -0.52 | 0.60306 | -1.07 | 0.38 | 1.2618 | -0.3944 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:20d:long | 15 | -1.0457 | -2.2065 | -2.3448 | -0.53 | None | 0.05 | -1.76 | -3.8096 | -1.3157 | 0 | None | None | ne | premalo |
| commodities:HIGH52:4w:long | 64 | -0.3267 | 0.3541 | -0.5851 | -0.55 | 0.58232 | 0.69 | -1.42 | -4.1848 | -0.5967 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_DN:10d:long | 38 | -0.6423 | -1.3493 | -1.0645 | -0.58 | 0.56191 | 0.43 | -1.15 | -0.8784 | -0.9123 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:4w:long | 64 | -0.3784 | -0.0654 | -0.6044 | -0.59 | 0.55519 | -1.46 | 0.47 | 1.8507 | -0.6484 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:20d:long | 31 | -1.3368 | 0.1347 | -2.0283 | -0.59 | 0.55519 | -0.27 | -0.73 | 4.2369 | -1.6068 | - | - | - | ne | odbaceno |
| alts:REV5:2w:long | 161 | -0.2395 | -0.746 | -0.403 | -0.61 | 0.54186 | 0.35 | -2.4 | -0.3194 | -0.5095 | 1 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:20d:short | 50 | -1.7908 | 0.1864 | -2.4157 | -0.63 | 0.52869 | -1.08 | 0.37 | 9.035 | -2.0608 | - | - | - | ne | odbaceno |
| alts:BRK20:2w:short | 161 | -0.2648 | -0.2213 | -0.4386 | -0.64 | 0.52217 | -0.81 | 0.16 | -0.1471 | -0.5348 | 1 | None | None | ne | odbaceno |
| crypto:HIGH52:1w:long | 291 | -0.2164 | -0.2185 | -0.3039 | -0.65 | 0.51569 | -0.23 | -0.81 | -1.216 | -0.4864 | 286 | -0.2719 | -0.87 | ne | odbaceno |
| alts:HIGH_BRK:7d:short | 159 | -1.3161 | 1.6156 | -1.6369 | -0.65 | 0.51569 | -1.07 | 0.07 | -3.2124 | -1.5861 | 0 | None | None | ne | odbaceno |
| stocks:REV5:2w:long | 155 | -0.225 | -0.6839 | -0.3238 | -0.67 | 0.50286 | 0.63 | -1.75 | -0.5028 | -0.495 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:5d:long | 49 | -0.5021 | -0.4633 | -0.8689 | -0.69 | 0.49019 | 0.25 | -1.26 | -0.9712 | -0.7721 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:2w:short | 129 | -0.2499 | -0.2738 | -0.3281 | -0.7 | 0.48393 | -0.9 | 0.11 | 0.5643 | -0.5199 | - | - | - | ne | odbaceno |
| commodities:REV5:4w:short | 77 | -0.4321 | -0.225 | -0.6295 | -0.71 | 0.4777 | 0.12 | -1.04 | 1.3875 | -0.7021 | 0 | None | None | ne | odbaceno |
| stocks:REV5:1w:long | 311 | -0.1163 | -0.3914 | -0.1563 | -0.73 | 0.46539 | 0.09 | -1.14 | 0.1028 | -0.3863 | - | - | - | ne | odbaceno |
| crypto:SPIKE_UP:28d:long | 54 | -2.8513 | -7.0174 | -4.2327 | -0.75 | 0.45325 | 1.07 | -2.56 | -11.9768 | -3.1213 | 24 | 1.9344 | 0.44 | ne | odbaceno |
| commodities:ATTN:2w:short | 149 | -0.2182 | -0.3752 | -0.2835 | -0.77 | 0.4413 | -1.49 | 0.42 | 1.1086 | -0.4882 | 0 | None | None | ne | odbaceno |
| commodities:LOWVOL:4w:long | 74 | -0.3404 | -0.4446 | -0.4736 | -0.78 | 0.43539 | -0.32 | -0.77 | -0.7738 | -0.6104 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:4w:long | 74 | -0.3693 | -0.4571 | -0.4869 | -0.78 | 0.43539 | -0.62 | -0.47 | 2.0835 | -0.6393 | 0 | None | None | ne | odbaceno |
| stocks:HIGH_BRK:5d:long | 133 | -0.5495 | -0.6136 | -0.7925 | -0.8 | 0.42371 | -0.21 | -0.87 | -2.2646 | -0.8195 | - | - | - | ne | odbaceno |
| alts:MOM12_1:2w:long | 145 | -0.3752 | -0.2939 | -0.538 | -0.86 | 0.38979 | -0.08 | -1.4 | -2.4788 | -0.6452 | 0 | None | None | ne | odbaceno |
| alts:SPIKE_DN:14d:long | 134 | -2.5179 | -7.4021 | -5.0587 | -0.86 | 0.38979 | -3.14 | 0.32 | -8.2814 | -2.7879 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:2w:long | 129 | -0.2719 | -0.3413 | -0.3513 | -0.89 | 0.37347 | -1.94 | 0.6 | 0.3575 | -0.5419 | - | - | - | ne | odbaceno |
| alts:SPIKE_DN:3d:long | 273 | -1.3046 | -4.5529 | -2.3789 | -0.9 | 0.36812 | -0.77 | -0.46 | -1.1412 | -1.5746 | 0 | None | None | ne | odbaceno |
| stocks:VOLUP:4w:short | 76 | -1.24 | 0.612 | -1.4632 | -0.97 | 0.33205 | -0.73 | -0.87 | -2.5589 | -1.51 | - | - | - | ne | odbaceno |
| alts:MOM12_1:2w:short | 145 | -0.437 | 0.2394 | -0.5178 | -0.99 | 0.32217 | -0.9 | -0.42 | -1.1946 | -0.707 | 0 | None | None | ne | odbaceno |
| stocks:ATTN:1w:long | 300 | -0.1262 | -0.1902 | -0.1598 | -1.0 | 0.31731 | -0.88 | -0.51 | -0.0225 | -0.3962 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:20d:long | 41 | -2.0955 | -3.5159 | -3.1378 | -1.0 | 0.31731 | -0.82 | -0.57 | -5.2886 | -2.3655 | - | - | - | ne | odbaceno |
| crypto:HIGH_BRK:14d:long | 61 | -3.4381 | -4.7041 | -4.9151 | -1.0 | 0.31731 | -0.83 | -0.55 | -10.3558 | -3.7081 | 37 | 2.7155 | 0.95 | ne | odbaceno |
| alts:REV5:4w:long | 80 | -0.7286 | -1.1187 | -1.0369 | -1.03 | 0.30301 | 0.04 | -1.89 | 0.2305 | -0.9986 | 1 | None | None | ne | odbaceno |
| stocks:BRK20:2w:short | 153 | -0.4857 | -0.2978 | -0.5629 | -1.05 | 0.29372 | -1.15 | -0.19 | 0.1067 | -0.7557 | - | - | - | ne | odbaceno |
| commodities:LOWVOL:2w:short | 149 | -0.4217 | -0.418 | -0.5164 | -1.1 | 0.27133 | -0.11 | -1.41 | -0.8445 | -0.6917 | 0 | None | None | ne | odbaceno |
| stocks:MOM12_1:1w:short | 260 | -0.2031 | -0.0392 | -0.2317 | -1.12 | 0.26271 | -1.14 | -0.29 | 0.0148 | -0.4731 | - | - | - | ne | odbaceno |
| alts:MOM12_1:4w:short | 72 | -1.1138 | 0.5401 | -1.33 | -1.13 | 0.25848 | -0.59 | -1.08 | -1.9848 | -1.3838 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:4w:short | 64 | -1.1695 | -0.0418 | -1.419 | -1.14 | 0.25429 | -1.07 | -0.5 | 2.4557 | -1.4395 | - | - | - | ne | odbaceno |
| stocks:HIGH_BRK:10d:short | 67 | -1.421 | -0.8624 | -1.8864 | -1.14 | 0.25429 | -0.63 | -1.03 | -0.2754 | -1.691 | - | - | - | ne | odbaceno |
| crypto:MOM12_1:2w:long | 145 | -0.7484 | -0.5767 | -0.9828 | -1.16 | 0.24605 | -1.25 | -0.36 | -1.5639 | -1.0184 | 144 | 0.1497 | 0.24 | ne | odbaceno |
| stocks:ATTN:4w:short | 74 | -0.6635 | -0.3962 | -0.8051 | -1.22 | 0.22246 | -0.49 | -1.18 | 0.9333 | -0.9335 | - | - | - | ne | odbaceno |
| alts:REV5:4w:short | 80 | -1.6076 | -1.1937 | -1.9557 | -1.25 | 0.2113 | -1.08 | -0.65 | 1.0137 | -1.8776 | 1 | None | None | ne | odbaceno |
| commodities:LOWVOL:2w:long | 149 | -0.2647 | -0.1335 | -0.313 | -1.25 | 0.2113 | -0.76 | -1.01 | -0.1016 | -0.5347 | 0 | None | None | ne | odbaceno |
| commodities:SPIKE_UP:10d:long | 36 | -1.4442 | -2.8444 | -2.0206 | -1.27 | 0.20408 | -1.12 | -0.78 | -0.8085 | -1.7142 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:2w:long | 153 | -0.3183 | -0.0859 | -0.3718 | -1.28 | 0.20055 | -1.42 | -0.48 | -0.9347 | -0.5883 | - | - | - | ne | odbaceno |
| alts:HIGH52:4w:long | 72 | -1.2608 | -0.2601 | -1.5232 | -1.28 | 0.20055 | -0.55 | -1.29 | -4.8431 | -1.5308 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:2w:short | 129 | -0.597 | -0.1191 | -0.6765 | -1.3 | 0.1936 | -1.47 | -0.29 | 1.2246 | -0.867 | - | - | - | ne | odbaceno |
| alts:MOM12_1:1w:long | 291 | -0.2713 | -0.3728 | -0.3112 | -1.3 | 0.1936 | -0.99 | -0.85 | -1.3252 | -0.5413 | 0 | None | None | ne | odbaceno |
| crypto:VOLUP:2w:long | 161 | -0.7895 | -1.3898 | -0.986 | -1.31 | 0.1902 | -0.58 | -1.41 | -0.9206 | -1.0595 | 160 | -0.6606 | -0.88 | ne | odbaceno |
| commodities:BRK20:4w:long | 76 | -0.6508 | -0.0816 | -0.7584 | -1.32 | 0.18684 | -1.11 | -0.78 | -3.7295 | -0.9208 | 0 | None | None | ne | odbaceno |
| stocks:BRK20:1w:short | 308 | -0.2543 | 0.0455 | -0.2876 | -1.34 | 0.18025 | -0.91 | -0.99 | -0.5155 | -0.5243 | - | - | - | ne | odbaceno |
| alts:HIGH_BRK:14d:long | 79 | -3.6174 | -3.9851 | -4.4689 | -1.34 | 0.18025 | -0.76 | -1.1 | -9.0669 | -3.8874 | 0 | None | None | ne | odbaceno |
| stocks:SPIKE_UP:5d:short | 199 | -0.961 | -0.2143 | -1.0968 | -1.36 | 0.17383 | -0.95 | -0.97 | 1.2105 | -1.231 | - | - | - | ne | odbaceno |
| commodities:VOLUP:4w:long | 76 | -0.7431 | -0.5578 | -0.9047 | -1.36 | 0.17383 | -1.26 | -0.64 | -0.8283 | -1.0131 | 0 | None | None | ne | odbaceno |
| commodities:REV5:2w:short | 155 | -0.4178 | -0.5687 | -0.5068 | -1.4 | 0.16151 | -1.39 | -0.58 | -0.6476 | -0.6878 | 0 | None | None | ne | odbaceno |
| crypto:ATTN:2w:long | 159 | -0.9497 | -0.903 | -1.1846 | -1.41 | 0.15854 | -0.74 | -1.51 | -5.1085 | -1.2197 | 156 | 1.8144 | 2.37 | ne | odbaceno |
| alts:MOM12_1:1w:short | 291 | -0.2868 | 0.015 | -0.3289 | -1.41 | 0.15854 | -1.67 | -0.12 | -0.1843 | -0.5568 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:1w:long | 260 | -0.2327 | -0.2281 | -0.2618 | -1.45 | 0.14706 | -2.4 | 0.26 | -0.2234 | -0.5027 | - | - | - | ne | odbaceno |
| commodities:SPIKE_DN:5d:short | 72 | -0.8614 | -0.8206 | -1.0795 | -1.45 | 0.14706 | -1.07 | -0.98 | 1.0197 | -1.1314 | 0 | None | None | ne | odbaceno |
| commodities:ATTN:1w:short | 300 | -0.1989 | -0.2468 | -0.236 | -1.46 | 0.14429 | -1.06 | -1.02 | 0.0807 | -0.4689 | 0 | None | None | ne | odbaceno |
| stocks:HIGH52:1w:short | 260 | -0.3292 | -0.096 | -0.3601 | -1.47 | 0.14156 | -1.51 | -0.47 | 0.1536 | -0.5992 | - | - | - | ne | odbaceno |
| stocks:REV5:2w:short | 155 | -0.595 | -0.3989 | -0.6736 | -1.5 | 0.13361 | -1.03 | -1.12 | 0.7668 | -0.865 | - | - | - | ne | odbaceno |
| stocks:SPIKE_DN:5d:long | 170 | -0.9101 | -1.8586 | -1.1019 | -1.56 | 0.11876 | -0.92 | -1.39 | 0.2532 | -1.1801 | - | - | - | ne | odbaceno |
| alts:HIGH52:4w:short | 72 | -1.6655 | 0.1091 | -1.9122 | -1.56 | 0.11876 | -0.53 | -1.85 | -5.3825 | -1.9355 | 0 | None | None | ne | odbaceno |
| commodities:MOM12_1:1w:long | 260 | -0.2746 | -0.1339 | -0.3042 | -1.56 | 0.11876 | -0.4 | -2.09 | -0.945 | -0.5446 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:2w:long | 129 | -0.4465 | -0.5038 | -0.537 | -1.56 | 0.11876 | -0.8 | -1.4 | -1.4314 | -0.7165 | 0 | None | None | ne | odbaceno |
| stocks:VOLUP:2w:short | 153 | -0.5949 | -0.1706 | -0.6798 | -1.58 | 0.11411 | -1.53 | -0.55 | -0.6936 | -0.8649 | - | - | - | ne | odbaceno |
| commodities:REV5:4w:long | 77 | -0.9113 | -1.4552 | -1.0734 | -1.62 | 0.10523 | -0.73 | -1.74 | 1.2768 | -1.1813 | 0 | None | None | ne | odbaceno |
| crypto:SPIKE_UP:14d:long | 110 | -2.7733 | -3.0424 | -3.2483 | -1.65 | 0.09894 | -0.26 | -2.35 | -4.4592 | -3.0433 | 63 | 2.5231 | 1.02 | ne | odbaceno |
| crypto:HIGH_BRK:7d:long | 114 | -3.1192 | -2.5695 | -3.7077 | -1.65 | 0.09894 | -2.12 | -0.14 | -10.9305 | -3.3892 | 71 | 2.6569 | 1.59 | ne | odbaceno |
| alts:BRK20:2w:long | 161 | -0.8328 | -1.1936 | -1.0996 | -1.65 | 0.09894 | -0.29 | -2.79 | -0.1958 | -1.1028 | 1 | None | None | ne | odbaceno |
| commodities:MOM12_1:4w:short | 64 | -1.0137 | -0.9552 | -1.1738 | -1.67 | 0.09492 | -2.04 | -0.07 | -1.6428 | -1.2837 | 0 | None | None | ne | odbaceno |
| commodities:BRK20:2w:short | 153 | -0.5438 | -0.3188 | -0.609 | -1.68 | 0.09296 | -0.87 | -1.47 | -1.8858 | -0.8138 | 0 | None | None | ne | odbaceno |
| alts:ATTN:1w:short | 319 | -0.3511 | -0.1482 | -0.4381 | -1.69 | 0.09103 | -1.45 | -0.88 | -0.3215 | -0.6211 | 0 | None | None | ne | odbaceno |
| stocks:LOWVOL:1w:short | 299 | -0.4312 | -0.011 | -0.4704 | -1.7 | 0.08913 | -1.09 | -1.31 | 0.5985 | -0.7012 | - | - | - | ne | odbaceno |
| stocks:ATTN:4w:long | 74 | -0.8158 | -1.09 | -0.9621 | -1.75 | 0.08012 | -2.35 | -0.02 | 1.0756 | -1.0858 | - | - | - | ne | odbaceno |
| commodities:VOLUP:2w:short | 153 | -0.5585 | -0.3614 | -0.642 | -1.79 | 0.07345 | 0.1 | -2.65 | -0.4422 | -0.8285 | 0 | None | None | ne | odbaceno |
| commodities:HIGH52:4w:short | 64 | -1.1231 | -1.103 | -1.289 | -1.8 | 0.07186 | -1.82 | -0.58 | -1.7187 | -1.3931 | 0 | None | None | ne | odbaceno |
| commodities:REV5:1w:long | 311 | -0.2788 | -0.2162 | -0.323 | -1.82 | 0.06876 | -1.34 | -1.23 | -1.1795 | -0.5488 | 0 | None | None | ne | odbaceno |
| stocks:LOWVOL:4w:short | 74 | -2.3734 | -0.6291 | -2.6549 | -1.86 | 0.06289 | -0.72 | -1.81 | -0.5965 | -2.6434 | - | - | - | ne | odbaceno |
| stocks:BRK20:4w:short | 76 | -2.801 | -0.7332 | -3.0302 | -1.9 | 0.05743 | -1.48 | -1.33 | -1.2912 | -3.071 | - | - | - | ne | odbaceno |
| crypto:VOLUP:4w:long | 80 | -2.3533 | -1.2836 | -2.9146 | -1.95 | 0.05118 | -1.8 | -0.75 | -5.3118 | -2.6233 | 79 | -3.8721 | -1.86 | ne | odbaceno |
| commodities:HIGH_BRK:20d:short | 12 | -5.9393 | -2.584 | -6.9562 | -1.95 | None | -1.71 | -1.4 | -2.1703 | -6.2093 | 0 | None | None | ne | premalo |
| crypto:ATTN:1w:long | 319 | -0.8007 | -1.1507 | -0.9239 | -1.99 | 0.04659 | -1.44 | -1.53 | -1.4989 | -1.0707 | 313 | 0.4077 | 0.86 | ne | odbaceno |
| stocks:LOWVOL:2w:short | 149 | -1.131 | -0.6725 | -1.241 | -2.06 | 0.0394 | -1.17 | -1.73 | 0.1256 | -1.401 | - | - | - | ne | odbaceno |
| stocks:LOWVOL:4w:long | 74 | -1.497 | -1.746 | -1.6941 | -2.1 | 0.03573 | -1.16 | -1.79 | -0.5785 | -1.767 | - | - | - | ne | odbaceno |
| commodities:HIGH_BRK:10d:short | 23 | -2.837 | -2.0238 | -3.4036 | -2.11 | None | -1.94 | -0.86 | -1.3837 | -3.107 | 0 | None | None | ne | premalo |
| alts:ATTN:4w:long | 79 | -2.2175 | -3.032 | -2.711 | -2.12 | 0.03401 | -0.51 | -3.03 | -4.4779 | -2.4875 | 0 | None | None | ne | odbaceno |
| commodities:REV5:1w:short | 311 | -0.337 | -0.301 | -0.3671 | -2.14 | 0.03235 | -1.67 | -1.34 | -0.8731 | -0.607 | 0 | None | None | ne | odbaceno |
| alts:HIGH52:2w:short | 145 | -1.0239 | -0.5225 | -1.1487 | -2.15 | 0.03156 | -1.31 | -1.77 | -3.011 | -1.2939 | 0 | None | None | ne | odbaceno |
| commodities:MOM12_1:2w:short | 129 | -0.6367 | -0.6018 | -0.733 | -2.18 | 0.02926 | -2.76 | -0.31 | -0.7608 | -0.9067 | 0 | None | None | ne | odbaceno |
| stocks:LOWVOL:2w:long | 149 | -0.7165 | -1.0431 | -0.7983 | -2.19 | 0.02852 | -1.35 | -1.73 | -0.2785 | -0.9865 | - | - | - | ne | odbaceno |
| stocks:REV5:1w:short | 311 | -0.3709 | -0.1839 | -0.399 | -2.2 | 0.02781 | -1.88 | -1.19 | 0.2583 | -0.6409 | - | - | - | ne | odbaceno |
| commodities:VOLUP:2w:long | 153 | -0.6066 | -0.7336 | -0.6792 | -2.21 | 0.02711 | -1.44 | -1.69 | -0.5016 | -0.8766 | 0 | None | None | ne | odbaceno |
| alts:SPIKE_UP:14d:long | 159 | -2.9883 | -6.9715 | -3.522 | -2.22 | 0.02642 | -2.29 | -0.78 | -5.7973 | -3.2583 | 0 | None | None | ne | odbaceno |
| crypto:MOM12_1:1w:long | 291 | -0.6593 | -0.9514 | -0.712 | -2.29 | 0.02202 | -1.36 | -2.01 | -1.6138 | -0.9293 | 286 | -0.1764 | -0.58 | da | odbaceno |
| commodities:ATTN:1w:long | 300 | -0.2649 | -0.2804 | -0.2852 | -2.29 | 0.02202 | -2.17 | -1.03 | 0.1427 | -0.5349 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:4w:short | 76 | -1.4494 | -0.8652 | -1.6162 | -2.35 | 0.01877 | -2.55 | -0.85 | -2.0914 | -1.7194 | 0 | None | None | da | odbaceno |
| crypto:REV5:4w:long | 80 | -2.8928 | -2.2545 | -3.2919 | -2.4 | 0.0164 | -0.97 | -2.93 | -3.2544 | -3.1628 | 79 | 0.4622 | 0.32 | da | odbaceno |
| stocks:LOWVOL:1w:long | 299 | -0.3885 | -0.2384 | -0.4181 | -2.42 | 0.01552 | -1.62 | -1.8 | -0.0112 | -0.6585 | - | - | - | da | odbaceno |
| commodities:LOWVOL:1w:short | 299 | -0.4657 | -0.2729 | -0.4932 | -2.44 | 0.01469 | -1.47 | -1.98 | -0.5722 | -0.7357 | 0 | None | None | da | odbaceno |
| crypto:VOLUP:1w:long | 323 | -0.8755 | -1.0497 | -1.0252 | -2.45 | 0.01429 | -1.1 | -2.99 | -1.6467 | -1.1455 | 321 | -0.2478 | -0.56 | da | odbaceno |
| crypto:SPIKE_UP:7d:long | 220 | -2.506 | -3.6681 | -2.8879 | -2.51 | 0.01207 | -0.53 | -4.07 | -5.4455 | -2.776 | 134 | -1.2117 | -0.74 | da | odbaceno |
| alts:HIGH52:1w:short | 291 | -0.5585 | -0.2796 | -0.5935 | -2.56 | 0.01047 | -2.59 | -0.95 | -0.3435 | -0.8285 | 0 | None | None | da | odbaceno |
| alts:HIGH52:2w:long | 145 | -1.2258 | -0.8292 | -1.336 | -2.57 | 0.01017 | -1.79 | -1.85 | -2.9003 | -1.4958 | 0 | None | None | da | odbaceno |
| alts:VOLUP:1w:short | 323 | -0.5369 | -0.2153 | -0.5882 | -2.62 | 0.00879 | -2.44 | -1.11 | -0.1635 | -0.8069 | 2 | None | None | da | odbaceno |
| alts:REV5:1w:long | 323 | -0.5674 | -1.0233 | -0.6747 | -2.65 | 0.00805 | -0.94 | -3.48 | -0.8343 | -0.8374 | 2 | None | None | da | odbaceno |
| alts:BRK20:1w:long | 323 | -0.5988 | -0.8216 | -0.6675 | -2.7 | 0.00693 | -1.6 | -2.45 | -0.6952 | -0.8688 | 2 | None | None | da | odbaceno |
| stocks:VOLUP:1w:short | 308 | -0.4068 | -0.5103 | -0.4322 | -2.71 | 0.00673 | -2.3 | -1.45 | -0.548 | -0.6768 | - | - | - | da | odbaceno |
| crypto:ATTN:4w:long | 79 | -3.2565 | -3.0239 | -3.6177 | -2.79 | 0.00527 | -2.42 | -1.41 | -11.0152 | -3.5265 | 77 | 1.5045 | 0.85 | da | odbaceno |
| alts:HIGH52:1w:long | 291 | -0.7204 | -0.8434 | -0.8189 | -2.81 | 0.00495 | -2.01 | -1.98 | -1.7344 | -0.9904 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:7d:long | 130 | -5.6639 | -7.0293 | -6.6609 | -2.82 | 0.0048 | -1.11 | -2.88 | -12.1202 | -5.9339 | 47 | 1.3751 | 0.38 | da | odbaceno |
| alts:SPIKE_DN:7d:long | 272 | -3.6232 | -6.9886 | -4.4303 | -2.82 | 0.0048 | -1.51 | -3.02 | -6.8878 | -3.8932 | 0 | None | None | da | odbaceno |
| commodities:LOWVOL:1w:long | 299 | -0.29 | -0.2496 | -0.3073 | -2.86 | 0.00424 | -2.25 | -1.77 | -0.2056 | -0.56 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:1w:short | 308 | -0.3935 | -0.4249 | -0.4199 | -2.89 | 0.00385 | -2.71 | -1.28 | 0.1644 | -0.6635 | 0 | None | None | da | odbaceno |
| commodities:BRK20:2w:long | 153 | -0.7256 | -0.7877 | -0.7844 | -2.9 | 0.00373 | -1.43 | -2.78 | -1.3513 | -0.9956 | 0 | None | None | da | odbaceno |
| alts:VOLUP:2w:long | 161 | -1.4482 | -1.5349 | -1.6265 | -3.0 | 0.0027 | -1.39 | -3.67 | -2.5832 | -1.7182 | 1 | None | None | da | odbaceno |
| stocks:SPIKE_UP:10d:short | 96 | -5.7705 | -2.0868 | -6.0181 | -3.07 | 0.00214 | -2.45 | -1.84 | 0.6348 | -6.0405 | - | - | - | da | odbaceno |
| commodities:SPIKE_UP:5d:long | 72 | -1.5258 | -2.0412 | -1.7868 | -3.1 | 0.00194 | -1.75 | -2.88 | -2.9285 | -1.7958 | 0 | None | None | da | odbaceno |
| commodities:BRK20:1w:long | 308 | -0.4296 | -0.2883 | -0.459 | -3.11 | 0.00187 | -2.78 | -1.62 | 0.231 | -0.6996 | 0 | None | None | da | odbaceno |
| commodities:BRK20:1w:short | 308 | -0.4575 | -0.4479 | -0.4884 | -3.11 | 0.00187 | -2.57 | -1.81 | -0.2156 | -0.7275 | 0 | None | None | da | odbaceno |
| commodities:HIGH52:1w:long | 260 | -0.4069 | -0.2408 | -0.4295 | -3.15 | 0.00163 | -2.24 | -2.22 | -0.7986 | -0.6769 | 0 | None | None | da | odbaceno |
| commodities:MOM12_1:1w:short | 260 | -0.4833 | -0.3367 | -0.5179 | -3.18 | 0.00147 | -2.99 | -1.41 | -1.0472 | -0.7533 | 0 | None | None | da | odbaceno |
| commodities:VOLUP:1w:long | 308 | -0.4524 | -0.3602 | -0.4824 | -3.37 | 0.00075 | -2.86 | -1.82 | 0.0703 | -0.7224 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:28d:long | 37 | -18.3068 | -17.4787 | -21.5337 | -3.51 | 0.00045 | -1.81 | -4.33 | -24.691 | -18.5768 | 11 | -3.2657 | -1.37 | da | odbaceno |
| alts:ATTN:1w:long | 319 | -1.005 | -1.1065 | -1.1388 | -3.8 | 0.00014 | -1.92 | -4.01 | -2.1776 | -1.275 | 0 | None | None | da | odbaceno |
| alts:ATTN:2w:long | 159 | -1.5861 | -1.7247 | -1.6869 | -3.84 | 0.00012 | -1.27 | -4.45 | -4.7164 | -1.8561 | 0 | None | None | da | odbaceno |
| commodities:HIGH52:2w:short | 129 | -1.3257 | -1.142 | -1.3978 | -3.98 | 7e-05 | -3.4 | -2.15 | -1.4811 | -1.5957 | 0 | None | None | da | odbaceno |
| crypto:SPIKE_DN:14d:long | 69 | -11.3132 | -12.7651 | -12.2162 | -4.21 | 3e-05 | -1.62 | -5.68 | -23.6872 | -11.5832 | 24 | -3.2459 | -0.86 | da | odbaceno |
| crypto:REV5:2w:long | 161 | -2.2249 | -2.6114 | -2.3741 | -4.43 | 1e-05 | -2.84 | -3.86 | -3.2795 | -2.4949 | 160 | -0.7045 | -1.15 | da | odbaceno |
| commodities:HIGH52:1w:short | 260 | -0.7179 | -0.7538 | -0.7447 | -4.5 | 1e-05 | -3.82 | -2.48 | -1.0825 | -0.9879 | 0 | None | None | da | odbaceno |
| alts:SPIKE_UP:7d:long | 320 | -2.8313 | -4.5083 | -2.9864 | -4.62 | 0.0 | -3.6 | -2.9 | -7.0315 | -3.1013 | 1 | None | None | da | odbaceno |
| alts:VOLUP:1w:long | 323 | -1.1398 | -1.2203 | -1.1972 | -5.24 | 0.0 | -3.46 | -4.12 | -1.8575 | -1.4098 | 2 | None | None | da | odbaceno |
| alts:SPIKE_UP:3d:long | 322 | -2.7395 | -3.6014 | -2.8997 | -5.7 | 0.0 | -6.41 | -1.97 | -4.7027 | -3.0095 | 1 | None | None | da | odbaceno |
| crypto:REV5:1w:long | 323 | -1.4751 | -1.5369 | -1.5507 | -5.75 | 0.0 | -4.43 | -3.71 | -2.3133 | -1.7451 | 321 | -1.0751 | -3.37 | da | odbaceno |

## Opisni slucaj: GME (vlasnikov ulaz 2026-10-03)

Gde je GME po svakoj rang-porodici na poslednjoj sveci pre ulaza (2026-10-02). Percentil 1.0 = najvise u univerzumu (od 64 clanova).

| porodica | ocena | percentil |
|---|---|---|
| MOM12_1 | -0.3149 | 0.095 |
| HIGH52 | 0.9074 | 0.698 |
| REV5 | -0.056 | 0.143 |
| VOLUP | 0.0326 | 0.825 |
| BRK20 | -0.0128 | 0.635 |
| LOWVOL | -0.0261 | 0.683 |
| ATTN | 1.4911 | 0.968 |

Dogadjaji u poslednjih 10 svecâ: nijedan.
