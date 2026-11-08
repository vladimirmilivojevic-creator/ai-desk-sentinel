# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2817 | -0.0278, -0.57 | -0.0761, -0.79 | 0.0892, -0.45 | -0.0227, -0.94 | -0.077, -1.08 | -0.0886, -1.12 | 29.2 | 3.6 | 6.93/21.56 | 7.74/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2465 | 0.5069, 1.84 | -0.053, 0.67 | -0.0458, 0.15 | 0.216, 0.87 | 0.2034, 0.81 | 0.1604, 0.61 | 31.8 | 4.6 | 7.66/20.69 | 7.45/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1282 | 0.0755, 0.64 | 0.069, 0.36 | -0.2195, -0.42 | 0.1047, 0.4 | 0.1069, 0.4 | -0.0925, -0.07 | 32.9 | 5.1 | 8.12/24.01 | 7.87/25.38 | 12.0 |
| D_CSM_mom_L14 | 1063 | 0.588, 0.66 | 0.3196, 0.5 | 0.3836, 0.97 | 0.5741, 0.82 | 0.5601, 0.8 | 0.4251, 0.55 | 33.8 | 5.0 | 7.74/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 917 | 0.6065, 1.01 | 0.0473, 0.21 | -0.0306, -0.12 | 0.1175, 0.3 | 0.1202, 0.3 | 0.0825, 0.3 | 34.8 | 5.2 | 8.0/24.44 | 8.44/26.83 | 12.0 |
