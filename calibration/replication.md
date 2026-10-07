# Ponavljanje unapred zapisanih hipoteza (config/preregistered_hypotheses.json)

## HYP-LS-1 na uzorku 2022-09-01..2024-11-30

Neto Sharpe 0.4 (uz stvarni taker 0.724), t 0.56, godisnji prinos 8.35%, najveci pad -18.82%, dana 718, aktivnih instrumenata 44.
Po godinama: {2022: 6.77, 2023: -0.61, 2024: 1.04}
Dopuna (nije kriterijum): uz prebijanje pozicija neto Sharpe 0.754, t 1.06 (uz stvarni taker 0.879), dnevni promet 0.11 kapitala.
Posle kontrola (nizak vol, momentum 30 d i 90 d): {'feature': 'top_acc_ls', 'sign': -1, 'H': 7, 'alpha_ann_pct': 0.67, 't_alpha': 0.05, 'r2': 0.243, 'beta': {'nizak_vol': 0.021, 'mom30': 0.229, 'mom90': 0.186}, 'days': 718}
Kriterijumi (zapisani unapred): {'net_sharpe': False, 'net_t': False, 'alpha_positive': True}. **Ishod: NIJE PROSLO.**
