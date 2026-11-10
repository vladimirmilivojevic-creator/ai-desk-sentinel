# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 241 | -0.7329, -1.72 | -1.0327, -2.14 | -0.5937, -1.51 | -0.8918, -1.96 | -0.8396, -1.92 | -0.8396, -1.92 | 23.9 | 0.0 | 5.04/14.37 | 3.61/13.78 | 9.93 |
| D_MOM_L21_z0.5 | 210 | 0.3033, 0.92 | 0.2011, 0.58 | 0.2906, 0.64 | 0.1713, 0.77 | 0.1386, 0.7 | 0.1386, 0.7 | 21.3 | 0.0 | 4.24/13.58 | 4.15/14.48 | 9.98 |
| D_MOM_L14_z1.0 | 72 | -0.6362, -0.28 | -0.5149, -0.07 | -0.5146, -0.49 | -0.5566, -0.22 | -0.6563, -0.29 | -0.6563, -0.29 | 20.0 | 0.0 | 5.12/12.72 | 3.29/13.74 | 9.52 |
| D_CSM_mom_L7 | 156 | -1.5363, -1.93 | -1.3044, -1.91 | -1.2304, -2.03 | -1.4069, -1.88 | -1.428, -1.9 | -1.428, -1.9 | 22.5 | 0.7 | 5.42/15.31 | 3.56/12.88 | 11.24 |
| D_CSM_mom_L14 | 130 | -0.232, -0.75 | -0.3804, -0.99 | -0.224, -0.79 | -0.3016, -0.83 | -0.2704, -0.83 | -0.2704, -0.83 | 24.4 | 0.8 | 5.12/15.31 | 3.73/17.65 | 11.37 |
| D_CSM_mom_L30 | 109 | -0.3636, -1.0 | -0.1099, -0.7 | 0.3145, 0.13 | -0.3318, -1.06 | -0.2216, -0.92 | -0.2216, -0.92 | 21.2 | 0.0 | 4.28/14.82 | 5.22/17.44 | 10.73 |
