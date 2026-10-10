<!-- Nastalo 2026-10-10 posle upisa HYP-INS-1 (commit ff382c9): isti kod lab/insider_study.py bez izmena, SEC Form 4 kvartali 2021q1-2022q4 -->
# Ponavljanje na 2021-2022: insider klasteri (HYP-INS-1)

**Ishod HYP-INS-1 po unapred zadatim kriterijumima: ODBACENA.** Podgrupa "cena ulaza ispod proseka insidera": n = 427 (uslov n >= 100 ispunjen), srednje +0,04% za 20 dana (uslov > 0 jedva ispunjen), ali t = -0,97 (uslov t >= 1,5 NIJE ispunjen). Razlika prema ostatku klastera je oko +1,9 procentnih poena (uslov >= 0,5 ispunjen), ali uslovi su zadati svi zajedno.

Sta ostaje (procena): u OBA uzorka klasteri gde se cena juri preko 15-30% iznad cene insidera gube vise od ostalih (2023-2026: -0,3% i -2,4%; 2021-2022: -4,6% i -6,9% za 20 dana), pa je pravilo "ne juri" potvrdjeno dva puta. Nigde nema pozitivnog proseka koji je statisticki razlicit od nule: pratnja insider klastera nije izvor dobiti. 2022 je bio medvedji rezim, a 658 od 2.049 dogadjaja nema Yahoo cene (verovatno izbaceni sa berze), pa je pravi rezultat verovatno losiji od ovog. Kolona "placebo" u ovom uzorku nije vremenski uparena (slucajni datumi obuhvataju rast 2020-2021) i ne treba je citati.


Dogadjaja po unapred zadatom pravilu: 2049, sa cenama: 1391 (bez cena: 658; izdavaoci bez Yahoo istorije su verovatno izbaceni sa berze, pa je ovo blago optimisticno - greska preziveli).
Mera: prinos od otvaranja prvog dana posle prijave do zatvaranja posle H trgovackih dana, MINUS SPY, MINUS trosak 0.23%. t je preko nedelja prijave. Placebo = isti izdavaoci, slucajni datumi.

## Svi dogadjaji, po horizontu

| H (dana) | n | nedelja | srednje % | medijana % | udeo > 0 | t | placebo srednje % | p protiv placeba |
|---|---|---|---|---|---|---|---|---|
| 5 | 1384 | 104 | -0.31 | -0.28 | 0.48 | -2.18 | 2.119 | 0.632 |
| 10 | 1380 | 103 | -0.43 | -0.50 | 0.47 | -1.88 | 2.494 | 0.687 |
| 20 | 1379 | 103 | -1.32 | -1.24 | 0.45 | -2.65 | 4.806 | 0.95 |
| 40 | 1378 | 103 | -1.76 | -1.67 | 0.45 | -1.13 | 2.422 | 0.94 |
| 60 | 1376 | 103 | -2.42 | -2.32 | 0.44 | -3.09 | 1.787 | 0.915 |

## Podgrupe (primarni horizont 20 dana; ostali su orijentacija). Podgrupe su istrazivacke, bez korekcije za mnogo poredjenja.

| podgrupa | n | srednje % | medijana % | udeo > 0 | t | srednje % (H=5) | srednje % (H=60) |
|---|---|---|---|---|---|---|---|
| SVE | 1379 | -1.32 | -1.24 | 0.45 | -2.65 | -0.307 | -2.416 |
| 2 kupca | 904 | -1.35 | -1.40 | 0.44 | -1.82 | -0.317 | -2.738 |
| 3 kupca | 239 | -1.20 | -0.45 | 0.47 | -1.29 | 0.235 | -2.365 |
| 4+ kupaca | 236 | -1.33 | -1.26 | 0.45 | -1.44 | -0.811 | -1.234 |
| CEO/CFO/predsednik medju kupcima | 797 | -0.88 | -1.05 | 0.46 | -1.54 | -0.206 | -2.157 |
| bez CEO/CFO | 582 | -1.92 | -1.42 | 0.43 | -2.96 | -0.445 | -2.772 |
| iznos >= $500k | 576 | -2.51 | -1.39 | 0.44 | -3.07 | -0.455 | -4.719 |
| iznos < $250k | 546 | -0.55 | -0.62 | 0.47 | -0.03 | 0.224 | -0.326 |
| cena ulaza ispod proseka insidera | 427 | +0.04 | -0.80 | 0.46 | -0.97 | -0.113 | 0.656 |
| juri 0 do 15% | 698 | -0.31 | -0.47 | 0.48 | -0.18 | 0.416 | -0.497 |
| juri 15 do 30% | 61 | -4.62 | -3.66 | 0.41 | -1.22 | -3.393 | -4.752 |
| juri preko 30% | 193 | -6.91 | -7.70 | 0.32 | -3.13 | -2.345 | -15.453 |
| GME recept: 4+ kupaca i juri preko 15% | 68 | -6.71 | -7.37 | 0.35 | -1.67 | -3.514 | -10.355 |
| bez prodaja u 30 d | 1131 | -1.17 | -1.22 | 0.45 | -2.26 | -0.387 | -2.288 |
| sa prodajama u 30 d | 248 | -1.99 | -1.31 | 0.43 | -1.99 | 0.06 | -3.003 |
| cena akcije < $10 | 419 | -2.15 | -3.47 | 0.42 | -1.58 | -0.516 | -3.155 |
| cena akcije $10-50 | 744 | -1.02 | -0.77 | 0.46 | -2.63 | -0.284 | -2.827 |
| cena akcije >= $50 | 216 | -0.73 | -1.37 | 0.44 | -0.69 | 0.023 | 0.423 |

## Samo akcije koje se trguju na Liquid-u (xyz): 15 dogadjaja

| H | n | srednje % | udeo > 0 | t |
|---|---|---|---|---|
| 5 | 15 | +0.42 | 0.67 | 0.44 |
| 10 | 15 | +0.13 | 0.60 | 0.52 |
| 20 | 15 | -2.55 | 0.40 | -0.32 |
| 40 | 15 | -3.01 | 0.40 | -0.06 |
| 60 | 15 | -0.73 | 0.40 | 0.28 |

| akcija | datum prijave | kupaca | iznos $ | juri % | prinos 20 d % (minus SPY, trosak) |
|---|---|---|---|---|---|
| INTC | 2021-01-28 | 2 | 2017368 | 0.8 | 7.74 |
| ORCL | 2021-04-09 | 2 | 737939 | 13.9 | 3.87 |
| INTC | 2021-10-26 | 5 | 2488698 | -2.5 | -0.9 |
| RIVN | 2021-11-17 | 10 | 18403008 | 75.4 | -20.06 |
| DKNG | 2021-11-19 | 2 | 2233670 | -7.1 | -20.56 |
| INTC | 2022-02-24 | 2 | 745250 | 4.7 | 4.58 |
| DKNG | 2022-03-04 | 2 | 1966000 | -6.3 | -12.94 |
| GME | 2022-03-23 | 2 | 10559813 | -67.0 | 7.17 |
| INTC | 2022-05-03 | 2 | 491205 | 0.9 | 0.23 |
| MSTR | 2022-05-13 | 2 | 908844 | -90.1 | -17.91 |
| BX | 2022-05-25 | 2 | 1553299 | 3.5 | -10.13 |
| RIVN | 2022-05-31 | 2 | 2229380 | 14.5 | -9.23 |
| HIMS | 2022-06-09 | 2 | 225900 | -0.9 | 40.0 |
| BX | 2022-08-10 | 2 | 328073 | 10.4 | -6.79 |
| INTC | 2022-11-08 | 2 | 299619 | 0.6 | -3.32 |
