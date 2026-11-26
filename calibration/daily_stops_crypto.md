# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2861 | 0.1286, -0.42 | 0.079, -0.56 | 0.2112, -0.28 | 0.1368, -0.76 | 0.0833, -0.9 | 0.0719, -0.94 | 28.9 | 3.6 | 6.9/21.53 | 7.93/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2523 | 0.7264, 2.2 | 0.1658, 1.07 | 0.1534, 0.59 | 0.4415, 1.26 | 0.4291, 1.19 | 0.3869, 1.0 | 31.2 | 4.5 | 7.55/20.52 | 7.67/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 735 | 2.572, 2.75 | 1.0738, 1.23 | -0.0083, -0.47 | 1.4606, 1.29 | 1.4622, 1.34 | 1.4984, 1.4 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1291 | 0.038, 0.47 | 0.0658, 0.28 | -0.2029, -0.46 | 0.0651, 0.23 | 0.0672, 0.24 | -0.1308, -0.24 | 33.3 | 5.1 | 8.15/24.24 | 7.94/25.74 | 12.0 |
| D_CSM_mom_L14 | 1070 | 0.5213, 0.5 | 0.3174, 0.46 | 0.3582, 0.85 | 0.5357, 0.71 | 0.5217, 0.69 | 0.3871, 0.44 | 34.1 | 5.0 | 7.86/24.51 | 8.17/28.34 | 12.0 |
| D_CSM_mom_L30 | 920 | 0.6063, 1.07 | 0.0936, 0.37 | 0.0303, 0.07 | 0.0987, 0.34 | 0.1064, 0.35 | 0.0688, 0.34 | 35.2 | 5.1 | 8.12/24.88 | 8.56/26.83 | 12.0 |
