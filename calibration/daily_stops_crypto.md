# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2819 | -0.0282, -0.57 | -0.0764, -0.79 | 0.091, -0.45 | -0.023, -0.95 | -0.0773, -1.08 | -0.0889, -1.13 | 29.2 | 3.6 | 6.93/21.56 | 7.75/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2467 | 0.5331, 1.86 | -0.0252, 0.7 | -0.0181, 0.19 | 0.2431, 0.9 | 0.2305, 0.84 | 0.1875, 0.64 | 31.7 | 4.6 | 7.65/20.64 | 7.46/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1283 | 0.0852, 0.66 | 0.0787, 0.38 | -0.2085, -0.4 | 0.1144, 0.42 | 0.1166, 0.42 | -0.0826, -0.05 | 32.9 | 5.1 | 8.12/24.01 | 7.9/25.38 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.6, 0.66 | 0.3295, 0.49 | 0.384, 0.93 | 0.5861, 0.82 | 0.572, 0.8 | 0.4372, 0.54 | 33.7 | 5.0 | 7.81/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.6125, 1.01 | 0.0573, 0.21 | -0.0249, -0.12 | 0.1235, 0.3 | 0.1262, 0.3 | 0.0885, 0.29 | 34.6 | 5.2 | 8.0/24.44 | 8.44/26.83 | 12.0 |
