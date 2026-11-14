# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 252 | -0.9073, -2.0 | -1.1682, -2.41 | -0.717, -1.77 | -1.0568, -2.23 | -1.0066, -2.18 | -1.0066, -2.18 | 24.6 | 0.0 | 5.04/14.5 | 3.56/13.78 | 9.94 |
| D_MOM_L21_z0.5 | 216 | -0.0448, 0.62 | 0.0683, 0.45 | 0.1156, 0.43 | -0.0382, 0.59 | -0.0701, 0.51 | -0.0701, 0.51 | 21.7 | 0.0 | 4.42/14.37 | 4.09/14.58 | 10.09 |
| D_MOM_L14_z1.0 | 75 | -0.7389, -0.45 | -0.618, -0.25 | -0.5621, -0.58 | -0.6616, -0.4 | -0.7585, -0.46 | -0.7585, -0.46 | 20.8 | 0.0 | 5.12/12.72 | 3.29/13.74 | 9.76 |
| D_CSM_mom_L7 | 161 | -1.6333, -2.03 | -1.3629, -1.98 | -1.2959, -2.19 | -1.5038, -1.98 | -1.5242, -2.01 | -1.5242, -2.01 | 23.1 | 0.6 | 5.45/16.17 | 3.57/13.55 | 11.24 |
| D_CSM_mom_L14 | 136 | -0.1931, -0.68 | -0.4031, -1.04 | -0.2196, -0.78 | -0.2611, -0.76 | -0.2306, -0.76 | -0.2306, -0.76 | 24.6 | 0.8 | 5.12/15.31 | 4.05/17.65 | 11.37 |
| D_CSM_mom_L30 | 111 | -0.3879, -1.0 | -0.3, -0.82 | 0.1827, 0.04 | -0.5095, -1.17 | -0.4033, -1.02 | -0.4033, -1.02 | 22.2 | 0.0 | 4.48/15.35 | 5.22/17.44 | 10.67 |
