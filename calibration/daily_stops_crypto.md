# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2847 | 0.0516, -0.41 | -0.0062, -0.62 | 0.1338, -0.35 | 0.0567, -0.78 | 0.0028, -0.92 | -0.0087, -0.96 | 29.1 | 3.6 | 6.92/21.53 | 7.83/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2491 | 0.6016, 1.99 | 0.0467, 0.85 | 0.0451, 0.34 | 0.3133, 1.04 | 0.3008, 0.98 | 0.2582, 0.78 | 31.5 | 4.5 | 7.6/20.58 | 7.52/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 732 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1285 | 0.0608, 0.56 | 0.0761, 0.34 | -0.213, -0.46 | 0.1008, 0.35 | 0.1029, 0.35 | -0.0962, -0.12 | 33.0 | 5.1 | 8.13/24.22 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5442, 0.57 | 0.3065, 0.46 | 0.3364, 0.82 | 0.5472, 0.76 | 0.5331, 0.74 | 0.3984, 0.49 | 33.9 | 5.0 | 7.85/24.39 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.6208, 1.04 | 0.092, 0.29 | 0.0227, 0.0 | 0.1406, 0.34 | 0.1434, 0.33 | 0.1057, 0.33 | 34.8 | 5.1 | 8.0/24.54 | 8.56/26.83 | 12.0 |
