# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 272 | -0.8003, -1.59 | -1.1213, -2.1 | -0.5824, -1.24 | -0.9393, -1.83 | -0.8927, -1.79 | -0.8927, -1.79 | 25.6 | 0.0 | 5.12/15.03 | 3.54/15.21 | 10.27 |
| D_MOM_L21_z0.5 | 231 | 0.7613, 1.55 | 0.6088, 1.21 | 0.6425, 1.27 | 0.5766, 1.28 | 0.5473, 1.21 | 0.6825, 1.3 | 21.8 | 0.4 | 4.34/14.37 | 4.47/16.92 | 10.36 |
| D_MOM_L14_z1.0 | 76 | -0.5478, -0.19 | -0.4317, 0.02 | -0.5347, -0.53 | -0.4735, -0.14 | -0.5666, -0.2 | -0.5666, -0.2 | 20.0 | 0.0 | 5.12/12.72 | 3.29/13.87 | 9.84 |
| D_CSM_mom_L7 | 169 | -1.4575, -1.66 | -1.149, -1.46 | -1.1038, -1.57 | -1.3317, -1.59 | -1.3512, -1.62 | -1.3512, -1.62 | 22.6 | 0.6 | 5.42/16.17 | 3.64/13.95 | 11.33 |
| D_CSM_mom_L14 | 144 | 0.486, 0.5 | -0.2033, -0.51 | 0.0071, -0.2 | 0.2125, 0.23 | 0.241, 0.23 | 0.4509, 0.45 | 25.2 | 1.4 | 5.12/15.31 | 3.75/17.77 | 11.41 |
| D_CSM_mom_L30 | 118 | 0.5033, -0.32 | 0.1035, -0.45 | 0.4669, 0.32 | 0.1157, -0.62 | 0.2171, -0.49 | 0.4886, -0.27 | 21.2 | 0.9 | 4.28/14.82 | 5.22/17.44 | 10.7 |
