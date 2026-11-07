# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 238 | -0.788, -1.88 | -1.0821, -2.3 | -0.6905, -1.77 | -0.9366, -2.1 | -0.8965, -2.07 | -0.8965, -2.07 | 23.5 | 0.0 | 4.87/14.37 | 3.56/12.77 | 9.93 |
| D_MOM_L21_z0.5 | 206 | 0.1911, 0.47 | 0.088, 0.11 | 0.2665, 0.24 | 0.1, 0.35 | 0.0196, 0.24 | 0.0196, 0.24 | 21.1 | 0.0 | 4.2/13.58 | 4.07/14.4 | 9.92 |
| D_MOM_L14_z1.0 | 72 | -0.6438, -0.27 | -0.5208, -0.06 | -0.4515, -0.37 | -0.563, -0.22 | -0.6642, -0.29 | -0.6642, -0.29 | 20.3 | 0.0 | 5.12/12.72 | 3.29/13.74 | 9.52 |
| D_CSM_mom_L7 | 155 | -1.6148, -1.99 | -1.3799, -1.98 | -1.2484, -2.03 | -1.4837, -1.94 | -1.5051, -1.97 | -1.5051, -1.97 | 22.8 | 0.7 | 5.42/15.9 | 3.52/13.55 | 11.23 |
| D_CSM_mom_L14 | 129 | -0.1174, -0.46 | -0.3455, -0.85 | -0.2941, -0.75 | -0.1619, -0.55 | -0.1785, -0.59 | -0.1785, -0.59 | 23.6 | 0.8 | 4.72/14.53 | 3.73/16.69 | 11.34 |
| D_CSM_mom_L30 | 106 | -0.2967, -0.9 | 0.0064, -0.51 | 0.3935, 0.27 | -0.1516, -0.8 | -0.1519, -0.81 | -0.1519, -0.81 | 19.6 | 0.0 | 4.19/14.42 | 5.33/17.44 | 10.7 |
