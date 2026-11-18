# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 258 | -0.7509, -1.53 | -1.0915, -2.03 | -0.6217, -1.26 | -0.8968, -1.78 | -0.8479, -1.74 | -0.8479, -1.74 | 24.4 | 0.0 | 5.04/14.37 | 3.56/14.42 | 10.03 |
| D_MOM_L21_z0.5 | 225 | 0.1584, 0.76 | 0.2472, 0.53 | 0.2844, 0.54 | 0.1062, 0.54 | 0.0752, 0.47 | 0.0752, 0.47 | 21.6 | 0.0 | 4.42/14.37 | 4.15/15.2 | 10.22 |
| D_MOM_L14_z1.0 | 75 | -0.4942, -0.1 | -0.3766, 0.11 | -0.481, -0.44 | -0.419, -0.05 | -0.5133, -0.11 | -0.5133, -0.11 | 20.3 | 0.0 | 5.12/12.72 | 3.46/13.87 | 9.76 |
| D_CSM_mom_L7 | 164 | -1.5955, -2.03 | -1.3319, -1.98 | -1.2665, -2.19 | -1.4692, -1.98 | -1.4891, -2.01 | -1.4891, -2.01 | 22.5 | 0.6 | 5.36/16.17 | 3.57/13.87 | 11.29 |
| D_CSM_mom_L14 | 139 | -0.1512, -0.59 | -0.5184, -1.26 | -0.3073, -0.98 | -0.2182, -0.67 | -0.1882, -0.67 | -0.1882, -0.67 | 25.0 | 0.8 | 5.12/15.05 | 4.05/16.69 | 11.4 |
| D_CSM_mom_L30 | 113 | -0.34, -0.94 | -0.2529, -0.74 | 0.2254, 0.13 | -0.4604, -1.09 | -0.3553, -0.95 | -0.3553, -0.95 | 22.0 | 0.0 | 4.28/15.35 | 5.22/17.44 | 10.73 |
