# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2818 | -0.0619, -0.62 | -0.0865, -0.82 | 0.0722, -0.49 | -0.0541, -1.0 | -0.1085, -1.13 | -0.1201, -1.18 | 29.1 | 3.6 | 6.92/21.55 | 7.68/24.75 | 12.0 |
| D_MOM_L21_z0.5 | 2459 | 0.4895, 1.77 | -0.0715, 0.59 | -0.054, 0.11 | 0.198, 0.8 | 0.1854, 0.74 | 0.1422, 0.54 | 31.9 | 4.6 | 7.66/20.69 | 7.44/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1281 | 0.1016, 0.69 | 0.0816, 0.36 | -0.2052, -0.42 | 0.1331, 0.43 | 0.1311, 0.43 | -0.0686, -0.05 | 32.7 | 5.1 | 8.05/23.99 | 7.77/25.38 | 12.0 |
| D_CSM_mom_L14 | 1063 | 0.584, 0.63 | 0.3174, 0.46 | 0.4032, 0.97 | 0.5701, 0.79 | 0.556, 0.77 | 0.421, 0.51 | 33.6 | 5.0 | 7.66/24.34 | 8.06/28.34 | 12.0 |
| D_CSM_mom_L30 | 915 | 0.6211, 1.02 | 0.0543, 0.2 | -0.0259, -0.13 | 0.1356, 0.31 | 0.1383, 0.31 | 0.1005, 0.31 | 34.6 | 5.2 | 8.0/24.54 | 8.3/26.87 | 12.0 |
