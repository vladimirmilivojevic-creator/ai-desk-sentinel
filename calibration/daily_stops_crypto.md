# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2863 | 0.0527, -0.51 | 0.0028, -0.68 | 0.1484, -0.4 | 0.0609, -0.86 | 0.0072, -1.0 | -0.0042, -1.04 | 29.1 | 3.6 | 6.93/21.55 | 7.82/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2507 | 0.6463, 2.11 | 0.0928, 0.98 | 0.0922, 0.5 | 0.3588, 1.16 | 0.3463, 1.09 | 0.3037, 0.9 | 31.4 | 4.5 | 7.6/20.58 | 7.54/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 733 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1289 | 0.0541, 0.5 | 0.0902, 0.33 | -0.1883, -0.42 | 0.0961, 0.29 | 0.0982, 0.3 | -0.1, -0.18 | 33.1 | 5.1 | 8.14/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1066 | 0.5174, 0.5 | 0.3092, 0.45 | 0.3466, 0.83 | 0.5318, 0.72 | 0.5178, 0.7 | 0.3832, 0.44 | 34.0 | 5.0 | 7.85/24.51 | 8.16/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.617, 1.08 | 0.0928, 0.35 | 0.0325, 0.07 | 0.1327, 0.38 | 0.1354, 0.38 | 0.0977, 0.37 | 35.0 | 5.2 | 8.0/24.88 | 8.52/26.83 | 12.0 |
