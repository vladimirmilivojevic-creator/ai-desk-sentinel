# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 261 | -0.9859, -1.8 | -1.3122, -2.32 | -0.7766, -1.51 | -1.1283, -2.03 | -1.0806, -1.99 | -1.0806, -1.99 | 25.8 | 0.0 | 5.13/15.03 | 3.51/13.78 | 10.05 |
| D_MOM_L21_z0.5 | 227 | 0.2373, 0.98 | 0.3555, 0.82 | 0.4124, 0.88 | 0.1858, 0.77 | 0.1552, 0.7 | 0.1552, 0.7 | 21.8 | 0.0 | 4.42/14.41 | 4.19/15.4 | 10.33 |
| D_MOM_L14_z1.0 | 76 | -0.5478, -0.19 | -0.4317, 0.02 | -0.5347, -0.53 | -0.4735, -0.14 | -0.5666, -0.2 | -0.5666, -0.2 | 20.0 | 0.0 | 5.12/12.72 | 3.29/13.87 | 9.84 |
| D_CSM_mom_L7 | 166 | -1.4402, -1.64 | -1.1782, -1.53 | -1.111, -1.59 | -1.3147, -1.58 | -1.3345, -1.61 | -1.3345, -1.61 | 22.4 | 0.6 | 5.33/15.9 | 3.57/13.87 | 11.29 |
| D_CSM_mom_L14 | 140 | -0.2285, -0.65 | -0.5362, -1.29 | -0.3019, -0.99 | -0.2935, -0.74 | -0.2644, -0.73 | -0.2644, -0.73 | 25.0 | 0.7 | 5.12/15.31 | 3.75/16.69 | 11.41 |
| D_CSM_mom_L30 | 114 | -0.3891, -1.01 | -0.3035, -0.83 | 0.1746, 0.03 | -0.5073, -1.18 | -0.4041, -1.04 | -0.4041, -1.04 | 21.6 | 0.0 | 4.48/14.82 | 5.17/16.54 | 10.7 |
