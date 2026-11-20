# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2863 | 0.0529, -0.54 | 0.0055, -0.71 | 0.1519, -0.42 | 0.0611, -0.89 | 0.0074, -1.02 | -0.004, -1.07 | 29.1 | 3.6 | 6.92/21.55 | 7.83/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2505 | 0.6462, 2.12 | 0.0929, 1.0 | 0.0923, 0.52 | 0.3587, 1.17 | 0.3462, 1.11 | 0.3037, 0.91 | 31.4 | 4.5 | 7.6/20.58 | 7.56/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 733 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1288 | 0.0369, 0.48 | 0.0662, 0.3 | -0.2141, -0.46 | 0.0784, 0.27 | 0.0805, 0.28 | -0.1181, -0.2 | 33.1 | 5.1 | 8.14/24.28 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5438, 0.57 | 0.3212, 0.49 | 0.3548, 0.87 | 0.5514, 0.77 | 0.5374, 0.75 | 0.4027, 0.5 | 33.9 | 5.0 | 7.84/24.48 | 8.16/28.34 | 12.0 |
| D_CSM_mom_L30 | 920 | 0.6377, 1.1 | 0.1147, 0.38 | 0.0545, 0.1 | 0.1545, 0.4 | 0.1572, 0.4 | 0.1196, 0.39 | 34.9 | 5.1 | 8.0/24.88 | 8.61/26.83 | 12.0 |
