# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 231 | -0.9304, -2.05 | -1.2586, -2.51 | -0.8287, -1.99 | -1.0682, -2.25 | -1.0423, -2.23 | -1.0423, -2.23 | 23.3 | 0.0 | 4.82/13.51 | 3.54/12.65 | 9.73 |
| D_MOM_L21_z0.5 | 202 | -0.0087, 0.28 | -0.1373, -0.1 | 0.0418, 0.01 | -0.0968, 0.16 | -0.1484, 0.08 | -0.1484, 0.08 | 21.3 | 0.0 | 4.2/13.58 | 4.03/14.31 | 9.64 |
| D_MOM_L14_z1.0 | 71 | -0.4989, -0.05 | -0.3994, 0.14 | -0.3794, -0.24 | -0.3669, 0.08 | -0.5196, -0.07 | -0.5196, -0.07 | 19.1 | 0.0 | 5.12/12.03 | 3.29/13.74 | 9.28 |
| D_CSM_mom_L7 | 152 | -1.8153, -2.54 | -1.5874, -2.7 | -1.4513, -2.86 | -1.6582, -2.5 | -1.7033, -2.54 | -1.7033, -2.54 | 22.6 | 0.7 | 5.42/15.31 | 3.52/12.88 | 11.18 |
| D_CSM_mom_L14 | 128 | -0.2205, -0.69 | -0.4505, -1.08 | -0.3987, -1.02 | -0.2654, -0.78 | -0.2821, -0.81 | -0.2821, -0.81 | 23.8 | 0.8 | 4.76/14.53 | 3.73/15.62 | 11.37 |
| D_CSM_mom_L30 | 105 | -0.7016, -1.2 | -0.3925, -0.88 | 0.039, -0.07 | -0.5536, -1.15 | -0.5539, -1.15 | -0.5539, -1.15 | 20.0 | 0.0 | 4.28/14.82 | 5.22/16.54 | 10.73 |
