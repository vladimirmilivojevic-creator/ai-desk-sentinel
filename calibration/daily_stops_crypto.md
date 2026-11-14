# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2838 | -0.0076, -0.51 | -0.0585, -0.72 | 0.0867, -0.46 | -0.0024, -0.88 | -0.0566, -1.01 | -0.0681, -1.06 | 29.2 | 3.6 | 6.95/21.55 | 7.78/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2487 | 0.5556, 1.93 | -0.0011, 0.77 | -0.0069, 0.24 | 0.2664, 0.97 | 0.2538, 0.91 | 0.2111, 0.71 | 31.6 | 4.5 | 7.63/20.59 | 7.48/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1283 | 0.0631, 0.56 | 0.0681, 0.32 | -0.2149, -0.47 | 0.0997, 0.34 | 0.1018, 0.35 | -0.0972, -0.13 | 33.1 | 5.1 | 8.14/24.21 | 7.92/25.38 | 12.0 |
| D_CSM_mom_L14 | 1065 | 0.5568, 0.59 | 0.3015, 0.42 | 0.3518, 0.85 | 0.548, 0.75 | 0.5339, 0.73 | 0.3992, 0.47 | 33.8 | 5.0 | 7.84/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 919 | 0.6468, 1.1 | 0.1038, 0.32 | 0.0393, 0.04 | 0.1651, 0.4 | 0.1678, 0.39 | 0.1302, 0.39 | 34.8 | 5.1 | 8.0/24.54 | 8.61/26.83 | 12.0 |
