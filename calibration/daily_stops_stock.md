# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 266 | -1.0207, -1.93 | -1.3481, -2.46 | -0.7985, -1.61 | -1.1625, -2.16 | -1.115, -2.12 | -1.115, -2.12 | 26.1 | 0.0 | 5.13/15.03 | 3.51/13.78 | 10.11 |
| D_MOM_L21_z0.5 | 228 | 0.2719, 1.08 | 0.3896, 0.91 | 0.4462, 0.98 | 0.2207, 0.87 | 0.1902, 0.8 | 0.1902, 0.8 | 21.7 | 0.0 | 4.34/14.41 | 4.19/15.4 | 10.33 |
| D_MOM_L14_z1.0 | 76 | -0.5478, -0.19 | -0.4317, 0.02 | -0.5347, -0.53 | -0.4735, -0.14 | -0.5666, -0.2 | -0.5666, -0.2 | 20.0 | 0.0 | 5.12/12.72 | 3.29/13.87 | 9.84 |
| D_CSM_mom_L7 | 168 | -1.5587, -1.84 | -1.2464, -1.68 | -1.1549, -1.71 | -1.4314, -1.78 | -1.4511, -1.81 | -1.4511, -1.81 | 22.8 | 0.6 | 5.36/16.17 | 3.62/13.87 | 11.29 |
| D_CSM_mom_L14 | 142 | -0.2868, -0.78 | -0.5979, -1.42 | -0.3398, -1.09 | -0.3513, -0.86 | -0.3224, -0.85 | -0.3224, -0.85 | 25.5 | 0.7 | 5.12/15.31 | 3.73/16.69 | 11.41 |
| D_CSM_mom_L30 | 115 | 0.5033, -0.32 | 0.1035, -0.45 | 0.4669, 0.32 | 0.1157, -0.62 | 0.2171, -0.49 | 0.4886, -0.27 | 21.2 | 0.9 | 4.28/14.82 | 5.22/17.44 | 10.67 |
