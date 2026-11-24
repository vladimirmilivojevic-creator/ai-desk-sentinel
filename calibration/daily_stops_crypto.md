# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2859 | 0.1116, -0.43 | 0.0572, -0.59 | 0.1919, -0.31 | 0.1198, -0.78 | 0.0663, -0.92 | 0.0549, -0.96 | 29.0 | 3.6 | 6.91/21.53 | 7.92/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2513 | 0.6702, 2.14 | 0.1158, 1.01 | 0.1032, 0.52 | 0.3838, 1.19 | 0.3713, 1.13 | 0.329, 0.93 | 31.4 | 4.5 | 7.6/20.56 | 7.61/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 735 | 2.5693, 2.73 | 1.0691, 1.21 | -0.0145, -0.49 | 1.4564, 1.28 | 1.458, 1.33 | 1.4942, 1.39 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1292 | 0.0307, 0.46 | 0.0585, 0.26 | -0.2186, -0.5 | 0.0578, 0.22 | 0.0599, 0.23 | -0.138, -0.25 | 33.3 | 5.1 | 8.17/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1066 | 0.5346, 0.54 | 0.3264, 0.5 | 0.3638, 0.89 | 0.549, 0.76 | 0.535, 0.74 | 0.4004, 0.48 | 34.0 | 5.0 | 7.85/24.51 | 8.17/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.632, 1.1 | 0.1047, 0.38 | 0.0348, 0.07 | 0.1358, 0.39 | 0.1385, 0.39 | 0.1009, 0.38 | 35.0 | 5.1 | 8.01/24.88 | 8.61/26.83 | 12.0 |
