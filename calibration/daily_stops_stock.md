# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 256 | -0.8293, -1.69 | -1.1726, -2.2 | -0.699, -1.44 | -0.9763, -1.93 | -0.927, -1.89 | -0.927, -1.89 | 24.6 | 0.0 | 5.04/14.37 | 3.56/13.78 | 10.03 |
| D_MOM_L21_z0.5 | 221 | 0.1584, 0.76 | 0.2472, 0.53 | 0.2844, 0.54 | 0.1062, 0.54 | 0.0752, 0.47 | 0.0752, 0.47 | 21.6 | 0.0 | 4.42/14.37 | 4.15/15.2 | 10.1 |
| D_MOM_L14_z1.0 | 75 | -0.5492, -0.17 | -0.4299, 0.04 | -0.3748, -0.26 | -0.4729, -0.12 | -0.5685, -0.18 | -0.5685, -0.18 | 20.5 | 0.0 | 4.76/12.72 | 3.29/13.87 | 9.76 |
| D_CSM_mom_L7 | 163 | -1.6491, -2.07 | -1.3822, -2.03 | -1.316, -2.24 | -1.5212, -2.02 | -1.5414, -2.04 | -1.5414, -2.04 | 22.8 | 0.6 | 5.42/16.17 | 3.57/13.87 | 11.33 |
| D_CSM_mom_L14 | 138 | -0.1235, -0.53 | -0.4934, -1.21 | -0.2807, -0.92 | -0.191, -0.62 | -0.1607, -0.61 | -0.1607, -0.61 | 25.2 | 0.8 | 5.12/15.05 | 4.05/16.69 | 11.37 |
| D_CSM_mom_L30 | 113 | -0.34, -0.94 | -0.2529, -0.74 | 0.2254, 0.13 | -0.4604, -1.09 | -0.3553, -0.95 | -0.3553, -0.95 | 22.0 | 0.0 | 4.28/15.35 | 5.22/17.44 | 10.73 |
