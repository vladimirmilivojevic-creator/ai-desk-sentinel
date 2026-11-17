# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2854 | 0.0372, -0.5 | -0.016, -0.68 | 0.1267, -0.4 | 0.0441, -0.86 | -0.0098, -0.99 | -0.0213, -1.04 | 29.1 | 3.6 | 6.93/21.55 | 7.82/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2497 | 0.6022, 2.02 | 0.0475, 0.88 | 0.0459, 0.38 | 0.314, 1.07 | 0.3015, 1.01 | 0.2589, 0.81 | 31.5 | 4.5 | 7.6/20.58 | 7.52/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 732 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1285 | 0.0425, 0.5 | 0.0683, 0.31 | -0.2164, -0.47 | 0.0868, 0.3 | 0.0889, 0.31 | -0.1101, -0.17 | 33.1 | 5.1 | 8.14/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1063 | 0.5353, 0.56 | 0.3127, 0.48 | 0.3435, 0.85 | 0.5429, 0.76 | 0.5289, 0.74 | 0.3943, 0.49 | 33.9 | 5.0 | 7.85/24.48 | 8.16/28.34 | 12.0 |
| D_CSM_mom_L30 | 916 | 0.6261, 1.06 | 0.0967, 0.33 | 0.0251, 0.04 | 0.1454, 0.37 | 0.1481, 0.37 | 0.1104, 0.36 | 34.9 | 5.2 | 8.0/24.54 | 8.56/26.83 | 12.0 |
