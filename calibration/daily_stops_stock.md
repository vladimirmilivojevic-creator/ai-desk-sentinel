# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 271 | -0.8483, -1.68 | -1.1718, -2.19 | -0.6287, -1.33 | -0.9884, -1.91 | -0.9414, -1.87 | -0.9414, -1.87 | 25.8 | 0.0 | 5.13/15.03 | 3.51/15.21 | 10.29 |
| D_MOM_L21_z0.5 | 231 | 0.752, 1.54 | 0.6046, 1.2 | 0.6209, 1.24 | 0.564, 1.26 | 0.5341, 1.19 | 0.6718, 1.28 | 21.7 | 0.5 | 4.34/14.37 | 4.35/15.73 | 10.36 |
| D_MOM_L14_z1.0 | 76 | -0.5478, -0.19 | -0.4317, 0.02 | -0.5347, -0.53 | -0.4735, -0.14 | -0.5666, -0.2 | -0.5666, -0.2 | 20.0 | 0.0 | 5.12/12.72 | 3.29/13.87 | 9.84 |
| D_CSM_mom_L7 | 169 | -1.4738, -1.67 | -1.1634, -1.48 | -1.0725, -1.47 | -1.3473, -1.61 | -1.3669, -1.64 | -1.3669, -1.64 | 22.7 | 0.6 | 5.36/16.17 | 3.62/13.95 | 11.33 |
| D_CSM_mom_L14 | 144 | -0.155, -0.48 | -0.464, -1.1 | -0.165, -0.61 | -0.2191, -0.56 | -0.1904, -0.56 | -0.1904, -0.56 | 25.4 | 0.7 | 5.13/15.31 | 3.75/17.65 | 11.41 |
| D_CSM_mom_L30 | 118 | 0.5033, -0.32 | 0.1035, -0.45 | 0.4669, 0.32 | 0.1157, -0.62 | 0.2171, -0.49 | 0.4886, -0.27 | 21.2 | 0.9 | 4.28/14.82 | 5.22/17.44 | 10.7 |
