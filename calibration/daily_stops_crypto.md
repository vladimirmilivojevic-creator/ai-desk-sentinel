# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2838 | 0.0151, -0.45 | -0.0359, -0.65 | 0.1096, -0.37 | 0.0202, -0.82 | -0.0339, -0.95 | -0.0454, -0.99 | 29.1 | 3.6 | 6.93/21.55 | 7.8/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2486 | 0.5714, 1.99 | 0.0149, 0.84 | 0.0128, 0.33 | 0.2823, 1.03 | 0.2697, 0.97 | 0.227, 0.77 | 31.6 | 4.5 | 7.63/20.59 | 7.51/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1284 | 0.0668, 0.57 | 0.0813, 0.34 | -0.2019, -0.44 | 0.1068, 0.35 | 0.1089, 0.36 | -0.0901, -0.12 | 33.1 | 5.1 | 8.14/24.22 | 7.93/25.74 | 12.0 |
| D_CSM_mom_L14 | 1064 | 0.5265, 0.53 | 0.2899, 0.41 | 0.3472, 0.85 | 0.5295, 0.72 | 0.5154, 0.7 | 0.3805, 0.45 | 34.0 | 5.0 | 7.85/24.39 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.6299, 1.05 | 0.0977, 0.3 | 0.0362, 0.02 | 0.1502, 0.35 | 0.153, 0.35 | 0.1153, 0.34 | 34.9 | 5.1 | 8.0/24.54 | 8.61/26.83 | 12.0 |
