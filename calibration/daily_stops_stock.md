# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 259 | -0.7787, -1.65 | -1.1366, -2.19 | -0.6525, -1.4 | -0.9239, -1.88 | -0.8752, -1.85 | -0.8752, -1.85 | 24.7 | 0.0 | 5.04/14.5 | 3.54/14.42 | 10.04 |
| D_MOM_L21_z0.5 | 225 | 0.267, 1.02 | 0.3554, 0.81 | 0.3941, 0.85 | 0.2151, 0.81 | 0.1842, 0.74 | 0.1842, 0.74 | 21.5 | 0.0 | 4.42/14.37 | 4.19/15.4 | 10.22 |
| D_MOM_L14_z1.0 | 75 | -0.4942, -0.1 | -0.3766, 0.11 | -0.481, -0.44 | -0.419, -0.05 | -0.5133, -0.11 | -0.5133, -0.11 | 20.3 | 0.0 | 5.12/12.72 | 3.46/13.87 | 9.76 |
| D_CSM_mom_L7 | 164 | -1.4402, -1.64 | -1.1782, -1.53 | -1.111, -1.59 | -1.3147, -1.58 | -1.3345, -1.61 | -1.3345, -1.61 | 22.4 | 0.6 | 5.33/15.9 | 3.57/13.87 | 11.29 |
| D_CSM_mom_L14 | 139 | -0.1554, -0.6 | -0.5198, -1.27 | -0.3103, -1.0 | -0.2219, -0.68 | -0.1921, -0.68 | -0.1921, -0.68 | 24.8 | 0.8 | 4.89/15.05 | 3.75/16.69 | 11.4 |
| D_CSM_mom_L30 | 113 | -0.329, -0.92 | -0.2427, -0.73 | 0.2313, 0.14 | -0.4483, -1.08 | -0.3441, -0.94 | -0.3441, -0.94 | 21.8 | 0.0 | 4.48/15.35 | 5.22/17.44 | 10.73 |
