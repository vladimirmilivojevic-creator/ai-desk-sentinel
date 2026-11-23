# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2858 | 0.098, -0.46 | 0.043, -0.62 | 0.1799, -0.34 | 0.1062, -0.81 | 0.0526, -0.94 | 0.0412, -0.99 | 29.0 | 3.6 | 6.92/21.53 | 7.92/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2508 | 0.6684, 2.13 | 0.1167, 1.01 | 0.1054, 0.52 | 0.3818, 1.19 | 0.3694, 1.12 | 0.3269, 0.93 | 31.3 | 4.5 | 7.58/20.56 | 7.6/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 735 | 2.5693, 2.73 | 1.0691, 1.21 | -0.0145, -0.49 | 1.4564, 1.28 | 1.458, 1.33 | 1.4942, 1.39 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1292 | 0.0442, 0.48 | 0.0805, 0.31 | -0.2031, -0.47 | 0.0802, 0.26 | 0.0823, 0.27 | -0.1158, -0.21 | 33.2 | 5.1 | 8.15/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1067 | 0.5237, 0.51 | 0.3155, 0.46 | 0.3529, 0.84 | 0.5382, 0.73 | 0.5241, 0.71 | 0.3895, 0.45 | 34.0 | 5.0 | 7.85/24.51 | 8.16/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.6252, 1.09 | 0.101, 0.37 | 0.0267, 0.04 | 0.1409, 0.39 | 0.1436, 0.39 | 0.1059, 0.38 | 35.0 | 5.2 | 8.01/24.88 | 8.56/26.83 | 12.0 |
