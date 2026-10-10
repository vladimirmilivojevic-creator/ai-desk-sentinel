# Lovac: studija na sirem univerzumu (2026-10-10)

Univerzumi: stocks 45 instrumenata (2020-10-12 do 2026-10-09); crypto 413 instrumenata (2020-06-24 do 2026-10-09); commodities 20 instrumenata (2020-10-12 do 2026-10-09).
Testova: 180 (rang-porodice x horizonti x noge, dogadjaji x horizonti x noge), FDR 10% preko svih. Trosak 0.23% po krugu (strogo 0.50%). Mera = prosecan neto prinos ODABRANE grupe minus prosek univerzuma; nepreklapajuci periodi; t preko perioda.
Status: kandidat 11, nagovestaj 3, odbaceno 154, premalo 12.

Ogranicenja (cita se pre brojeva): nema stopova u testu; ulaz je otvaranje sledece svece, a uzivo se ulazi sat-dva kasnije. Zato jedino 'potvrdjen' (posle prolaska unapred) ima ikakvu tezinu.
- stocks: spisak je prema SADASNJOJ listi Liquid-a (preziveli i popularni), pa su istorijski rezultati verovatno prelepi.
- crypto: clanstvo je point-in-time (prvih 40 po prometu na dan, ukljucuje i kasnije ugasene kovanice), ali se trguje samo kovanicama koje Liquid sada ima; podaci su Binance spot, ne Liquid; uzivo se ulazi sat-dva posle otvaranja dnevne svece (dodato 0.10% troska).
- commodities: Yahoo futures serije NISU ispravljene za zamenu ugovora (skokovi pri roll-u), pa je rezultat zasumljen i dodato je 0.15% troska; platinum, paladijum i aluminijum nisu u studiji (Yahoo nema obim).

## Svi testovi, poredjani po t

| pravilo | n | neto % | apsolutno % | t | p | t prvi deo | t zadnji deo | zadnjih 270 d % | strogi trosak % | FDR | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| crypto:BRK20:2w:short | 161 | 2.9764 | 2.6892 | 5.12 | 0.0 | 2.72 | 5.08 | 5.399 | 2.7064 | da | kandidat |
| crypto:BRK20:1w:short | 323 | 1.5032 | 1.328 | 4.9 | 0.0 | 3.01 | 4.43 | 2.839 | 1.2332 | da | kandidat |
| crypto:LOWVOL:2w:short | 159 | 3.5754 | 3.3183 | 4.89 | 0.0 | 2.94 | 4.24 | 10.3796 | 3.3054 | da | kandidat |
| crypto:BRK20:4w:short | 80 | 5.2193 | 4.7212 | 4.52 | 1e-05 | 2.12 | 4.92 | 8.004 | 4.9493 | da | kandidat |
| crypto:SPIKE_DN:14d:short | 69 | 10.9198 | 8.8504 | 4.03 | 6e-05 | 1.27 | 5.81 | 23.8974 | 10.6498 | da | kandidat |
| crypto:LOWVOL:1w:short | 319 | 1.4183 | 1.2848 | 3.57 | 0.00036 | 1.89 | 3.85 | 4.4677 | 1.1483 | da | kandidat |
| crypto:SPIKE_DN:28d:short | 37 | 18.5927 | 11.4983 | 3.53 | 0.00042 | 1.67 | 4.64 | 31.1919 | 18.3227 | da | nagovestaj |
| crypto:BRK20:2w:long | 161 | 1.8113 | 2.0984 | 3.12 | 0.00181 | 2.86 | 1.32 | 0.8359 | 1.5413 | da | kandidat |
| crypto:LOWVOL:4w:short | 79 | 4.4454 | 3.057 | 3.02 | 0.00253 | 1.24 | 3.87 | 14.6478 | 4.1754 | da | kandidat |
| crypto:LOWVOL:2w:long | 159 | 1.3611 | 1.6181 | 2.95 | 0.00318 | 1.07 | 4.04 | 2.2205 | 1.0911 | da | kandidat |
| stocks:SPIKE_UP:10d:long | 89 | 5.695 | 8.3865 | 2.82 | 0.0048 | 2.31 | 1.59 | -0.4864 | 5.425 | da | nagovestaj |
| crypto:SPIKE_DN:7d:short | 129 | 5.1756 | 3.7934 | 2.56 | 0.01047 | 0.72 | 2.9 | 11.1288 | 4.9056 | da | kandidat |
| crypto:LOWVOL:4w:long | 79 | 3.0496 | 4.4381 | 2.48 | 0.01314 | 0.76 | 4.19 | 2.5473 | 2.7796 | da | kandidat |
| crypto:LOWVOL:1w:long | 319 | 0.5673 | 0.7008 | 2.08 | 0.03753 | 1.0 | 2.2 | 0.7376 | 0.2973 | ne | nagovestaj |
| crypto:VOLUP:4w:short | 80 | 1.9549 | 1.4568 | 1.82 | 0.06876 | 1.17 | 1.63 | 1.2785 | 1.6849 | ne | odbaceno |
| commodities:HIGH_BRK:20d:long | 13 | 5.0768 | 5.8974 | 1.81 | None | 1.18 | 1.35 | 1.4103 | 4.8068 | ne | premalo |
| crypto:HIGH52:2w:short | 145 | 1.0769 | 1.5822 | 1.79 | 0.07345 | 1.5 | 0.96 | 1.1174 | 0.8069 | ne | odbaceno |
| crypto:SPIKE_UP:7d:short | 227 | 1.6187 | 2.9413 | 1.63 | 0.1031 | -0.24 | 3.68 | 5.7873 | 1.3487 | ne | odbaceno |
| commodities:SPIKE_UP:5d:short | 71 | 0.7742 | 0.6847 | 1.55 | 0.12114 | 0.57 | 1.86 | 2.3022 | 0.5042 | ne | odbaceno |
| crypto:SPIKE_UP:14d:short | 112 | 2.5918 | 3.0581 | 1.53 | 0.12602 | 0.13 | 2.3 | 6.739 | 2.3218 | ne | odbaceno |
| commodities:HIGH_BRK:10d:long | 24 | 1.9496 | 2.6332 | 1.5 | None | 1.52 | 0.34 | 0.6289 | 1.6796 | ne | premalo |
| crypto:VOLUP:2w:short | 161 | 0.7985 | 0.5113 | 1.37 | 0.17069 | 1.38 | 0.43 | 2.6303 | 0.5285 | ne | odbaceno |
| crypto:BRK20:1w:long | 323 | 0.5035 | 0.6787 | 1.34 | 0.18025 | 1.25 | 0.53 | -0.4972 | 0.2335 | ne | odbaceno |
| stocks:ATTN:2w:long | 149 | 0.6685 | 2.422 | 1.33 | 0.18352 | 0.83 | 1.43 | 0.4675 | 0.3985 | ne | odbaceno |
| crypto:HIGH52:2w:long | 145 | 0.7913 | 0.286 | 1.3 | 0.1936 | 1.51 | 0.05 | -1.8479 | 0.5213 | ne | odbaceno |
| stocks:MOM12_1:4w:long | 64 | 1.1592 | 4.681 | 1.29 | 0.19705 | -0.51 | 2.31 | 2.5306 | 0.8892 | ne | odbaceno |
| crypto:ATTN:2w:short | 159 | 0.6207 | 0.3855 | 1.23 | 0.2187 | 0.43 | 1.96 | 0.3965 | 0.3507 | ne | odbaceno |
| stocks:VOLUP:4w:long | 76 | 1.2107 | 5.1591 | 1.19 | 0.23405 | 0.74 | 0.94 | -0.7509 | 0.9407 | ne | odbaceno |
| stocks:SPIKE_DN:20d:short | 38 | 2.7359 | -0.8791 | 1.15 | 0.25014 | 0.84 | 0.77 | 9.2158 | 2.4659 | ne | odbaceno |
| crypto:HIGH_BRK:7d:short | 117 | 2.1255 | 2.8542 | 1.14 | 0.25429 | 1.6 | -0.05 | 12.6245 | 1.8555 | ne | odbaceno |
| crypto:HIGH52:1w:short | 291 | 0.3423 | 0.5068 | 1.1 | 0.27133 | 1.6 | -0.31 | -0.2325 | 0.0723 | ne | odbaceno |
| stocks:VOLUP:2w:long | 153 | 0.403 | 2.3101 | 1.04 | 0.29834 | 0.78 | 0.68 | 0.7158 | 0.133 | ne | odbaceno |
| stocks:MOM12_1:2w:long | 129 | 0.4555 | 2.1987 | 0.99 | 0.32217 | -0.98 | 2.17 | 1.4844 | 0.1855 | ne | odbaceno |
| crypto:BRK20:4w:long | 80 | 1.2084 | 1.7065 | 0.98 | 0.32709 | 0.09 | 1.8 | -1.2494 | 0.9384 | ne | odbaceno |
| crypto:MOM12_1:4w:short | 72 | 1.1704 | 1.7192 | 0.97 | 0.33205 | -0.07 | 2.31 | 4.0695 | 0.9004 | ne | odbaceno |
| stocks:HIGH_BRK:10d:long | 56 | 1.3635 | 3.2567 | 0.91 | 0.36282 | 0.98 | 0.22 | 1.1708 | 1.0935 | ne | odbaceno |
| stocks:SPIKE_UP:5d:long | 183 | 0.6225 | 1.2588 | 0.88 | 0.37886 | 1.32 | -0.32 | -2.7553 | 0.3525 | ne | odbaceno |
| crypto:HIGH_BRK:14d:short | 61 | 2.529 | 2.2002 | 0.73 | 0.46539 | 0.56 | 0.46 | 13.1142 | 2.259 | ne | odbaceno |
| crypto:ATTN:1w:short | 319 | 0.2019 | 0.0756 | 0.71 | 0.4777 | -0.26 | 2.09 | 0.2494 | -0.0681 | ne | odbaceno |
| crypto:REV5:4w:short | 80 | 1.0772 | 0.5791 | 0.69 | 0.49019 | 1.09 | -0.43 | 6.2689 | 0.8072 | ne | odbaceno |
| crypto:SPIKE_UP:28d:short | 54 | 2.592 | 4.995 | 0.69 | 0.49019 | -1.32 | 2.92 | 19.138 | 2.322 | ne | odbaceno |
| stocks:SPIKE_DN:5d:short | 140 | 0.3872 | -1.0195 | 0.59 | 0.55519 | 0.2 | 0.78 | 1.8402 | 0.1172 | ne | odbaceno |
| commodities:SPIKE_UP:10d:short | 35 | 0.689 | 0.2546 | 0.59 | 0.55519 | 0.39 | 0.44 | -0.0295 | 0.419 | ne | odbaceno |
| crypto:HIGH52:4w:short | 72 | 0.5574 | 1.1171 | 0.41 | 0.68181 | -0.16 | 1.46 | 1.3108 | 0.2874 | ne | odbaceno |
| crypto:VOLUP:1w:short | 323 | 0.1214 | -0.0538 | 0.41 | 0.68181 | 0.88 | -0.49 | 0.8388 | -0.1486 | ne | odbaceno |
| stocks:BRK20:1w:long | 308 | 0.0656 | 0.8496 | 0.36 | 0.71885 | 0.66 | -0.17 | -0.0202 | -0.2044 | ne | odbaceno |
| stocks:MOM12_1:1w:long | 260 | 0.0799 | 0.8219 | 0.34 | 0.73386 | -0.84 | 1.16 | 0.4493 | -0.1901 | ne | odbaceno |
| crypto:HIGH52:4w:long | 72 | 0.4573 | -0.1024 | 0.34 | 0.73386 | 0.35 | 0.08 | -3.6514 | 0.1873 | ne | odbaceno |
| crypto:MOM12_1:2w:short | 145 | 0.2356 | 0.7402 | 0.33 | 0.7414 | -0.58 | 1.8 | 0.8365 | -0.0344 | ne | odbaceno |
| stocks:ATTN:1w:long | 300 | 0.0622 | 0.7919 | 0.32 | 0.74897 | -0.08 | 0.75 | 0.131 | -0.2078 | ne | odbaceno |
| commodities:ATTN:4w:short | 74 | 0.1643 | -0.8697 | 0.3 | 0.76418 | -0.09 | 0.49 | 3.7626 | -0.1057 | ne | odbaceno |
| stocks:SPIKE_DN:10d:long | 68 | 0.5912 | 3.3815 | 0.29 | 0.77182 | 0.71 | -0.8 | -6.2604 | 0.3212 | ne | odbaceno |
| commodities:BRK20:4w:short | 76 | 0.176 | -1.0021 | 0.28 | 0.77948 | 1.29 | -0.67 | 0.2826 | -0.094 | ne | odbaceno |
| stocks:BRK20:4w:long | 76 | 0.1959 | 4.1443 | 0.23 | 0.81809 | -0.11 | 0.47 | 0.9385 | -0.0741 | ne | odbaceno |
| crypto:HIGH_BRK:28d:short | 27 | 1.809 | 1.7717 | 0.22 | None | 0.15 | 0.15 | 23.5027 | 1.539 | ne | premalo |
| commodities:SPIKE_DN:5d:long | 72 | 0.1088 | 0.7483 | 0.18 | 0.85715 | -0.14 | 0.39 | -1.7537 | -0.1612 | ne | odbaceno |
| crypto:HIGH52:1w:long | 291 | 0.068 | -0.0965 | 0.16 | 0.87288 | 0.59 | -0.85 | -1.6374 | -0.202 | ne | odbaceno |
| crypto:MOM12_1:4w:long | 72 | 0.1827 | -0.3661 | 0.13 | 0.89657 | 0.43 | -0.53 | -0.6009 | -0.0873 | ne | odbaceno |
| crypto:ATTN:4w:short | 79 | 0.1201 | -1.2481 | 0.12 | 0.90448 | -0.67 | 1.68 | 0.9923 | -0.1499 | ne | odbaceno |
| commodities:MOM12_1:4w:long | 64 | 0.0624 | 0.8989 | 0.08 | 0.93624 | -0.05 | 0.16 | -2.8176 | -0.2076 | ne | odbaceno |
| stocks:REV5:4w:long | 77 | 0.0592 | 4.2072 | 0.03 | 0.97607 | 0.58 | -1.69 | -4.3337 | -0.2108 | ne | odbaceno |
| stocks:BRK20:2w:long | 153 | 0.0093 | 1.9164 | 0.03 | 0.97607 | -0.83 | 0.76 | -0.2904 | -0.2607 | ne | odbaceno |
| commodities:REV5:2w:long | 155 | 0.0103 | 0.5384 | 0.03 | 0.97607 | -0.72 | 0.79 | -0.4314 | -0.2597 | ne | odbaceno |
| commodities:LOWVOL:4w:short | 74 | 0.0019 | -1.0321 | 0.0 | 1.0 | 0.31 | -0.29 | 1.4545 | -0.2681 | ne | odbaceno |
| stocks:HIGH_BRK:20d:short | 27 | -0.0379 | -4.7057 | -0.01 | None | -0.03 | 0.03 | -2.4859 | -0.3079 | ne | premalo |
| stocks:SPIKE_UP:20d:long | 46 | -0.1506 | 5.572 | -0.05 | 0.96012 | 0.49 | -0.86 | -9.3213 | -0.4206 | ne | odbaceno |
| stocks:VOLUP:1w:long | 308 | -0.0154 | 0.7687 | -0.08 | 0.93624 | 0.33 | -0.5 | -0.1801 | -0.2854 | ne | odbaceno |
| stocks:SPIKE_UP:20d:short | 46 | -0.3094 | -6.032 | -0.1 | 0.92034 | -0.59 | 0.74 | 8.8613 | -0.5794 | ne | odbaceno |
| commodities:SPIKE_UP:20d:short | 21 | -0.2964 | -1.1999 | -0.12 | None | 1.31 | -0.79 | -2.1662 | -0.5664 | ne | premalo |
| stocks:HIGH_BRK:20d:long | 27 | -0.4221 | 4.2457 | -0.15 | None | -0.08 | -0.2 | 2.0259 | -0.6921 | ne | premalo |
| commodities:SPIKE_DN:20d:short | 14 | -0.3284 | -1.1811 | -0.16 | None | -0.3 | 0.65 | 1.1052 | -0.5984 | ne | premalo |
| crypto:REV5:2w:short | 161 | -0.1132 | -0.4004 | -0.18 | 0.85715 | -0.71 | 0.79 | 3.5431 | -0.3832 | ne | odbaceno |
| stocks:HIGH52:4w:long | 64 | -0.1386 | 3.3833 | -0.19 | 0.84931 | -0.65 | 0.29 | 2.0587 | -0.4086 | ne | odbaceno |
| commodities:SPIKE_UP:20d:long | 21 | -0.4636 | 0.4399 | -0.19 | None | -1.71 | 0.64 | 1.4062 | -0.7336 | ne | premalo |
| stocks:HIGH_BRK:5d:short | 114 | -0.1533 | -0.9081 | -0.21 | 0.83367 | -0.13 | -0.16 | 0.4226 | -0.4233 | ne | odbaceno |
| commodities:SPIKE_DN:20d:long | 14 | -0.4316 | 0.4211 | -0.21 | None | 0.09 | -1.39 | -1.8652 | -0.7016 | ne | premalo |
| crypto:REV5:1w:short | 323 | -0.0898 | -0.265 | -0.23 | 0.81809 | -0.82 | 1.26 | 1.2624 | -0.3598 | ne | odbaceno |
| stocks:REV5:1w:long | 311 | -0.049 | 0.7287 | -0.26 | 0.79486 | -0.26 | -0.09 | 0.0917 | -0.319 | ne | odbaceno |
| commodities:SPIKE_DN:10d:short | 37 | -0.2959 | -1.1251 | -0.26 | 0.79486 | -1.05 | 0.56 | -1.0988 | -0.5659 | ne | odbaceno |
| stocks:MOM12_1:4w:short | 64 | -0.2384 | -3.7603 | -0.27 | 0.78716 | -0.56 | 0.43 | 1.3748 | -0.5084 | ne | odbaceno |
| crypto:VOLUP:2w:long | 161 | -0.2156 | 0.0716 | -0.28 | 0.77948 | 0.38 | -1.3 | -0.6118 | -0.4856 | ne | odbaceno |
| crypto:HIGH_BRK:28d:long | 27 | -2.469 | -2.4317 | -0.3 | None | -0.22 | -0.2 | -24.1627 | -2.739 | ne | premalo |
| commodities:HIGH_BRK:5d:short | 50 | -0.2726 | -0.3303 | -0.38 | 0.70395 | -1.15 | 0.64 | 0.4767 | -0.5426 | ne | odbaceno |
| stocks:HIGH_BRK:5d:long | 114 | -0.3067 | 0.4481 | -0.41 | 0.68181 | -0.36 | -0.21 | -0.8826 | -0.5767 | ne | odbaceno |
| commodities:SPIKE_DN:10d:long | 37 | -0.4641 | 0.3651 | -0.41 | 0.68181 | 0.44 | -0.93 | 0.3388 | -0.7341 | ne | odbaceno |
| commodities:HIGH52:4w:long | 64 | -0.2596 | 0.5769 | -0.44 | 0.65994 | 0.66 | -1.22 | -6.2103 | -0.5296 | ne | odbaceno |
| stocks:SPIKE_DN:10d:short | 68 | -1.0512 | -3.8415 | -0.52 | 0.60306 | -0.86 | 0.58 | 5.8004 | -1.3212 | ne | odbaceno |
| commodities:MOM12_1:2w:long | 129 | -0.2214 | 0.1455 | -0.59 | 0.55519 | -0.52 | -0.29 | -1.3107 | -0.4914 | ne | odbaceno |
| commodities:ATTN:2w:long | 149 | -0.1441 | 0.3 | -0.6 | 0.54851 | -1.21 | 0.4 | 1.1156 | -0.4141 | ne | odbaceno |
| stocks:MOM12_1:2w:short | 129 | -0.2616 | -2.0048 | -0.62 | 0.53526 | -1.06 | 0.43 | 1.114 | -0.5316 | ne | odbaceno |
| stocks:ATTN:2w:short | 149 | -0.2219 | -1.9754 | -0.68 | 0.4965 | 1.07 | -2.7 | -0.4152 | -0.4919 | ne | odbaceno |
| commodities:HIGH_BRK:5d:long | 50 | -0.4874 | -0.4297 | -0.69 | 0.49019 | 0.25 | -1.26 | -1.2367 | -0.7574 | ne | odbaceno |
| commodities:ATTN:4w:long | 74 | -0.367 | 0.667 | -0.78 | 0.43539 | -0.46 | -0.63 | 0.3673 | -0.637 | ne | odbaceno |
| stocks:HIGH52:2w:long | 129 | -0.2952 | 1.448 | -0.82 | 0.41222 | -1.62 | 0.4 | 0.5623 | -0.5652 | ne | odbaceno |
| crypto:MOM12_1:1w:short | 291 | -0.306 | -0.1396 | -0.85 | 0.39533 | -1.34 | 0.68 | -0.3121 | -0.576 | ne | odbaceno |
| commodities:LOWVOL:4w:long | 74 | -0.3724 | 0.6616 | -0.86 | 0.38979 | -0.36 | -0.85 | -1.8473 | -0.6424 | ne | odbaceno |
| crypto:SPIKE_UP:28d:long | 54 | -3.252 | -5.655 | -0.87 | 0.3843 | 1.18 | -3.05 | -19.798 | -3.522 | ne | odbaceno |
| commodities:REV5:4w:short | 77 | -0.5488 | -1.7868 | -0.88 | 0.37886 | -0.28 | -0.93 | 0.6256 | -0.8188 | ne | odbaceno |
| stocks:REV5:2w:long | 155 | -0.3701 | 1.5473 | -0.89 | 0.37347 | 0.25 | -1.77 | -1.6884 | -0.6401 | ne | odbaceno |
| stocks:VOLUP:4w:short | 76 | -1.5162 | -5.4645 | -0.89 | 0.37347 | -0.65 | -0.89 | -5.2994 | -1.7862 | ne | odbaceno |
| stocks:ATTN:1w:short | 300 | -0.1449 | -0.8746 | -0.9 | 0.36812 | -0.56 | -0.81 | 0.3107 | -0.4149 | ne | odbaceno |
| crypto:HIGH_BRK:14d:long | 61 | -3.189 | -2.8602 | -0.92 | 0.35757 | -0.71 | -0.58 | -13.7742 | -3.459 | ne | odbaceno |
| stocks:BRK20:2w:short | 153 | -0.5332 | -2.4403 | -0.97 | 0.33205 | -1.35 | 0.31 | -0.6036 | -0.8032 | ne | odbaceno |
| commodities:LOWVOL:2w:short | 149 | -0.3774 | -0.8215 | -0.99 | 0.32217 | -0.5 | -0.88 | 0.842 | -0.6474 | ne | odbaceno |
| stocks:REV5:4w:short | 77 | -1.0031 | -5.1511 | -1.11 | 0.267 | -0.28 | -1.22 | 0.1015 | -1.2731 | ne | odbaceno |
| commodities:ATTN:2w:short | 149 | -0.31 | -0.7541 | -1.11 | 0.267 | -1.81 | 0.22 | 1.1342 | -0.58 | ne | odbaceno |
| stocks:ATTN:4w:long | 74 | -0.7149 | 2.7012 | -1.16 | 0.24605 | -2.42 | 0.94 | 1.6094 | -0.9849 | ne | odbaceno |
| stocks:HIGH_BRK:10d:short | 56 | -1.8235 | -3.7167 | -1.21 | 0.22628 | -1.21 | -0.42 | -1.6308 | -2.0935 | ne | odbaceno |
| stocks:MOM12_1:1w:short | 260 | -0.2525 | -0.9945 | -1.24 | 0.21498 | -1.34 | -0.24 | 0.1779 | -0.5225 | ne | odbaceno |
| stocks:VOLUP:2w:short | 153 | -0.5646 | -2.4718 | -1.24 | 0.21498 | -0.89 | -0.91 | -1.9879 | -0.8346 | ne | odbaceno |
| commodities:SPIKE_UP:10d:long | 35 | -1.449 | -1.0146 | -1.24 | 0.21498 | -1.12 | -0.74 | -0.7305 | -1.719 | ne | odbaceno |
| stocks:HIGH52:1w:long | 260 | -0.2437 | 0.4983 | -1.29 | 0.19705 | -1.95 | -0.03 | -0.0997 | -0.5137 | ne | odbaceno |
| stocks:SPIKE_DN:5d:long | 140 | -0.8472 | 0.5595 | -1.29 | 0.19705 | -0.69 | -1.3 | -2.3002 | -1.1172 | ne | odbaceno |
| crypto:MOM12_1:2w:long | 145 | -0.8607 | -1.3653 | -1.31 | 0.1902 | -1.54 | -0.22 | -1.6883 | -1.1307 | ne | odbaceno |
| stocks:SPIKE_DN:20d:long | 38 | -3.1959 | 0.4191 | -1.35 | 0.17702 | -0.99 | -0.89 | -9.6758 | -3.4659 | ne | odbaceno |
| commodities:HIGH52:2w:long | 129 | -0.3918 | -0.0249 | -1.37 | 0.17069 | -0.76 | -1.16 | -1.9513 | -0.6618 | ne | odbaceno |
| commodities:VOLUP:4w:long | 76 | -0.7505 | 0.4276 | -1.37 | 0.17069 | -1.24 | -0.68 | -3.0323 | -1.0205 | ne | odbaceno |
| commodities:BRK20:4w:long | 76 | -0.6905 | 0.4876 | -1.4 | 0.16151 | -0.97 | -1.0 | -4.4478 | -0.9605 | ne | odbaceno |
| crypto:ATTN:2w:long | 159 | -1.0134 | -0.7782 | -1.45 | 0.14706 | -0.63 | -1.66 | -6.1444 | -1.2834 | ne | odbaceno |
| commodities:REV5:1w:long | 311 | -0.2182 | 0.0438 | -1.45 | 0.14706 | -1.11 | -0.94 | -0.7897 | -0.4882 | ne | odbaceno |
| commodities:SPIKE_DN:5d:short | 72 | -0.8688 | -1.5083 | -1.47 | 0.14156 | -0.96 | -1.1 | 0.9937 | -1.1388 | ne | odbaceno |
| commodities:REV5:2w:short | 155 | -0.4432 | -0.9713 | -1.49 | 0.13622 | -1.55 | -0.53 | -0.5024 | -0.7132 | ne | odbaceno |
| crypto:HIGH_BRK:7d:long | 117 | -2.7855 | -3.5142 | -1.5 | 0.13361 | -1.88 | -0.17 | -13.2845 | -3.0555 | ne | odbaceno |
| stocks:SPIKE_UP:5d:short | 183 | -1.0825 | -1.7188 | -1.52 | 0.12851 | -1.8 | -0.13 | 2.2953 | -1.3525 | ne | odbaceno |
| commodities:BRK20:2w:short | 153 | -0.5056 | -1.014 | -1.56 | 0.11876 | -0.42 | -1.69 | -0.7405 | -0.7756 | ne | odbaceno |
| commodities:LOWVOL:2w:long | 149 | -0.329 | 0.115 | -1.56 | 0.11876 | -1.03 | -1.18 | -0.6518 | -0.599 | ne | odbaceno |
| crypto:VOLUP:1w:long | 323 | -0.6441 | -0.469 | -1.59 | 0.11183 | -0.31 | -2.96 | -1.4811 | -0.9141 | ne | odbaceno |
| stocks:HIGH52:4w:short | 64 | -1.8778 | -5.3997 | -1.61 | 0.1074 | -1.81 | -0.28 | 1.5096 | -2.1478 | ne | odbaceno |
| commodities:VOLUP:2w:short | 153 | -0.5038 | -1.0122 | -1.62 | 0.10523 | 0.14 | -2.21 | -0.9335 | -0.7738 | ne | odbaceno |
| stocks:BRK20:4w:short | 76 | -3.1171 | -7.0655 | -1.67 | 0.09492 | -1.48 | -0.88 | -2.5298 | -3.3871 | ne | odbaceno |
| commodities:REV5:4w:long | 77 | -0.9493 | 0.2888 | -1.67 | 0.09492 | -1.19 | -1.18 | -0.265 | -1.2193 | ne | odbaceno |
| commodities:ATTN:1w:short | 300 | -0.2248 | -0.4592 | -1.67 | 0.09492 | -1.09 | -1.3 | -0.1252 | -0.4948 | ne | odbaceno |
| stocks:BRK20:1w:short | 308 | -0.3605 | -1.1445 | -1.71 | 0.08727 | -1.21 | -1.21 | -1.0843 | -0.6305 | ne | odbaceno |
| stocks:HIGH52:2w:short | 129 | -0.8909 | -2.6341 | -1.76 | 0.07841 | -2.2 | 0.02 | 1.1773 | -1.1609 | ne | odbaceno |
| commodities:MOM12_1:1w:long | 260 | -0.3063 | -0.1225 | -1.78 | 0.07508 | -0.96 | -1.68 | -0.9037 | -0.5763 | ne | odbaceno |
| crypto:VOLUP:4w:long | 80 | -2.2432 | -1.7451 | -1.86 | 0.06289 | -1.91 | -0.39 | -4.6403 | -2.5132 | ne | odbaceno |
| commodities:MOM12_1:4w:short | 64 | -1.1347 | -1.9712 | -1.87 | 0.06148 | -2.14 | -0.26 | -2.3562 | -1.4047 | ne | odbaceno |
| stocks:HIGH52:1w:short | 260 | -0.4419 | -1.1839 | -1.9 | 0.05743 | -2.41 | -0.01 | 0.1905 | -0.7119 | ne | odbaceno |
| crypto:SPIKE_UP:14d:long | 112 | -3.2518 | -3.7181 | -1.92 | 0.05486 | -0.43 | -2.55 | -7.399 | -3.5218 | ne | odbaceno |
| stocks:LOWVOL:4w:short | 74 | -2.9252 | -6.3384 | -2.02 | 0.04338 | -0.81 | -2.02 | -4.4348 | -3.1952 | ne | odbaceno |
| stocks:LOWVOL:4w:long | 74 | -1.6605 | 1.7526 | -2.04 | 0.04135 | -0.52 | -2.38 | -3.6855 | -1.9305 | ne | odbaceno |
| crypto:ATTN:1w:long | 319 | -0.8395 | -0.7132 | -2.09 | 0.03662 | -1.45 | -1.71 | -1.7539 | -1.1095 | ne | odbaceno |
| commodities:HIGH_BRK:10d:short | 24 | -2.7096 | -3.3932 | -2.09 | None | -1.91 | -0.86 | -1.3889 | -2.9796 | ne | premalo |
| commodities:HIGH_BRK:20d:short | 13 | -5.8368 | -6.6574 | -2.09 | None | -1.35 | -1.56 | -2.1703 | -6.1068 | ne | premalo |
| commodities:VOLUP:2w:long | 153 | -0.5609 | -0.0525 | -2.11 | 0.03486 | -1.33 | -1.67 | -1.0291 | -0.8309 | ne | odbaceno |
| commodities:REV5:1w:short | 311 | -0.335 | -0.597 | -2.14 | 0.03235 | -1.88 | -1.09 | -0.6796 | -0.605 | ne | odbaceno |
| commodities:LOWVOL:1w:short | 300 | -0.4137 | -0.648 | -2.19 | 0.02852 | -1.46 | -1.64 | -0.4111 | -0.6837 | ne | odbaceno |
| commodities:MOM12_1:2w:short | 129 | -0.6454 | -1.0123 | -2.21 | 0.02711 | -3.11 | -0.04 | -0.7428 | -0.9154 | da | odbaceno |
| stocks:REV5:2w:short | 155 | -1.1396 | -3.0569 | -2.23 | 0.02575 | -1.52 | -1.75 | -0.0287 | -1.4096 | da | odbaceno |
| commodities:HIGH52:4w:short | 64 | -1.3647 | -2.2012 | -2.25 | 0.02445 | -2.01 | -1.03 | -1.3888 | -1.6347 | da | odbaceno |
| commodities:VOLUP:4w:short | 76 | -1.399 | -2.5771 | -2.28 | 0.02261 | -2.46 | -0.84 | -3.6784 | -1.669 | da | odbaceno |
| crypto:SPIKE_UP:7d:long | 227 | -2.2787 | -3.6013 | -2.29 | 0.02202 | -0.23 | -4.21 | -6.4473 | -2.5487 | da | odbaceno |
| commodities:ATTN:1w:long | 300 | -0.2791 | -0.0448 | -2.41 | 0.01595 | -2.08 | -1.31 | -0.0987 | -0.5491 | da | odbaceno |
| stocks:REV5:1w:short | 311 | -0.5163 | -1.294 | -2.42 | 0.01552 | -1.95 | -1.43 | -0.0525 | -0.7863 | da | odbaceno |
| stocks:VOLUP:1w:short | 308 | -0.4383 | -1.2223 | -2.45 | 0.01429 | -2.05 | -1.34 | -1.1993 | -0.7083 | da | odbaceno |
| stocks:ATTN:4w:short | 74 | -1.5756 | -4.9918 | -2.45 | 0.01429 | -0.96 | -2.64 | -0.5895 | -1.8456 | da | odbaceno |
| crypto:REV5:4w:long | 80 | -3.0006 | -2.5024 | -2.48 | 0.01314 | -0.98 | -3.08 | -3.4586 | -3.2706 | da | odbaceno |
| stocks:LOWVOL:1w:long | 300 | -0.4592 | 0.272 | -2.61 | 0.00905 | -1.12 | -2.56 | -1.0034 | -0.7292 | da | odbaceno |
| stocks:LOWVOL:2w:long | 149 | -0.9678 | 0.7842 | -2.67 | 0.00759 | -0.92 | -2.92 | -2.3703 | -1.2378 | da | odbaceno |
| stocks:LOWVOL:2w:short | 149 | -1.8907 | -3.6427 | -2.69 | 0.00715 | -1.66 | -2.32 | -2.0815 | -2.1607 | da | odbaceno |
| crypto:MOM12_1:1w:long | 291 | -0.8847 | -1.0511 | -2.79 | 0.00527 | -2.14 | -1.82 | -1.75 | -1.1547 | da | odbaceno |
| crypto:ATTN:4w:long | 79 | -3.3897 | -2.0215 | -2.79 | 0.00527 | -2.56 | -1.31 | -11.5316 | -3.6597 | da | odbaceno |
| commodities:BRK20:2w:long | 153 | -0.6857 | -0.1773 | -2.8 | 0.00511 | -1.31 | -2.8 | -1.8156 | -0.9557 | da | odbaceno |
| commodities:VOLUP:1w:short | 308 | -0.3781 | -0.6372 | -2.81 | 0.00495 | -3.17 | -0.64 | 0.3675 | -0.6481 | da | odbaceno |
| crypto:SPIKE_DN:7d:long | 129 | -5.8356 | -4.4534 | -2.89 | 0.00385 | -1.01 | -3.08 | -11.7888 | -6.1056 | da | odbaceno |
| commodities:BRK20:1w:short | 308 | -0.4329 | -0.6919 | -2.93 | 0.00339 | -2.37 | -1.78 | -0.1033 | -0.7029 | da | odbaceno |
| commodities:HIGH52:1w:long | 260 | -0.3823 | -0.1985 | -2.96 | 0.00308 | -2.33 | -1.83 | -0.8876 | -0.6523 | da | odbaceno |
| stocks:SPIKE_UP:10d:short | 89 | -6.155 | -8.8465 | -3.04 | 0.00237 | -2.48 | -1.75 | 0.0264 | -6.425 | da | odbaceno |
| commodities:MOM12_1:1w:short | 260 | -0.4651 | -0.6489 | -3.07 | 0.00214 | -3.19 | -1.0 | -0.3845 | -0.7351 | da | odbaceno |
| commodities:SPIKE_UP:5d:long | 71 | -1.5342 | -1.4447 | -3.08 | 0.00207 | -1.69 | -2.92 | -3.0622 | -1.8042 | da | odbaceno |
| commodities:BRK20:1w:long | 308 | -0.4258 | -0.1667 | -3.15 | 0.00163 | -2.68 | -1.76 | -0.2368 | -0.6958 | da | odbaceno |
| stocks:LOWVOL:1w:short | 300 | -0.963 | -1.6943 | -3.17 | 0.00152 | -1.95 | -2.62 | -0.9964 | -1.233 | da | odbaceno |
| commodities:LOWVOL:1w:long | 300 | -0.3343 | -0.0999 | -3.3 | 0.00097 | -2.72 | -1.86 | -0.4644 | -0.6043 | da | odbaceno |
| commodities:VOLUP:1w:long | 308 | -0.4716 | -0.2126 | -3.55 | 0.00039 | -3.23 | -1.65 | -0.301 | -0.7416 | da | odbaceno |
| crypto:SPIKE_DN:28d:long | 37 | -19.2527 | -12.1583 | -3.66 | 0.00025 | -1.76 | -4.76 | -31.8519 | -19.5227 | da | odbaceno |
| crypto:REV5:2w:long | 161 | -2.0024 | -1.7152 | -3.73 | 0.00019 | -2.2 | -3.7 | -2.8177 | -2.2724 | da | odbaceno |
| crypto:SPIKE_DN:14d:long | 69 | -11.5798 | -9.5104 | -4.27 | 2e-05 | -1.45 | -6.0 | -24.5574 | -11.8498 | da | odbaceno |
| commodities:HIGH52:2w:short | 129 | -1.4322 | -1.7992 | -4.38 | 1e-05 | -3.42 | -2.72 | -1.0748 | -1.7022 | da | odbaceno |
| commodities:HIGH52:1w:short | 260 | -0.7379 | -0.9216 | -4.67 | 0.0 | -3.78 | -2.76 | -1.0617 | -1.0079 | da | odbaceno |
| crypto:REV5:1w:long | 323 | -1.437 | -1.2618 | -5.31 | 0.0 | -4.1 | -3.45 | -2.3733 | -1.707 | da | odbaceno |

## Opisni slucaj: GME (vlasnikov ulaz 2026-10-03)

Gde je GME po svakoj rang-porodici na poslednjoj sveci pre ulaza (2026-10-02). Percentil 1.0 = najvise u univerzumu (od 45 clanova).

| porodica | ocena | percentil |
|---|---|---|
| MOM12_1 | -0.3149 | 0.114 |
| HIGH52 | 0.9074 | 0.705 |
| REV5 | -0.056 | 0.136 |
| VOLUP | 0.0326 | 0.773 |
| BRK20 | -0.0128 | 0.636 |
| LOWVOL | -0.0261 | 0.705 |
| ATTN | 1.4911 | 0.955 |

Dogadjaji u poslednjih 10 svecâ: nijedan.
