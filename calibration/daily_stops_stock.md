# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 230 | -0.8628, -1.95 | -1.2196, -2.44 | -0.8759, -2.04 | -1.0025, -2.16 | -0.9763, -2.14 | -0.9763, -2.14 | 22.7 | 0.0 | 4.82/13.5 | 3.54/12.45 | 9.75 |
| D_MOM_L21_z0.5 | 202 | -0.1011, 0.02 | -0.2304, -0.39 | -0.0503, -0.3 | -0.1896, -0.1 | -0.2415, -0.18 | -0.2415, -0.18 | 21.4 | 0.0 | 4.2/13.58 | 3.99/14.31 | 9.64 |
| D_MOM_L14_z1.0 | 70 | -0.4989, -0.05 | -0.3994, 0.14 | -0.3794, -0.24 | -0.3669, 0.08 | -0.5196, -0.07 | -0.5196, -0.07 | 19.1 | 0.0 | 5.12/12.03 | 3.29/13.74 | 9.1 |
| D_CSM_mom_L7 | 151 | -1.7577, -2.46 | -1.5335, -2.61 | -1.4263, -2.79 | -1.5983, -2.41 | -1.6441, -2.46 | -1.6441, -2.46 | 22.2 | 0.7 | 5.42/15.28 | 3.52/12.88 | 11.23 |
| D_CSM_mom_L14 | 127 | -0.1247, -0.59 | -0.367, -0.99 | -0.3511, -0.95 | -0.1703, -0.68 | -0.1874, -0.71 | -0.1874, -0.71 | 23.3 | 0.8 | 4.76/14.53 | 3.73/16.69 | 11.4 |
| D_CSM_mom_L30 | 104 | -0.7016, -1.2 | -0.3925, -0.88 | 0.039, -0.07 | -0.5536, -1.15 | -0.5539, -1.15 | -0.5539, -1.15 | 20.0 | 0.0 | 4.28/14.82 | 5.22/16.54 | 10.83 |
