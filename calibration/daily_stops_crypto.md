# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2821 | -0.028, -0.57 | -0.0523, -0.76 | 0.1125, -0.41 | -0.0229, -0.95 | -0.0771, -1.08 | -0.0887, -1.13 | 29.0 | 3.6 | 6.87/21.56 | 7.74/24.81 | 12.0 |
| D_MOM_L21_z0.5 | 2464 | 0.4944, 1.81 | -0.0664, 0.64 | -0.0489, 0.16 | 0.203, 0.84 | 0.1904, 0.78 | 0.1473, 0.58 | 31.9 | 4.6 | 7.65/20.69 | 7.44/25.64 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1281 | 0.0956, 0.71 | 0.0752, 0.38 | -0.2058, -0.41 | 0.1172, 0.43 | 0.1193, 0.44 | -0.0799, -0.04 | 32.8 | 5.1 | 8.05/23.99 | 7.77/25.38 | 12.0 |
| D_CSM_mom_L14 | 1061 | 0.5818, 0.63 | 0.3147, 0.46 | 0.4015, 0.98 | 0.5679, 0.79 | 0.5538, 0.77 | 0.4185, 0.51 | 33.6 | 5.0 | 7.66/24.34 | 8.12/28.34 | 12.0 |
| D_CSM_mom_L30 | 915 | 0.6204, 1.02 | 0.0585, 0.21 | -0.0102, -0.11 | 0.1309, 0.31 | 0.1336, 0.3 | 0.0959, 0.3 | 34.7 | 5.2 | 7.94/24.44 | 8.35/26.83 | 12.0 |
