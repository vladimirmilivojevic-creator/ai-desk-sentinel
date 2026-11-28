# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2861 | 0.1228, -0.43 | 0.0669, -0.65 | 0.2017, -0.35 | 0.131, -0.78 | 0.0775, -0.91 | 0.0662, -0.96 | 29.0 | 3.6 | 6.91/21.53 | 7.93/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2530 | 0.7294, 2.21 | 0.1695, 1.07 | 0.1534, 0.59 | 0.4448, 1.26 | 0.4324, 1.2 | 0.3903, 1.0 | 31.2 | 4.5 | 7.55/20.52 | 7.69/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 735 | 2.572, 2.75 | 1.0738, 1.23 | -0.0083, -0.47 | 1.4606, 1.29 | 1.4622, 1.34 | 1.4984, 1.4 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1292 | 0.0178, 0.43 | 0.0316, 0.19 | -0.2241, -0.52 | 0.0332, 0.18 | 0.0353, 0.18 | -0.1622, -0.3 | 33.5 | 5.1 | 8.17/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1070 | 0.5367, 0.52 | 0.323, 0.48 | 0.3644, 0.85 | 0.5511, 0.74 | 0.5371, 0.72 | 0.4027, 0.46 | 34.2 | 5.0 | 7.87/24.48 | 8.2/28.22 | 12.0 |
| D_CSM_mom_L30 | 921 | 0.5995, 1.07 | 0.082, 0.35 | 0.0321, 0.05 | 0.0916, 0.34 | 0.0928, 0.34 | 0.0551, 0.33 | 35.4 | 5.1 | 8.16/24.88 | 8.61/26.83 | 12.0 |
