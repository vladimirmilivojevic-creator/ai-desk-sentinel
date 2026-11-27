# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 274 | -0.2805, -0.44 | -0.7966, -1.34 | -0.4761, -0.83 | -0.5299, -0.92 | -0.4847, -0.9 | -0.3702, -0.66 | 24.8 | 0.4 | 5.12/14.77 | 4.12/15.68 | 10.27 |
| D_MOM_L21_z0.5 | 237 | 0.82, 1.61 | 0.6305, 1.15 | 0.6814, 1.27 | 0.6377, 1.34 | 0.6088, 1.27 | 0.7422, 1.36 | 21.9 | 0.4 | 4.34/14.41 | 4.52/17.39 | 10.43 |
| D_MOM_L14_z1.0 | 76 | -0.3966, 0.03 | -0.282, 0.24 | -0.3837, -0.28 | -0.3233, 0.08 | -0.4151, 0.02 | -0.4151, 0.02 | 19.7 | 0.0 | 5.12/12.72 | 3.46/14.43 | 9.84 |
| D_CSM_mom_L7 | 173 | -0.8701, -0.96 | -0.8893, -1.15 | -0.8961, -1.29 | -0.9264, -1.13 | -0.9454, -1.16 | -0.7663, -0.92 | 22.6 | 1.2 | 5.36/16.17 | 3.64/14.58 | 11.37 |
| D_CSM_mom_L14 | 145 | 0.456, 0.53 | -0.203, -0.45 | -0.0304, -0.17 | 0.1476, 0.24 | 0.1755, 0.23 | 0.381, 0.45 | 25.4 | 1.4 | 5.13/15.31 | 4.05/17.77 | 11.42 |
| D_CSM_mom_L30 | 119 | 0.5172, -0.29 | 0.1243, -0.41 | 0.3748, 0.15 | 0.1363, -0.59 | 0.236, -0.46 | 0.5028, -0.24 | 20.9 | 0.9 | 4.28/14.82 | 5.22/17.44 | 10.67 |
