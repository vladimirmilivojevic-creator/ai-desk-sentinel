# Dnevna pravila: fiksno drzanje (testirano) prema stopu i cilju (uzivo), H=7 dana, grupa crypto

Neto posle troska 0.23%. Ulaz na zatvaranju svece. 'uzivo' = stop 2,5 x ATR (3-12%), cilj 3 x stop; 'uzi' 1,5 x ATR (2-8%); 'siri' 4 x ATR (5-20%). Prinos po trejdu je SIROV (nije oduzet prinos korpe), pa se poredi samo izmedju nacina za isto pravilo.

| pravilo | n | fiksno srednje %, t | uzivo srednje %, t | uzi srednje %, t | siri srednje %, t | pogodjen stop uzivo % | pogodjen cilj uzivo % | MAE p50/p90 % | MFE p50/p90 % | uzivo stop (medijana) % |
|---|---|---|---|---|---|---|---|---|---|---|
| D_MOM_L7_z0.5 | 3775 | 0.1061, 0.41 | 0.0569, -0.18 | 0.1305, -0.17 | 0.0985, -0.68 | 29.2 | 4.3 | 6.88/21.39 | 7.59/25.21 | 12.0 |
| D_MOM_L21_z0.5 | 3284 | 0.6057, 2.64 | -0.0015, 0.86 | 0.0474, 0.44 | 0.2859, 1.4 | 32.4 | 5.0 | 7.53/20.87 | 7.37/26.21 | 12.0 |
| D_MOM_L14_z1.0 | 988 | 3.1329, 3.65 | 0.8344, 1.11 | -0.0515, -0.36 | 1.364, 1.85 | 36.5 | 8.9 | 8.39/21.98 | 9.6/35.06 | 12.0 |
| D_CSM_mom_L7 | 1238 | 0.6628, 1.5 | 0.0547, 0.32 | 0.0072, -0.06 | 0.1913, 0.65 | 36.1 | 5.2 | 8.2/25.33 | 8.9/29.22 | 12.0 |
| D_CSM_mom_L14 | 1051 | 0.4766, 0.06 | -0.1632, -1.01 | -0.5025, -1.83 | 0.1497, -0.46 | 36.7 | 5.3 | 8.52/26.78 | 8.94/29.36 | 12.0 |
| D_CSM_mom_L30 | 926 | 1.0324, 1.18 | -0.0297, -0.3 | 0.0689, -0.42 | 0.1694, 0.03 | 36.7 | 5.3 | 8.45/25.83 | 8.77/29.86 | 12.0 |
