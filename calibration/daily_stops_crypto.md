# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2828 | -0.0228, -0.56 | -0.071, -0.78 | 0.085, -0.47 | -0.0176, -0.93 | -0.0719, -1.07 | -0.0835, -1.11 | 29.2 | 3.6 | 6.93/21.56 | 7.75/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2473 | 0.5395, 1.89 | -0.0185, 0.73 | -0.0158, 0.21 | 0.2496, 0.93 | 0.237, 0.87 | 0.1941, 0.67 | 31.7 | 4.6 | 7.63/20.64 | 7.46/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1283 | 0.094, 0.67 | 0.0875, 0.39 | -0.2071, -0.4 | 0.1232, 0.42 | 0.1253, 0.43 | -0.0737, -0.05 | 32.8 | 5.1 | 8.12/24.01 | 7.92/25.38 | 12.0 |
| D_CSM_mom_L14 | 1065 | 0.5909, 0.63 | 0.3232, 0.47 | 0.3728, 0.92 | 0.577, 0.79 | 0.563, 0.77 | 0.4281, 0.52 | 33.6 | 5.0 | 7.81/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 917 | 0.6413, 1.1 | 0.0861, 0.32 | 0.0051, 0.01 | 0.1524, 0.39 | 0.1551, 0.39 | 0.1174, 0.38 | 34.6 | 5.2 | 8.0/24.44 | 8.46/26.83 | 12.0 |
