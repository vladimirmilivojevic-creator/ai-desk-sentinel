# Lovac: studija na sirem univerzumu (2026-10-10)

Univerzumi: stocks 48 instrumenata (2020-10-12 do 2026-10-09).
Testova: 60 (rang-porodice x horizonti x noge, dogadjaji x horizonti x noge), FDR 10% preko svih. Trosak 0.23% po krugu (strogo 0.50%). Mera = prosecan neto prinos ODABRANE grupe minus prosek univerzuma; nepreklapajuci periodi; t preko perioda.
Status: nagovestaj 1, odbaceno 57, premalo 2.

Ogranicenja (cita se pre brojeva): univerzum je izabran prema SADASNJOJ listi Liquid-a (preziveli i popularni), pa su istorijski rezultati verovatno prelepi; nema stopova u testu; ulaz je otvaranje sledeceg dana, a uzivo se ulazi sat-dva kasnije. Zato jedino 'potvrdjen' (posle prolaska unapred) ima ikakvu tezinu.

## Svi testovi, poredjani po t

| pravilo | n | neto % | apsolutno % | t | p | t prvi deo | t zadnji deo | zadnjih 270 d % | strogi trosak % | FDR | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| stocks:SPIKE_UP:10d:long | 90 | 5.8148 | 8.4577 | 2.9 | 0.00373 | 2.43 | 1.56 | -0.4513 | 5.5448 | da | nagovestaj |
| stocks:MOM12_1:4w:long | 64 | 1.445 | 4.8413 | 1.49 | 0.13622 | -0.6 | 2.49 | 3.6804 | 1.175 | ne | odbaceno |
| stocks:VOLUP:4w:long | 76 | 1.3537 | 5.1835 | 1.43 | 0.15272 | 0.81 | 1.2 | -0.5253 | 1.0837 | ne | odbaceno |
| stocks:VOLUP:2w:long | 153 | 0.4963 | 2.3574 | 1.38 | 0.16759 | 0.87 | 1.08 | 1.1464 | 0.2263 | ne | odbaceno |
| stocks:MOM12_1:2w:long | 129 | 0.5865 | 2.2757 | 1.3 | 0.1936 | -0.71 | 2.25 | 1.6317 | 0.3165 | ne | odbaceno |
| stocks:SPIKE_DN:20d:short | 39 | 2.7969 | -0.6408 | 1.21 | 0.22628 | 0.98 | 0.7 | 8.4108 | 2.5269 | ne | odbaceno |
| stocks:ATTN:2w:long | 149 | 0.5413 | 2.2508 | 1.18 | 0.238 | 0.68 | 1.26 | 0.2384 | 0.2713 | ne | odbaceno |
| stocks:HIGH_BRK:10d:long | 58 | 1.4479 | 3.081 | 1.0 | 0.31731 | 1.08 | 0.26 | 1.1919 | 1.1779 | ne | odbaceno |
| stocks:SPIKE_DN:5d:short | 147 | 0.4763 | -0.8566 | 0.76 | 0.44725 | 0.36 | 0.85 | 1.8583 | 0.2063 | ne | odbaceno |
| stocks:SPIKE_UP:5d:long | 186 | 0.4582 | 1.0547 | 0.65 | 0.51569 | 1.16 | -0.53 | -3.4309 | 0.1882 | ne | odbaceno |
| stocks:BRK20:4w:long | 76 | 0.3011 | 4.1309 | 0.38 | 0.70395 | -0.09 | 0.68 | 1.408 | 0.0311 | ne | odbaceno |
| stocks:MOM12_1:1w:long | 260 | 0.0749 | 0.8013 | 0.33 | 0.7414 | -0.83 | 1.06 | 0.6523 | -0.1951 | ne | odbaceno |
| stocks:BRK20:2w:long | 153 | 0.094 | 1.9551 | 0.32 | 0.74897 | -0.35 | 0.77 | -0.5947 | -0.176 | ne | odbaceno |
| stocks:BRK20:1w:long | 308 | 0.0522 | 0.8213 | 0.3 | 0.76418 | 0.66 | -0.28 | -0.2508 | -0.2178 | ne | odbaceno |
| stocks:ATTN:1w:long | 300 | 0.0465 | 0.7631 | 0.26 | 0.79486 | -0.13 | 0.67 | 0.0269 | -0.2235 | ne | odbaceno |
| stocks:REV5:4w:long | 77 | 0.1319 | 4.1593 | 0.07 | 0.94419 | 0.54 | -1.58 | -4.1019 | -0.1381 | ne | odbaceno |
| stocks:SPIKE_DN:10d:long | 72 | 0.1194 | 2.6122 | 0.06 | 0.95216 | 0.7 | -1.34 | -6.0441 | -0.1506 | ne | odbaceno |
| stocks:ATTN:2w:short | 149 | 0.0081 | -1.7014 | 0.03 | 0.97607 | 1.46 | -1.96 | -0.0425 | -0.2619 | ne | odbaceno |
| stocks:HIGH_BRK:20d:short | 27 | -0.0078 | -4.6379 | -0.0 | None | -0.02 | 0.05 | -2.59 | -0.2778 | ne | premalo |
| stocks:SPIKE_UP:20d:long | 46 | -0.0254 | 5.6058 | -0.01 | 0.99202 | 0.52 | -0.83 | -9.1928 | -0.2954 | ne | odbaceno |
| stocks:VOLUP:1w:long | 308 | -0.0265 | 0.7426 | -0.14 | 0.88866 | 0.16 | -0.39 | -0.2785 | -0.2965 | ne | odbaceno |
| stocks:SPIKE_UP:20d:short | 46 | -0.4346 | -6.0658 | -0.14 | 0.88866 | -0.63 | 0.72 | 8.7328 | -0.7046 | ne | odbaceno |
| stocks:MOM12_1:4w:short | 64 | -0.1378 | -3.5341 | -0.16 | 0.87288 | -0.47 | 0.5 | 1.2983 | -0.4078 | ne | odbaceno |
| stocks:HIGH_BRK:20d:long | 27 | -0.4522 | 4.1779 | -0.16 | None | -0.08 | -0.22 | 2.13 | -0.7222 | ne | premalo |
| stocks:HIGH_BRK:5d:long | 116 | -0.1993 | 0.4721 | -0.27 | 0.78716 | -0.21 | -0.17 | -0.8745 | -0.4693 | ne | odbaceno |
| stocks:HIGH52:4w:long | 64 | -0.2127 | 3.1836 | -0.29 | 0.77182 | -0.84 | 0.32 | 2.2208 | -0.4827 | ne | odbaceno |
| stocks:SPIKE_DN:10d:short | 72 | -0.5794 | -3.0722 | -0.3 | 0.76418 | -0.85 | 1.11 | 5.5841 | -0.8494 | ne | odbaceno |
| stocks:HIGH_BRK:5d:short | 116 | -0.2607 | -0.9321 | -0.35 | 0.72634 | -0.3 | -0.19 | 0.4145 | -0.5307 | ne | odbaceno |
| stocks:REV5:1w:long | 311 | -0.0884 | 0.6765 | -0.49 | 0.62413 | -0.4 | -0.29 | 0.084 | -0.3584 | ne | odbaceno |
| stocks:MOM12_1:2w:short | 129 | -0.2192 | -1.9084 | -0.54 | 0.5892 | -1.06 | 0.57 | 1.1747 | -0.4892 | ne | odbaceno |
| stocks:ATTN:1w:short | 300 | -0.1153 | -0.832 | -0.75 | 0.45325 | -0.41 | -0.73 | 0.255 | -0.3853 | ne | odbaceno |
| stocks:HIGH52:2w:long | 129 | -0.307 | 1.3822 | -0.9 | 0.36812 | -1.71 | 0.35 | 0.186 | -0.577 | ne | odbaceno |
| stocks:REV5:4w:short | 77 | -0.7578 | -4.7851 | -0.9 | 0.36812 | -0.24 | -0.99 | 0.4752 | -1.0278 | ne | odbaceno |
| stocks:BRK20:2w:short | 153 | -0.496 | -2.3571 | -0.92 | 0.35757 | -1.2 | 0.19 | -0.9822 | -0.766 | ne | odbaceno |
| stocks:VOLUP:4w:short | 76 | -1.6997 | -5.5295 | -1.01 | 0.3125 | -0.81 | -0.81 | -5.8518 | -1.9697 | ne | odbaceno |
| stocks:REV5:2w:long | 155 | -0.4156 | 1.459 | -1.07 | 0.28462 | 0.15 | -1.95 | -1.6063 | -0.6856 | ne | odbaceno |
| stocks:MOM12_1:1w:short | 260 | -0.2182 | -0.9446 | -1.1 | 0.27133 | -1.14 | -0.27 | 0.1758 | -0.4882 | ne | odbaceno |
| stocks:HIGH52:1w:long | 260 | -0.2053 | 0.5213 | -1.16 | 0.24605 | -1.92 | 0.15 | -0.1507 | -0.4753 | ne | odbaceno |
| stocks:ATTN:4w:long | 74 | -0.7129 | 2.6049 | -1.21 | 0.22628 | -2.32 | 0.53 | 1.3261 | -0.9829 | ne | odbaceno |
| stocks:SPIKE_UP:5d:short | 186 | -0.9182 | -1.5147 | -1.3 | 0.1936 | -1.64 | 0.07 | 2.9709 | -1.1882 | ne | odbaceno |
| stocks:VOLUP:2w:short | 153 | -0.5893 | -2.4504 | -1.31 | 0.1902 | -1.02 | -0.83 | -2.2687 | -0.8593 | ne | odbaceno |
| stocks:HIGH_BRK:10d:short | 58 | -1.9079 | -3.541 | -1.32 | 0.18684 | -1.32 | -0.46 | -1.6519 | -2.1779 | ne | odbaceno |
| stocks:SPIKE_DN:20d:long | 39 | -3.2569 | 0.1808 | -1.41 | 0.15854 | -1.14 | -0.82 | -8.8708 | -3.5269 | ne | odbaceno |
| stocks:BRK20:4w:short | 76 | -2.6764 | -6.5061 | -1.43 | 0.15272 | -1.33 | -0.52 | -1.7854 | -2.9464 | ne | odbaceno |
| stocks:SPIKE_DN:5d:long | 147 | -0.9363 | 0.3966 | -1.49 | 0.13622 | -0.87 | -1.4 | -2.3183 | -1.2063 | ne | odbaceno |
| stocks:HIGH52:4w:short | 64 | -1.8176 | -5.2139 | -1.6 | 0.1096 | -1.57 | -0.56 | 1.6619 | -2.0876 | ne | odbaceno |
| stocks:BRK20:1w:short | 308 | -0.3486 | -1.1177 | -1.71 | 0.08727 | -1.1 | -1.34 | -0.9837 | -0.6186 | ne | odbaceno |
| stocks:LOWVOL:4w:short | 74 | -2.4748 | -5.7902 | -1.8 | 0.07186 | -0.48 | -1.99 | -4.3607 | -2.7448 | ne | odbaceno |
| stocks:ATTN:4w:short | 74 | -1.1022 | -4.42 | -1.8 | 0.07186 | -0.59 | -1.98 | 0.4517 | -1.3722 | ne | odbaceno |
| stocks:HIGH52:2w:short | 129 | -0.9011 | -2.5903 | -1.86 | 0.06289 | -1.96 | -0.48 | 0.9173 | -1.1711 | ne | odbaceno |
| stocks:HIGH52:1w:short | 260 | -0.4318 | -1.1583 | -1.92 | 0.05486 | -2.0 | -0.55 | -0.0289 | -0.7018 | ne | odbaceno |
| stocks:LOWVOL:4w:long | 74 | -1.5833 | 1.7321 | -2.01 | 0.04443 | -0.49 | -2.34 | -3.7167 | -1.8533 | ne | odbaceno |
| stocks:REV5:2w:short | 155 | -1.1436 | -3.0182 | -2.29 | 0.02202 | -1.44 | -1.99 | -0.0986 | -1.4136 | ne | odbaceno |
| stocks:VOLUP:1w:short | 308 | -0.4233 | -1.1925 | -2.48 | 0.01314 | -2.03 | -1.43 | -1.2928 | -0.6933 | da | odbaceno |
| stocks:LOWVOL:2w:long | 149 | -0.8772 | 0.8311 | -2.5 | 0.01242 | -0.88 | -2.72 | -2.239 | -1.1472 | da | odbaceno |
| stocks:LOWVOL:2w:short | 149 | -1.644 | -3.3523 | -2.5 | 0.01242 | -1.47 | -2.19 | -2.0364 | -1.914 | da | odbaceno |
| stocks:LOWVOL:1w:long | 300 | -0.4445 | 0.2739 | -2.59 | 0.0096 | -1.18 | -2.48 | -0.9557 | -0.7145 | da | odbaceno |
| stocks:REV5:1w:short | 311 | -0.5663 | -1.3312 | -2.79 | 0.00527 | -2.03 | -1.92 | -0.2401 | -0.8363 | da | odbaceno |
| stocks:LOWVOL:1w:short | 300 | -0.8446 | -1.563 | -2.9 | 0.00373 | -1.71 | -2.47 | -0.806 | -1.1146 | da | odbaceno |
| stocks:SPIKE_UP:10d:short | 90 | -6.2748 | -8.9177 | -3.13 | 0.00175 | -2.6 | -1.73 | -0.0087 | -6.5448 | da | odbaceno |

## Opisni slucaj: GME (vlasnikov ulaz 2026-10-03)

Gde je GME po svakoj rang-porodici na poslednjoj sveci pre ulaza (2026-10-02). Percentil 1.0 = najvise u univerzumu (od 48 clanova).

| porodica | ocena | percentil |
|---|---|---|
| MOM12_1 | -0.3149 | 0.106 |
| HIGH52 | 0.9074 | 0.702 |
| REV5 | -0.056 | 0.17 |
| VOLUP | 0.0326 | 0.787 |
| BRK20 | -0.0128 | 0.617 |
| LOWVOL | -0.0261 | 0.702 |
| ATTN | 1.4911 | 0.957 |

Dogadjaji u poslednjih 10 svecâ: nijedan.
