# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa macro

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%). Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 40 | -0.8315, -1.41 | -0.6866, -1.27 | -0.3645, -0.29 | -0.86, -1.45 | 8.1 | 0.0 | 2.33/6.9 | 2.31/4.63 | 4.76 |
| D_MOM_L21_z0.5 | 31 | -0.0111, -0.55 | -0.0433, -0.55 | 0.1319, -0.42 | -0.1334, -0.69 | 13.3 | 0.0 | 2.03/8.11 | 2.6/7.39 | 4.65 |
| D_MOM_L14_z1.0 | 11 | 0.2465, 0.2 | 0.3862, 0.33 | 0.1139, 0.08 | 0.2447, 0.2 | 18.2 | 0.0 | 2.33/7.99 | 1.53/6.1 | 4.35 |
