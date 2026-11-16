# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 256 | -0.8435, -1.7 | -1.1034, -2.09 | -0.6414, -1.35 | -0.9924, -1.94 | -0.9425, -1.9 | -0.9425, -1.9 | 24.5 | 0.0 | 5.04/14.37 | 3.56/13.78 | 10.03 |
| D_MOM_L21_z0.5 | 219 | -0.0143, 0.6 | 0.0758, 0.37 | 0.1135, 0.37 | -0.0673, 0.39 | -0.0987, 0.32 | -0.0987, 0.32 | 21.9 | 0.0 | 4.54/14.41 | 4.09/14.8 | 10.1 |
| D_MOM_L14_z1.0 | 75 | -0.7389, -0.45 | -0.618, -0.25 | -0.5621, -0.58 | -0.6616, -0.4 | -0.7585, -0.46 | -0.7585, -0.46 | 20.8 | 0.0 | 5.12/12.72 | 3.29/13.74 | 9.76 |
| D_CSM_mom_L7 | 163 | -1.6333, -2.03 | -1.3629, -1.98 | -1.2959, -2.19 | -1.5038, -1.98 | -1.5242, -2.01 | -1.5242, -2.01 | 23.1 | 0.6 | 5.45/16.17 | 3.57/13.55 | 11.33 |
| D_CSM_mom_L14 | 138 | -0.1931, -0.68 | -0.4031, -1.04 | -0.2196, -0.78 | -0.2611, -0.76 | -0.2306, -0.76 | -0.2306, -0.76 | 24.6 | 0.8 | 5.12/15.31 | 4.05/17.65 | 11.37 |
| D_CSM_mom_L30 | 113 | -0.34, -0.94 | -0.2529, -0.74 | 0.2254, 0.13 | -0.4604, -1.09 | -0.3553, -0.95 | -0.3553, -0.95 | 22.0 | 0.0 | 4.28/15.35 | 5.22/17.44 | 10.73 |
