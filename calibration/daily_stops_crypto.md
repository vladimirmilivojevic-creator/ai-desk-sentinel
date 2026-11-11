# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%); 'x20' fiksan stop 20% i cilj 60%; 'x20bez' stop 20% bez cilja. Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | x20 srednje %, t | x20bez srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 2828 | -0.0191, -0.54 | -0.0673, -0.75 | 0.0801, -0.49 | -0.014, -0.91 | -0.0682, -1.05 | -0.0798, -1.09 | 29.2 | 3.6 | 6.95/21.56 | 7.77/24.87 | 12.0 |
| D_MOM_L21_z0.5 | 2474 | 0.5455, 1.91 | -0.0118, 0.75 | -0.0153, 0.22 | 0.256, 0.95 | 0.2434, 0.89 | 0.2006, 0.69 | 31.7 | 4.6 | 7.63/20.64 | 7.48/25.61 | 12.0 |
| D_MOM_L14_z1.0 | 728 | 2.5713, 2.73 | 1.0628, 1.2 | -0.0185, -0.49 | 1.4522, 1.27 | 1.4539, 1.32 | 1.4903, 1.38 | 35.0 | 8.9 | 8.37/22.07 | 9.39/34.1 | 12.0 |
| D_CSM_mom_L7 | 1284 | 0.0967, 0.67 | 0.0903, 0.4 | -0.2087, -0.4 | 0.126, 0.43 | 0.1281, 0.43 | -0.0709, -0.04 | 32.8 | 5.1 | 8.13/24.01 | 7.92/25.38 | 12.0 |
| D_CSM_mom_L14 | 1067 | 0.581, 0.59 | 0.3145, 0.42 | 0.3736, 0.88 | 0.5671, 0.75 | 0.5531, 0.73 | 0.4182, 0.48 | 33.7 | 5.0 | 7.74/24.34 | 8.14/28.34 | 12.0 |
| D_CSM_mom_L30 | 918 | 0.6568, 1.11 | 0.1015, 0.34 | 0.0249, 0.03 | 0.1678, 0.41 | 0.1705, 0.4 | 0.1328, 0.4 | 34.6 | 5.2 | 8.0/24.44 | 8.56/26.83 | 12.0 |
