<!-- Nastalo 2026-10-10 komandom: python -m lab.insider_study <raspakovani kvartali> calibration/insider_study.md --xyz <imena xyz> (SEC Form 4, 15 kvartala 2023q1-2026q3, Yahoo dnevne cene) -->
# Insider klasteri: sta merenje kaze (2026-10-10)

Pitanje vlasnika: "rucno kupljen GME je najbolji trejd, zasto ga sistem ne nalazi, i kako da nalazi takve i bolje?" Ovde je odgovor na podacima, ne na utisku.

**Sazetak (sudovi su procena, brojke su ispod):**
- Pravilo "bar 2 razlicita insidera kupuju na trzistu u 30 dana, preko $100.000" (ono sto desk vec koristi) dalo je 3.056 dogadjaja u 2023-2026, a 2.722 ima cene. Posle troska 0,23% i oduzimanja SPY, prosek posle 20 trgovackih dana je oko +0,5%, ali medijana je -0,8%, t je oko 0 i nije bolje od slucajnih datuma istih akcija (p = 0,12). Posle 40 i 60 dana prosek postaje negativan (t oko -2,4). Zakljucak: pratnja insider klastera nema dokazanu prednost kad se ulazi tek posle prijave.
- "Juri": klasteri gde je cena pri ulazu preko 15% iznad prosecne cene insidera gube prosecno -1,6% do -2,4% za 20 dana, a "GME recept" (4 ili vise kupaca i juris preko 15%) ima -1,6% za 20 dana i -11,6% za 60 dana (n = 84). Pravilo "ne juri 15%" je dakle potvrdjeno podacima, a GME je izuzetak, ne pravilo.
- Jedini istrazivacki trag: ulaz ISPOD prosecne cene insidera (n = 858): +1,6% za 20 dana, t oko 2. To je 1 od oko 22 podgrupe koje su gledane bez korekcije, pa je to hipoteza za proveru unapred, ne nalaz.
- GME je u 2023-2026 imao 5 klastera: -13,6%, -9,4%, -2,4%, +0,8% i sadasnji (septembar 2026) +20,6%. Prosek -0,8%. Sadasnji je dobar, ali ista postavka je 3 od 5 puta lose zavrsila.
- Ogranicenja: izdavaoci bez Yahoo istorije (334 dogadjaja) su verovatno izbaceni sa berze (greska preziveli), pa je stvarnost verovatno losija; ulaz je konzervativno prvi otvoreni dan posle prijave; 27 dogadjaja je na akcijama koje Liquid trguje, premalo za zakljucak.


Dogadjaja po unapred zadatom pravilu: 3056, sa cenama: 2722 (bez cena: 334; izdavaoci bez Yahoo istorije su verovatno izbaceni sa berze, pa je ovo blago optimisticno - greska preziveli).
Mera: prinos od otvaranja prvog dana posle prijave do zatvaranja posle H trgovackih dana, MINUS SPY, MINUS trosak 0.23%. t je preko nedelja prijave. Placebo = isti izdavaoci, slucajni datumi.

## Svi dogadjaji, po horizontu

| H (dana) | n | nedelja | srednje % | medijana % | udeo > 0 | t | placebo srednje % | p protiv placeba |
|---|---|---|---|---|---|---|---|---|
| 5 | 2712 | 196 | +0.38 | -0.31 | 0.47 | 0.46 | -0.268 | 0.03 |
| 10 | 2697 | 195 | +0.55 | -0.42 | 0.47 | 0.31 | -0.123 | 0.055 |
| 20 | 2658 | 193 | +0.49 | -0.80 | 0.47 | -0.2 | 0.089 | 0.124 |
| 40 | 2581 | 189 | -0.85 | -2.06 | 0.44 | -2.33 | -0.229 | 0.632 |
| 60 | 2534 | 185 | -0.77 | -2.98 | 0.42 | -2.47 | 0.202 | 0.458 |

## Podgrupe (primarni horizont 20 dana; ostali su orijentacija). Podgrupe su istrazivacke, bez korekcije za mnogo poredjenja.

| podgrupa | n | srednje % | medijana % | udeo > 0 | t | srednje % (H=5) | srednje % (H=60) |
|---|---|---|---|---|---|---|---|
| SVE | 2658 | +0.49 | -0.80 | 0.47 | -0.2 | 0.379 | -0.774 |
| 2 kupca | 1738 | +0.47 | -0.81 | 0.47 | 0.15 | 0.141 | -0.166 |
| 3 kupca | 453 | +0.54 | -0.47 | 0.47 | 1.22 | 0.989 | -0.103 |
| 4+ kupaca | 467 | +0.50 | -0.98 | 0.47 | -1.46 | 0.666 | -3.717 |
| CEO/CFO/predsednik medju kupcima | 1643 | +0.81 | -0.55 | 0.48 | 0.31 | 0.573 | -0.585 |
| bez CEO/CFO | 1015 | -0.03 | -1.19 | 0.45 | -0.26 | 0.065 | -1.075 |
| iznos >= $500k | 1047 | +0.10 | -0.58 | 0.48 | 0.12 | 0.514 | -2.52 |
| iznos < $250k | 1035 | +1.12 | -0.81 | 0.46 | 1.19 | 0.431 | 0.438 |
| cena ulaza ispod proseka insidera | 858 | +1.57 | +0.18 | 0.51 | 1.97 | 0.487 | 0.082 |
| juri 0 do 15% | 1511 | +0.24 | -1.19 | 0.45 | 0.41 | 0.335 | -0.248 |
| juri 15 do 30% | 136 | -0.27 | -2.23 | 0.43 | -0.79 | 0.213 | -4.289 |
| juri preko 30% | 153 | -2.41 | -2.58 | 0.46 | -1.42 | 0.351 | -7.64 |
| GME recept: 4+ kupaca i juri preko 15% | 84 | -1.61 | -4.34 | 0.42 | -1.54 | 0.871 | -11.579 |
| bez prodaja u 30 d | 2265 | +0.54 | -0.77 | 0.47 | -0.39 | 0.407 | -0.795 |
| sa prodajama u 30 d | 393 | +0.22 | -1.02 | 0.46 | 0.36 | 0.217 | -0.657 |
| cena akcije < $10 | 852 | +1.08 | -1.83 | 0.45 | 0.61 | 1.114 | 0.108 |
| cena akcije $10-50 | 1347 | +0.14 | -0.81 | 0.47 | -0.2 | -0.119 | -1.313 |
| cena akcije >= $50 | 459 | +0.43 | +0.09 | 0.50 | 0.1 | 0.472 | -0.827 |
| godina 2023 | 717 | -0.21 | -1.12 | 0.46 | -0.54 | -0.14 | -2.122 |
| godina 2024 | 583 | +0.19 | -1.65 | 0.42 | 0.46 | 0.725 | 0.861 |
| godina 2025 | 779 | +1.19 | -0.28 | 0.49 | 0.75 | 0.588 | -0.536 |
| godina 2026 | 579 | +0.72 | -0.34 | 0.49 | -1.14 | 0.394 | -1.156 |

## Samo akcije koje se trguju na Liquid-u (xyz): 27 dogadjaja

| H | n | srednje % | udeo > 0 | t |
|---|---|---|---|---|
| 5 | 27 | -0.74 | 0.56 | -0.49 |
| 10 | 27 | +1.38 | 0.63 | 0.03 |
| 20 | 27 | +1.00 | 0.56 | -0.21 |
| 40 | 25 | -0.78 | 0.52 | -0.56 |
| 60 | 24 | -4.36 | 0.33 | -1.18 |

| akcija | datum prijave | kupaca | iznos $ | juri % | prinos 20 d % (minus SPY, trosak) |
|---|---|---|---|---|---|
| INTC | 2023-02-02 | 2 | 501860 | 6.5 | -8.22 |
| CRWD | 2023-02-14 | 2 | 1534958 | -70.5 | 15.71 |
| GME | 2023-06-12 | 2 | 335900 | 17.0 | -13.6 |
| INTC | 2023-08-10 | 2 | 252341 | -1.9 | 9.72 |
| GME | 2023-09-11 | 2 | 372626 | -1.2 | -9.44 |
| AVGO | 2023-09-19 | 2 | 10451290 | -90.2 | 5.62 |
| INTC | 2023-11-14 | 2 | 2746874 | 4.9 | 7.82 |
| BX | 2024-02-21 | 2 | 338750 | 2.0 | -4.25 |
| AAOI | 2024-03-18 | 3 | 700434 | 0.7 | -8.73 |
| RDDT | 2024-03-27 | 2 | 442000 | 60.4 | -18.6 |
| MRNA | 2025-03-04 | 2 | 6008569 | 3.8 | -14.23 |
| GME | 2025-04-07 | 2 | 10882700 | 15.2 | -2.39 |
| LLY | 2025-08-12 | 5 | 2894853 | 1.4 | 14.92 |
| AAOI | 2025-08-14 | 3 | 1000938 | -3.9 | 22.12 |
| MRVL | 2025-09-25 | 4 | 2109632 | 6.3 | -1.66 |
| DKNG | 2025-11-12 | 2 | 1060200 | 2.0 | 11.43 |
| BX | 2025-11-13 | 2 | 4050169 | -6.2 | 6.57 |
| GME | 2026-01-22 | 2 | 21870360 | 8.3 | 0.84 |
| USAR | 2026-01-29 | 2 | 2173380 | 6.5 | -16.71 |
| IBM | 2026-02-25 | 3 | 417157 | -15.9 | 5.47 |
| TSM | 2026-03-30 | 2 | 167190 | 478.3 | 10.11 |
| BOT | 2026-05-05 | 2 | 2900000 | 490.0 | -33.07 |
| QNT | 2026-06-08 | 11 | 24661920 | 2.2 | 22.62 |
| TSM | 2026-06-09 | 31 | 387879 | 430.1 | 2.81 |
| TSM | 2026-08-10 | 30 | 933009 | 455.8 | 4.37 |
| BABA | 2026-08-24 | 2 | 15272800 | 726.3 | -2.81 |
| GME | 2026-09-09 | 2 | 1230076 | 5.5 | 20.63 |
