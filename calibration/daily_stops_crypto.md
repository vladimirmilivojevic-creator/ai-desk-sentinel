# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2819 | -0.0432, -0.59 | -0.0711, -0.78 | 0.0878, -0.44 | -0.0354, -0.96 | -0.0898, -1.09 | -0.1014, -1.14 | 29.1 | 3.6 | 6.92/21.55 | 7.69/24.75 | 12.0 |
| D_MOM_L21_z0.5 | 2461 | 0.4938, 1.8 | -0.067, 0.63 | -0.0495, 0.15 | 0.2025, 0.84 | 0.1898, 0.77 | 0.1467, 0.57 | 31.9 | 4.6 | 7.65/20.69 | 7.44/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1282 | 0.111, 0.72 | 0.0909, 0.39 | -0.1957, -0.4 | 0.1424, 0.46 | 0.1404, 0.46 | -0.0591, -0.02 | 32.7 | 5.1 | 8.05/23.99 | 7.77/25.38 | 12.0 |
| D_CSM_mom_L14 | 1061 | 0.5807, 0.62 | 0.3136, 0.46 | 0.3996, 0.97 | 0.5668, 0.78 | 0.5527, 0.76 | 0.4174, 0.51 | 33.6 | 5.0 | 7.66/24.34 | 8.06/28.34 | 12.0 |
| D_CSM_mom_L30 | 915 | 0.6226, 1.02 | 0.0552, 0.21 | -0.0181, -0.13 | 0.1365, 0.31 | 0.1393, 0.31 | 0.1014, 0.31 | 34.7 | 5.2 | 7.94/24.54 | 8.44/26.87 | 12.0 |
