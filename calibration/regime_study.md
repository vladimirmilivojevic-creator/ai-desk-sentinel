# Studija stanja trzista: sta menja rezultat dnevnih pravila

Generisano 2026-10-07T16:00:48Z. Testova (pravila x stanja): 117. BH-FDR 10%: prolazi 0. Sum sam po sebi (nasumicne korpe, isti testovi): 117 testova, najveci |t| 2.94, udeo |t| > 2: 0.026.

Postupak: stanje se uzima sa kasnjenjem 1 dan, tercili iz proslosti, blokovi od 14 dana, razlika proseka gornji minus donji tercil (Welch t).

| pravilo | stanje | n gore | n dole | prosek gore %/dan | prosek dole %/dan | razlika | t | FDR |
|---|---|---|---|---|---|---|---|---|
| csm_rev14 | t5yie | 32 | 49 | -0.209 | 0.001 | -0.210 | -2.31 | ne |
| csm_mom14 | t5yie | 32 | 49 | 0.171 | -0.038 | +0.209 | 2.28 | ne |
| csm_mom7 | t5yie | 32 | 50 | 0.142 | -0.010 | +0.152 | 2.24 | ne |
| csm_mom7 | nfci | 14 | 67 | -0.017 | 0.109 | -0.126 | -2.23 | ne |
| csm_mom7 | stable_c30 | 42 | 36 | 0.124 | -0.010 | +0.134 | 2.23 | ne |
| csm_rev14 | stable_c30 | 42 | 35 | -0.196 | -0.014 | -0.182 | -2.20 | ne |
| csm_mom14 | stable_c30 | 42 | 35 | 0.159 | -0.023 | +0.182 | 2.19 | ne |
| csm_mom7 | move | 24 | 57 | 0.004 | 0.112 | -0.108 | -2.03 | ne |
| csm_mom14 | dispersion30 | 38 | 21 | 0.162 | -0.030 | +0.192 | 1.93 | ne |
| csm_rev14 | dispersion30 | 38 | 21 | -0.199 | -0.009 | -0.189 | -1.92 | ne |
| csm_rev14 | nfci | 13 | 67 | -0.000 | -0.157 | +0.157 | 1.90 | ne |
| csm_mom7 | btc_ret30 | 26 | 30 | 0.153 | 0.022 | +0.130 | 1.89 | ne |
| csm_rev14 | move | 23 | 57 | -0.043 | -0.174 | +0.132 | 1.89 | ne |
| csm_mom7 | t10y2y | 47 | 29 | 0.101 | -0.004 | +0.105 | 1.88 | ne |
| csm_mom14 | move | 23 | 57 | 0.007 | 0.136 | -0.129 | -1.84 | ne |
| csm_mom14 | nfci | 13 | 67 | -0.034 | 0.119 | -0.153 | -1.83 | ne |
| csm_rev14 | btc_ret30 | 26 | 30 | -0.239 | -0.053 | -0.186 | -1.80 | ne |
| csm_mom14 | btc_ret30 | 26 | 30 | 0.202 | 0.016 | +0.186 | 1.79 | ne |
| csm_mom7 | dispersion30 | 38 | 21 | 0.127 | -0.004 | +0.131 | 1.76 | ne |
| csm_mom7 | ethbtc_c30 | 29 | 33 | 0.019 | 0.136 | -0.117 | -1.57 | ne |
| csm_rev14 | t10y2y | 47 | 28 | -0.146 | -0.029 | -0.117 | -1.49 | ne |
| csm_mom14 | t10y2y | 47 | 28 | 0.108 | -0.005 | +0.113 | 1.43 | ne |
| csm_rev14 | btc_trend200 | 17 | 36 | -0.283 | -0.093 | -0.190 | -1.42 | ne |
| csm_mom14 | btc_trend200 | 17 | 36 | 0.245 | 0.056 | +0.189 | 1.40 | ne |
| csm_mom7 | bn_glob_ls | 22 | 47 | 0.161 | 0.051 | +0.110 | 1.40 | ne |
