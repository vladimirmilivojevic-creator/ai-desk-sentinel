# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2857 | 0.0343, -0.51 | -0.019, -0.69 | 0.1238, -0.41 | 0.0411, -0.87 | -0.0128, -1.0 | -0.0242, -1.05 | 29.1 | 3.6 | 6.93/21.55 | 7.81/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2500 | 0.6053, 2.04 | 0.0524, 0.9 | 0.0567, 0.41 | 0.3181, 1.08 | 0.3056, 1.02 | 0.2631, 0.82 | 31.5 | 4.5 | 7.58/20.58 | 7.48/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 732 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1287 | 0.0475, 0.52 | 0.0733, 0.33 | -0.2088, -0.43 | 0.0918, 0.32 | 0.0939, 0.33 | -0.105, -0.15 | 33.0 | 5.1 | 8.13/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5371, 0.56 | 0.3144, 0.47 | 0.346, 0.84 | 0.5447, 0.76 | 0.5306, 0.74 | 0.396, 0.49 | 33.9 | 5.0 | 7.84/24.48 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 917 | 0.6154, 1.05 | 0.0917, 0.32 | 0.0315, 0.04 | 0.1316, 0.35 | 0.1343, 0.35 | 0.0967, 0.34 | 34.9 | 5.1 | 8.0/24.88 | 8.46/26.83 | 12.0 |
