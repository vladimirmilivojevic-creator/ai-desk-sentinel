# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2835 | -0.01, -0.53 | -0.061, -0.74 | 0.0843, -0.49 | -0.0049, -0.9 | -0.059, -1.03 | -0.0706, -1.08 | 29.2 | 3.6 | 6.95/21.55 | 7.77/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2485 | 0.5556, 1.93 | -0.0011, 0.77 | -0.0069, 0.24 | 0.2664, 0.97 | 0.2538, 0.91 | 0.2111, 0.71 | 31.6 | 4.5 | 7.63/20.59 | 7.48/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1283 | 0.0703, 0.6 | 0.0626, 0.31 | -0.2217, -0.48 | 0.0995, 0.36 | 0.1016, 0.36 | -0.0972, -0.11 | 33.0 | 5.1 | 8.14/24.01 | 7.92/25.38 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5486, 0.59 | 0.2946, 0.42 | 0.3523, 0.87 | 0.5398, 0.75 | 0.5258, 0.73 | 0.391, 0.47 | 33.9 | 5.0 | 7.81/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 920 | 0.637, 1.07 | 0.098, 0.31 | 0.0268, 0.0 | 0.1553, 0.37 | 0.158, 0.37 | 0.1204, 0.36 | 34.7 | 5.1 | 8.0/24.54 | 8.56/26.83 | 12.0 |
