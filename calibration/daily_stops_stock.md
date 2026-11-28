# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 276 | -0.3401, -0.53 | -0.8435, -1.43 | -0.5082, -0.9 | -0.5877, -1.02 | -0.5428, -1.0 | -0.4291, -0.75 | 25.0 | 0.4 | 5.13/14.77 | 4.12/15.68 | 10.35 |
| D_MOM_L21_z0.5 | 237 | 0.7548, 1.44 | 0.5765, 1.0 | 0.6473, 1.17 | 0.5733, 1.16 | 0.5445, 1.09 | 0.6774, 1.19 | 22.3 | 0.4 | 4.34/14.55 | 4.5/17.39 | 10.43 |
| D_MOM_L14_z1.0 | 76 | -0.3966, 0.03 | -0.282, 0.24 | -0.3837, -0.28 | -0.3233, 0.08 | -0.4151, 0.02 | -0.4151, 0.02 | 19.7 | 0.0 | 5.12/12.72 | 3.46/14.43 | 9.84 |
| D_CSM_mom_L7 | 175 | -0.8701, -0.96 | -0.8893, -1.15 | -0.8961, -1.29 | -0.9264, -1.13 | -0.9454, -1.16 | -0.7663, -0.92 | 22.6 | 1.2 | 5.36/16.17 | 3.64/14.58 | 11.37 |
| D_CSM_mom_L14 | 147 | 0.4789, 0.56 | -0.1755, -0.4 | -0.0041, -0.11 | 0.1726, 0.28 | 0.2004, 0.27 | 0.4044, 0.48 | 25.2 | 1.4 | 5.12/15.31 | 4.05/17.77 | 11.42 |
| D_CSM_mom_L30 | 120 | 0.4382, -0.32 | -0.0694, -0.52 | 0.2424, 0.07 | -0.0538, -0.68 | 0.0434, -0.55 | 0.3034, -0.32 | 22.0 | 0.8 | 4.55/15.36 | 5.33/17.44 | 10.67 |
