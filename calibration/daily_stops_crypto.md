# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2864 | 0.0782, -0.49 | 0.0245, -0.66 | 0.1626, -0.38 | 0.0864, -0.84 | 0.0329, -0.98 | 0.0215, -1.02 | 29.0 | 3.6 | 6.92/21.53 | 7.85/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2504 | 0.6512, 2.11 | 0.0981, 0.99 | 0.0929, 0.5 | 0.3639, 1.16 | 0.3514, 1.1 | 0.3089, 0.9 | 31.4 | 4.5 | 7.6/20.58 | 7.56/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 733 | 2.5693, 2.73 | 1.0691, 1.21 | -0.0145, -0.49 | 1.4564, 1.28 | 1.458, 1.33 | 1.4942, 1.39 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1292 | 0.0453, 0.48 | 0.0816, 0.31 | -0.2017, -0.46 | 0.0813, 0.27 | 0.0834, 0.27 | -0.1145, -0.21 | 33.1 | 5.1 | 8.14/24.24 | 7.92/25.74 | 12.0 |
| D_CSM_mom_L14 | 1067 | 0.5201, 0.51 | 0.3119, 0.45 | 0.3493, 0.84 | 0.5345, 0.72 | 0.5205, 0.7 | 0.3859, 0.45 | 34.0 | 5.0 | 7.85/24.51 | 8.16/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.6281, 1.09 | 0.1044, 0.37 | 0.0302, 0.04 | 0.1443, 0.39 | 0.147, 0.39 | 0.1094, 0.38 | 34.9 | 5.1 | 8.0/24.88 | 8.52/26.83 | 12.0 |
