# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2857 | 0.0668, -0.49 | 0.014, -0.66 | 0.1594, -0.37 | 0.0737, -0.84 | 0.0199, -0.98 | 0.0085, -1.02 | 29.1 | 3.6 | 6.9/21.53 | 7.83/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2507 | 0.628, 2.08 | 0.0763, 0.94 | 0.081, 0.47 | 0.3412, 1.13 | 0.3288, 1.06 | 0.2864, 0.87 | 31.4 | 4.5 | 7.57/20.56 | 7.51/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 732 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1287 | 0.0336, 0.48 | 0.0629, 0.3 | -0.2158, -0.46 | 0.0751, 0.27 | 0.0772, 0.27 | -0.1215, -0.2 | 33.1 | 5.1 | 8.14/24.28 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5341, 0.56 | 0.3112, 0.48 | 0.3434, 0.85 | 0.5417, 0.76 | 0.5276, 0.74 | 0.3929, 0.49 | 33.9 | 5.0 | 7.84/24.48 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 919 | 0.6284, 1.1 | 0.1054, 0.38 | 0.0452, 0.1 | 0.1452, 0.4 | 0.1479, 0.4 | 0.1103, 0.39 | 34.9 | 5.1 | 8.0/24.88 | 8.52/26.83 | 12.0 |
