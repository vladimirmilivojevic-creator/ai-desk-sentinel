# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2855 | 0.1125, -0.43 | 0.058, -0.59 | 0.1946, -0.3 | 0.1207, -0.78 | 0.0671, -0.91 | 0.0557, -0.96 | 29.0 | 3.6 | 6.92/21.53 | 7.93/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2516 | 0.7064, 2.18 | 0.1525, 1.05 | 0.135, 0.56 | 0.4207, 1.23 | 0.4084, 1.17 | 0.3661, 0.97 | 31.3 | 4.5 | 7.57/20.52 | 7.65/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 735 | 2.5693, 2.73 | 1.0691, 1.21 | -0.0145, -0.49 | 1.4564, 1.28 | 1.458, 1.33 | 1.4942, 1.39 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1291 | 0.0299, 0.45 | 0.0543, 0.24 | -0.2139, -0.5 | 0.0571, 0.21 | 0.0592, 0.22 | -0.139, -0.26 | 33.4 | 5.1 | 8.17/24.24 | 7.93/25.74 | 12.0 |
| D_CSM_mom_L14 | 1068 | 0.5185, 0.49 | 0.3146, 0.45 | 0.3558, 0.85 | 0.5329, 0.71 | 0.5189, 0.69 | 0.3843, 0.43 | 34.1 | 5.0 | 7.86/24.51 | 8.17/28.34 | 12.0 |
| D_CSM_mom_L30 | 919 | 0.5955, 1.05 | 0.0788, 0.32 | 0.0177, 0.02 | 0.0924, 0.32 | 0.0951, 0.32 | 0.0574, 0.31 | 35.2 | 5.1 | 8.12/24.88 | 8.61/26.83 | 12.0 |
