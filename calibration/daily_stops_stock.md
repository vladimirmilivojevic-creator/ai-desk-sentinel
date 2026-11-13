# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 247 | -0.8685, -1.91 | -1.1167, -2.3 | -0.6587, -1.64 | -1.0193, -2.14 | -0.9688, -2.1 | -0.9688, -2.1 | 24.4 | 0.0 | 5.04/14.5 | 3.61/13.78 | 9.93 |
| D_MOM_L21_z0.5 | 214 | -0.0291, 0.66 | 0.0845, 0.5 | 0.1438, 0.52 | -0.0225, 0.63 | -0.0545, 0.56 | -0.0545, 0.56 | 21.8 | 0.0 | 4.42/14.37 | 4.09/14.58 | 10.07 |
| D_MOM_L14_z1.0 | 74 | -0.7389, -0.45 | -0.618, -0.25 | -0.5621, -0.58 | -0.6616, -0.4 | -0.7585, -0.46 | -0.7585, -0.46 | 20.8 | 0.0 | 5.12/12.72 | 3.29/13.74 | 9.84 |
| D_CSM_mom_L7 | 161 | -1.5746, -1.9 | -1.2928, -1.82 | -1.2512, -2.06 | -1.4442, -1.85 | -1.4648, -1.88 | -1.4648, -1.88 | 22.6 | 0.6 | 5.42/15.9 | 3.56/13.55 | 11.24 |
| D_CSM_mom_L14 | 133 | -0.1653, -0.62 | -0.3115, -0.86 | -0.1575, -0.63 | -0.2339, -0.7 | -0.2032, -0.7 | -0.2032, -0.7 | 24.0 | 0.8 | 4.76/15.31 | 3.75/17.65 | 11.34 |
| D_CSM_mom_L30 | 110 | -0.3239, -0.95 | -0.0749, -0.64 | 0.3415, 0.19 | -0.2927, -1.01 | -0.1845, -0.87 | -0.1845, -0.87 | 20.8 | 0.0 | 4.28/14.82 | 5.22/17.44 | 10.7 |
