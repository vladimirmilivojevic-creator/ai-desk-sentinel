# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2862 | 0.1276, -0.42 | 0.071, -0.64 | 0.205, -0.34 | 0.1357, -0.77 | 0.0823, -0.91 | 0.0709, -0.95 | 29.0 | 3.6 | 6.9/21.53 | 7.93/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2529 | 0.7305, 2.22 | 0.1706, 1.09 | 0.1546, 0.61 | 0.4459, 1.28 | 0.4336, 1.21 | 0.3915, 1.02 | 31.2 | 4.5 | 7.55/20.52 | 7.69/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 735 | 2.572, 2.75 | 1.0738, 1.23 | -0.0083, -0.47 | 1.4606, 1.29 | 1.4622, 1.34 | 1.4984, 1.4 | 34.8 | 8.9 | 8.36/21.98 | 9.39/33.89 | 12.0 |
| D_CSM_mom_L7 | 1290 | 0.0291, 0.45 | 0.0462, 0.24 | -0.2149, -0.49 | 0.0445, 0.2 | 0.0466, 0.2 | -0.1514, -0.28 | 33.4 | 5.1 | 8.17/24.24 | 7.93/25.74 | 12.0 |
| D_CSM_mom_L14 | 1069 | 0.5265, 0.52 | 0.3128, 0.47 | 0.3694, 0.89 | 0.5409, 0.73 | 0.5269, 0.72 | 0.3926, 0.46 | 34.2 | 5.0 | 7.86/24.48 | 8.17/28.22 | 12.0 |
| D_CSM_mom_L30 | 922 | 0.6078, 1.09 | 0.0915, 0.37 | 0.0467, 0.08 | 0.1011, 0.36 | 0.1022, 0.36 | 0.0646, 0.35 | 35.3 | 5.1 | 8.12/24.88 | 8.65/26.83 | 12.0 |
