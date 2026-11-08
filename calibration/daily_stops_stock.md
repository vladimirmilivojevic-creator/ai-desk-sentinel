# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 240 | -0.7495, -1.73 | -1.0424, -2.13 | -0.6525, -1.59 | -0.8975, -1.96 | -0.8576, -1.93 | -0.8576, -1.93 | 23.3 | 0.0 | 4.82/14.37 | 3.56/12.77 | 9.94 |
| D_MOM_L21_z0.5 | 207 | 0.2273, 0.58 | 0.1247, 0.22 | 0.3023, 0.36 | 0.1366, 0.45 | 0.0566, 0.35 | 0.0566, 0.35 | 21.0 | 0.0 | 4.2/13.58 | 4.07/14.4 | 9.88 |
| D_MOM_L14_z1.0 | 72 | -0.6438, -0.27 | -0.5208, -0.06 | -0.4515, -0.37 | -0.563, -0.22 | -0.6642, -0.29 | -0.6642, -0.29 | 20.3 | 0.0 | 5.12/12.72 | 3.29/13.74 | 9.52 |
| D_CSM_mom_L7 | 156 | -1.6148, -1.99 | -1.3799, -1.98 | -1.2484, -2.03 | -1.4837, -1.94 | -1.5051, -1.97 | -1.5051, -1.97 | 22.8 | 0.7 | 5.42/15.9 | 3.52/13.55 | 11.24 |
| D_CSM_mom_L14 | 130 | -0.3008, -0.79 | -0.4414, -1.03 | -0.354, -0.89 | -0.3235, -0.84 | -0.3402, -0.87 | -0.3402, -0.87 | 24.2 | 0.8 | 4.76/15.05 | 3.73/16.69 | 11.37 |
| D_CSM_mom_L30 | 108 | -0.3041, -0.92 | -0.0341, -0.57 | 0.3646, 0.22 | -0.2134, -0.9 | -0.1607, -0.83 | -0.1607, -0.83 | 20.4 | 0.0 | 4.19/14.42 | 5.22/17.44 | 10.83 |
