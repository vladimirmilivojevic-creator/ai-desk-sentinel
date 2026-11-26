# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 274 | -0.377, -0.49 | -0.903, -1.41 | -0.5318, -0.87 | -0.6311, -0.98 | -0.5851, -0.97 | -0.4684, -0.72 | 25.3 | 0.4 | 5.12/14.77 | 3.56/15.42 | 10.27 |
| D_MOM_L21_z0.5 | 235 | 0.8384, 1.65 | 0.6872, 1.32 | 0.7207, 1.39 | 0.6553, 1.38 | 0.6263, 1.31 | 0.7603, 1.39 | 21.6 | 0.4 | 4.24/14.37 | 4.5/17.39 | 10.43 |
| D_MOM_L14_z1.0 | 76 | -0.3966, 0.03 | -0.282, 0.24 | -0.3837, -0.28 | -0.3233, 0.08 | -0.4151, 0.02 | -0.4151, 0.02 | 19.7 | 0.0 | 5.12/12.72 | 3.46/14.43 | 9.84 |
| D_CSM_mom_L7 | 172 | -1.4287, -1.65 | -1.1223, -1.45 | -1.057, -1.52 | -1.3045, -1.58 | -1.3237, -1.61 | -1.3237, -1.61 | 22.9 | 0.6 | 5.42/16.17 | 3.64/14.35 | 11.36 |
| D_CSM_mom_L14 | 145 | 0.5485, 0.58 | -0.1359, -0.39 | 0.073, -0.06 | 0.2769, 0.33 | 0.3052, 0.33 | 0.5136, 0.53 | 25.0 | 1.4 | 5.12/15.31 | 4.05/18.13 | 11.42 |
| D_CSM_mom_L30 | 118 | 0.5005, -0.32 | 0.1042, -0.45 | 0.4334, 0.26 | 0.1163, -0.62 | 0.2168, -0.49 | 0.4859, -0.27 | 21.1 | 0.9 | 4.28/14.82 | 5.22/17.44 | 10.7 |
