# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2816 | -0.0281, -0.57 | -0.0764, -0.79 | 0.089, -0.45 | -0.023, -0.94 | -0.0773, -1.08 | -0.0889, -1.12 | 29.2 | 3.6 | 6.93/21.56 | 7.75/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2465 | 0.4985, 1.82 | -0.0623, 0.65 | -0.0512, 0.14 | 0.2072, 0.86 | 0.1945, 0.8 | 0.1514, 0.6 | 31.9 | 4.6 | 7.66/20.69 | 7.44/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1281 | 0.1045, 0.71 | 0.084, 0.38 | -0.2079, -0.43 | 0.1261, 0.44 | 0.1282, 0.45 | -0.0713, -0.03 | 32.8 | 5.1 | 8.11/23.99 | 7.87/25.38 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5762, 0.61 | 0.3083, 0.44 | 0.3723, 0.9 | 0.5624, 0.77 | 0.5483, 0.75 | 0.4135, 0.5 | 33.7 | 5.0 | 7.74/24.34 | 8.06/28.34 | 12.0 |
| D_CSM_mom_L30 | 917 | 0.6019, 1.0 | 0.0427, 0.19 | -0.0352, -0.16 | 0.1129, 0.28 | 0.1156, 0.28 | 0.0779, 0.28 | 34.8 | 5.2 | 8.0/24.44 | 8.44/26.83 | 12.0 |
