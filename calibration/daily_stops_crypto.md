# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2828 | -0.0116, -0.52 | -0.0606, -0.73 | 0.0882, -0.46 | -0.0065, -0.89 | -0.0607, -1.03 | -0.0722, -1.07 | 29.2 | 3.6 | 6.95/21.55 | 7.77/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2482 | 0.5499, 1.94 | -0.0073, 0.78 | -0.0107, 0.26 | 0.2604, 0.98 | 0.2479, 0.92 | 0.205, 0.72 | 31.7 | 4.6 | 7.63/20.59 | 7.48/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1285 | 0.0785, 0.63 | 0.0712, 0.35 | -0.2139, -0.44 | 0.1076, 0.39 | 0.1098, 0.39 | -0.0888, -0.09 | 32.9 | 5.1 | 8.13/24.01 | 7.9/25.38 | 12.0 |
| D_CSM_mom_L14 | 1066 | 0.5795, 0.59 | 0.3128, 0.42 | 0.3733, 0.88 | 0.5657, 0.75 | 0.5516, 0.73 | 0.4166, 0.48 | 33.8 | 5.0 | 7.74/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 920 | 0.6448, 1.09 | 0.1064, 0.33 | 0.0367, 0.03 | 0.1637, 0.39 | 0.1664, 0.39 | 0.1288, 0.38 | 34.6 | 5.1 | 7.94/24.54 | 8.56/26.83 | 12.0 |
