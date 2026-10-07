# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa stock

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%). Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 169 | -1.4545, -2.48 | -1.5682, -2.78 | -1.2463, -2.57 | -1.5273, -2.59 | 22.6 | 0.0 | 5.04/14.37 | 3.49/11.33 | 9.24 |
| D_MOM_L21_z0.5 | 148 | -0.607, -0.68 | -0.567, -0.66 | -0.2623, -0.45 | -0.7137, -0.79 | 23.0 | 0.0 | 4.42/13.58 | 3.51/14.31 | 8.79 |
| D_MOM_L14_z1.0 | 57 | -0.2003, 0.26 | 0.0813, 0.58 | 0.0665, 0.2 | -0.0597, 0.38 | 17.9 | 0.0 | 4.76/11.38 | 3.29/13.87 | 8.91 |
| D_CSM_mom_L7 | 127 | -1.7227, -2.79 | -1.6571, -2.97 | -1.6448, -3.2 | -1.7226, -2.84 | 23.3 | 0.8 | 5.36/16.27 | 3.81/12.88 | 10.89 |
| D_CSM_mom_L14 | 109 | -0.8675, -0.76 | -1.0449, -0.95 | -0.6949, -0.7 | -0.9072, -0.84 | 24.5 | 1.0 | 5.13/15.38 | 3.79/12.26 | 11.42 |
| D_CSM_mom_L30 | 84 | -0.4841, -0.23 | -1.0638, -0.73 | -0.6471, -0.49 | -1.0989, -0.71 | 21.8 | 0.0 | 4.76/15.9 | 4.61/14.48 | 11.32 |
