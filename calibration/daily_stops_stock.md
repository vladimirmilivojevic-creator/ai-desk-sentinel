# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 244 | -0.755, -1.81 | -1.0517, -2.23 | -0.6056, -1.57 | -0.9133, -2.05 | -0.8612, -2.0 | -0.8612, -2.0 | 24.2 | 0.0 | 5.04/13.51 | 3.56/12.95 | 9.93 |
| D_MOM_L21_z0.5 | 213 | 0.3033, 0.92 | 0.2011, 0.58 | 0.2906, 0.64 | 0.1713, 0.77 | 0.1386, 0.7 | 0.1386, 0.7 | 21.3 | 0.0 | 4.24/13.58 | 4.15/14.48 | 10.05 |
| D_MOM_L14_z1.0 | 73 | -0.574, -0.19 | -0.4545, 0.02 | -0.4541, -0.39 | -0.4955, -0.14 | -0.5938, -0.21 | -0.5938, -0.21 | 19.7 | 0.0 | 4.76/12.03 | 3.29/13.74 | 9.76 |
| D_CSM_mom_L7 | 158 | -1.5031, -1.87 | -1.2728, -1.85 | -1.2566, -2.12 | -1.3745, -1.82 | -1.3955, -1.85 | -1.3955, -1.85 | 22.4 | 0.7 | 5.45/15.31 | 3.57/12.88 | 11.24 |
| D_CSM_mom_L14 | 131 | -0.2052, -0.7 | -0.3524, -0.94 | -0.1973, -0.73 | -0.2743, -0.78 | -0.2433, -0.78 | -0.2433, -0.78 | 24.2 | 0.8 | 5.12/15.31 | 3.75/17.65 | 11.4 |
| D_CSM_mom_L30 | 109 | -0.3297, -0.96 | -0.0784, -0.64 | 0.342, 0.19 | -0.2982, -1.01 | -0.189, -0.87 | -0.189, -0.87 | 21.0 | 0.0 | 4.19/14.82 | 5.22/17.44 | 10.73 |
