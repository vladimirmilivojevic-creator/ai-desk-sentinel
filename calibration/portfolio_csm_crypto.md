# Portfolio simulacija: dugo/kratko korpa po poretku unutar grupe (CSM), dnevne svece, v3 univerzum

Generisano 2026-10-07T12:00Z, python -m lab.portfolio_sim crypto (LAB_CONFIG=config/lab_v3.json). Izbor L/H/k na ISTOM uzorku je optimisticki; zato test kasnjenja, izbor-pre-2025/test-posle-2025 i ciljana volatilnost sa JEDNIM unapred zadatim prozorom (30 d).

```
instrumenata u grupi crypto: 44

trosak po krugu 0.23% (paper+proklizavanje) | L H k | Sharpe | god. prinos % | pad % | po godinama (Sharpe)
  L 7 H14 k5 |  1.11 |   23.1 |  -19.3 | {2022: -0.12, 2023: -0.91, 2024: 1.88, 2025: 2.23, 2026: 0.55}
  L 7 H14 k8 |  1.02 |   16.9 |  -14.8 | {2022: -0.01, 2023: -0.64, 2024: 1.67, 2025: 2.11, 2026: 0.37}
  L14 H 7 k8 |  0.94 |   22.0 |  -24.8 | {2022: -0.09, 2023: -0.94, 2024: 1.76, 2025: 2.03, 2026: 0.34}
  L 7 H14 k3 |  0.91 |   24.5 |  -23.3 | {2022: -0.31, 2023: -0.88, 2024: 1.56, 2025: 1.88, 2026: 0.51}
  L14 H 7 k5 |  0.82 |   23.9 |  -32.0 | {2022: 0.11, 2023: -1.17, 2024: 1.76, 2025: 1.7, 2026: 0.29}
  L 7 H 7 k5 |  0.82 |   21.3 |  -24.8 | {2022: 0.11, 2023: -0.58, 2024: 1.41, 2025: 1.47, 2026: 0.52}
  L 7 H 7 k8 |  0.75 |   15.2 |  -22.5 | {2022: 0.44, 2023: -0.42, 2024: 1.25, 2025: 1.43, 2026: 0.23}
  L14 H 7 k3 |  0.74 |   27.3 |  -34.6 | {2022: 0.46, 2023: -1.01, 2024: 1.53, 2025: 1.29, 2026: 0.52}
  pozitivan Sharpe u 36 od 36 kombinacija; medijana Sharpe 0.49

trosak po krugu 0.10% (pravi taker kripto) | L H k | Sharpe | god. prinos % | pad % | po godinama (Sharpe)
  L 7 H14 k5 |  1.27 |   26.5 |  -16.8 | {2022: 0.2, 2023: -0.69, 2024: 2.02, 2025: 2.37, 2026: 0.72}
  L14 H 3 k8 |  1.25 |   31.8 |  -25.2 | {2022: 1.32, 2023: -0.5, 2024: 1.87, 2025: 2.05, 2026: 1.04}
  L14 H 7 k8 |  1.24 |   28.8 |  -21.2 | {2022: 0.43, 2023: -0.55, 2024: 2.01, 2025: 2.3, 2026: 0.62}
  L 7 H14 k8 |  1.23 |   20.3 |  -13.6 | {2022: 0.34, 2023: -0.36, 2024: 1.84, 2025: 2.29, 2026: 0.58}
  L14 H 3 k5 |  1.11 |   35.6 |  -28.5 | {2022: 1.61, 2023: -0.74, 2024: 2.03, 2025: 1.41, 2026: 1.03}
  L 7 H 7 k5 |  1.08 |   28.0 |  -22.2 | {2022: 0.57, 2023: -0.22, 2024: 1.62, 2025: 1.71, 2026: 0.79}
  L 7 H 7 k8 |  1.08 |   22.0 |  -19.8 | {2022: 0.93, 2023: 0.02, 2024: 1.52, 2025: 1.74, 2026: 0.59}
  L14 H 7 k5 |  1.06 |   30.6 |  -27.6 | {2022: 0.58, 2023: -0.86, 2024: 1.95, 2025: 1.91, 2026: 0.52}
  pozitivan Sharpe u 36 od 36 kombinacija; medijana Sharpe 0.78

trosak po krugu 0.06% (maker) | L H k | Sharpe | god. prinos % | pad % | po godinama (Sharpe)
  L14 H 3 k8 |  1.44 |   36.6 |  -23.4 | {2022: 1.61, 2023: -0.26, 2024: 2.02, 2025: 2.24, 2026: 1.23}
  L14 H 7 k8 |  1.32 |   30.9 |  -20.4 | {2022: 0.59, 2023: -0.43, 2024: 2.09, 2025: 2.38, 2026: 0.71}
  L 7 H14 k5 |  1.32 |   27.5 |  -16.0 | {2022: 0.31, 2023: -0.62, 2024: 2.06, 2025: 2.42, 2026: 0.77}
  L 7 H14 k8 |  1.29 |   21.4 |  -13.2 | {2022: 0.45, 2023: -0.27, 2024: 1.89, 2025: 2.35, 2026: 0.65}
  L14 H 3 k5 |  1.26 |   40.5 |  -25.2 | {2022: 1.88, 2023: -0.53, 2024: 2.15, 2025: 1.55, 2026: 1.19}
  L 7 H 7 k8 |  1.18 |   24.1 |  -19.0 | {2022: 1.08, 2023: 0.16, 2024: 1.6, 2025: 1.84, 2026: 0.7}
  L 7 H 7 k5 |  1.16 |   30.1 |  -21.4 | {2022: 0.71, 2023: -0.11, 2024: 1.68, 2025: 1.78, 2026: 0.87}
  L14 H 7 k5 |  1.13 |   32.7 |  -26.2 | {2022: 0.73, 2023: -0.76, 2024: 2.01, 2025: 1.98, 2026: 0.59}
  pozitivan Sharpe u 36 od 36 kombinacija; medijana Sharpe 0.85

KASNJENJE ULAZA (L14 H7 k5 i L7 H14 k5, trosak 0.23%): Sharpe | t
  L14 H7: +0d: 0.82 | t 1.66   +1d: 0.57 | t 1.16   +2d: 0.43 | t 0.88   +3d: 0.32 | t 0.65
  L7 H14: +0d: 1.11 | t 2.24   +1d: 0.93 | t 1.89   +2d: 0.85 | t 1.72   +3d: 0.73 | t 1.47

IZBOR PRE 2025, TEST POSLE 2025 (sve 36 kombinacija; Sharpe pre | Sharpe posle | t posle | L H k):
   0.91 |  0.17 | t  0.23 | L30 H7 k5
   0.85 |  0.15 | t  0.20 | L21 H14 k8
   0.81 | -0.04 | t -0.05 | L30 H7 k8
   0.74 |  0.02 | t  0.03 | L21 H14 k5
   0.74 |  1.55 | t  2.05 | L7 H14 k5
  medijana Sharpe posle 2025 po svim kombinacijama: 0.36; pozitivnih 31/36; korelacija izbor->test: 0.13

CILJANA VOLATILNOST NA NIVOU KORPE (samo smanjenje, cap 1.0, trosak 0.23%; Sharpe | pad % | god. prinos %; medijana preko 36 kombinacija):
  cilj bez: Sharpe 0.49 | pad -33.3 | prinos 16.7 | pozitivnih 36/36
  cilj 25%: Sharpe 0.55 | pad -29.6 | prinos 12.7 | pozitivnih 36/36
  cilj 20%: Sharpe 0.52 | pad -25.5 | prinos 10.8 | pozitivnih 36/36
  cilj 15%: Sharpe 0.52 | pad -21.3 | prinos 8.5 | pozitivnih 35/36
  L7 H14 k5: bez {'sharpe': 1.108, 'max_dd_pct': -19.32} -> cilj 20% {'sharpe': 1.062, 'max_dd_pct': -19.19}
     po godinama (cilj 20%): {2022: -0.12, 2023: -0.91, 2024: 1.98, 2025: 2.19, 2026: 0.61}
  L14 H7 k5: bez {'sharpe': 0.824, 'max_dd_pct': -32.01} -> cilj 20% {'sharpe': 0.723, 'max_dd_pct': -28.87}
     po godinama (cilj 20%): {2022: 0.11, 2023: -1.07, 2024: 1.88, 2025: 1.77, 2026: 0.17}
  L14 H7 k5 samo 2026: Sharpe 0.287, t 0.25, prinos 8.4% god., dana 279
  L7 H14 k5 samo 2026: Sharpe 0.552, t 0.48, prinos 11.4% god., dana 279
```
