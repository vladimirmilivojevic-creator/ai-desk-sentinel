# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2817 | -0.0299, -0.57 | -0.0781, -0.79 | 0.087, -0.46 | -0.0248, -0.95 | -0.079, -1.08 | -0.0906, -1.13 | 29.2 | 3.6 | 6.92/21.56 | 7.73/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2463 | 0.4988, 1.82 | -0.062, 0.65 | -0.0482, 0.17 | 0.2075, 0.86 | 0.1948, 0.8 | 0.1517, 0.6 | 31.9 | 4.6 | 7.66/20.69 | 7.44/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1281 | 0.0939, 0.7 | 0.0734, 0.37 | -0.2092, -0.42 | 0.1155, 0.43 | 0.1176, 0.43 | -0.082, -0.04 | 32.9 | 5.1 | 8.11/23.99 | 7.79/25.38 | 12.0 |
| D_CSM_mom_L14 | 1060 | 0.5681, 0.61 | 0.3, 0.44 | 0.3731, 0.93 | 0.5542, 0.77 | 0.5402, 0.75 | 0.4053, 0.49 | 33.7 | 5.0 | 7.7/24.34 | 8.06/28.34 | 12.0 |
| D_CSM_mom_L30 | 917 | 0.5989, 1.0 | 0.0397, 0.19 | -0.0382, -0.16 | 0.1099, 0.28 | 0.1126, 0.28 | 0.0749, 0.28 | 34.8 | 5.2 | 8.0/24.44 | 8.44/26.83 | 12.0 |
