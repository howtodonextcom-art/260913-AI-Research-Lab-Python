# Algorithm V2 Research Report

Evidence-first classical ranking research for Vietlott Mega 6/45.
**Scores are ranking signals only — never probabilities.**
`DESCRIPTIVE PATTERN ≠ PREDICTIVE SIGNAL`.

## Protocol

| Field | Value |
| --- | --- |
| Protocol name | `algorithm_v2_classical_v1` |
| Protocol hash | `ad821d506775c08197cc22781e74928c26b6e4a086f4e062a227ea5c5aff210b` |
| Split | chronological 50/25/25 |
| Primary endpoint | Mean K @ Top18 (null = 2.4 exact) |
| Primary inference | Newey–West HAC (Student-t legacy retained) |
| Multiplicity | Holm–Bonferroni on Validation HAC p-values |
| Family | V2 classical family: random, all_history, hot, ewf, multi_scale_shrinkage, multi_scale_v2, momentum, mean_reversion, hazard; EWF half-lives Dev-selected from [30, 60, 90, 180]; Holm–Bonferroni on Validation HAC p-values. |
| HOT lookback (registered) | 90 |
| EWF half-life (Dev-selected) | 90 |
| Practical Δ Mean K | 0.05 |
| Artifact | `artifacts/experiments/algorithm_v2_latest.json` |

## Scientific outcome

| Field | Value |
| --- | --- |
| Scientific verdict | `NO_RANKING_EDGE_FOUND` |
| Holdout status | `NO_RANKING_EDGE_FOUND` |
| Pool-18 gate | `NO_VERIFIED_18_POOL_EDGE` |
| Tournament champion (Val max Mean K) | `multi_scale_v2` |
| Champion config hash | `f51509a69b977dbbdbb6d7b3bb93f04ec83154238cd400f0743ae97b382e41db` |
| Test Mean K | 2.3760 (lift -0.0240) |
| Test HAC p | 0.6624 |
| Fragility label | `FRAGILE_SIGNAL` |
| ML status | `PRUNE_ML` |

### Keep / reject decisions

| Model family | Decision | Reason |
| --- | --- | --- |
| Random / All-history / HOT / EWF / MultiScale V1/V2 / Momentum / Reversion / Hazard | `REJECTED_NO_BENEFIT` for predictive promotion | No Validation signal surviving practical Δ + Holm; Test lift negative for Val-selected champion |
| Regularized ML / pair / regime | `PRUNE_ML` | Classical V2 showed no Validation edge meeting promotion gates |
| Compression 18→7 specialized search | Skipped | Gate `NO_VERIFIED_18_POOL_EDGE`; transparency table from frozen ranking only |

## Development (explore only)

| Model | Complexity | Mean K | Δ vs null | P4 | P5 | P6 | Mean MCP | Rank metric | CI (HAC) | Adj p | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| random | 0 | 2.4834 | 0.0834 | 0.1811 | 0.0293 | 0.0013 | 39.50 | 22.69 | [-0.005, 0.172] | 0.0328 | SIGNAL_CANDIDATE |
| all_history | 1 | 2.4234 | 0.0234 | 0.1664 | 0.0266 | 0.0027 | 39.38 | 22.91 | [-0.065, 0.112] | 0.3018 | WEAK_POSITIVE |
| hot | 2 | 2.4248 | 0.0248 | 0.1505 | 0.0226 | 0.0027 | 39.18 | 22.74 | [-0.058, 0.107] | 0.2782 | WEAK_POSITIVE |
| ewf | 3 | 2.4447 | 0.0447 | 0.1664 | 0.0373 | 0.0013 | 39.33 | 22.90 | [-0.039, 0.129] | 0.1484 | WEAK_POSITIVE |
| multi_scale_shrinkage | 5 | 2.4208 | 0.0208 | 0.1598 | 0.0306 | 0.0013 | 39.49 | 22.97 | [-0.058, 0.099] | 0.3024 | WEAK_POSITIVE |
| multi_scale_v2 | 6 | 2.3941 | -0.0059 | 0.1558 | 0.0213 | 0.0000 | 39.59 | 23.12 | [-0.088, 0.076] | 0.5557 | NO_EDGE |
| momentum | 4 | 2.3715 | -0.0285 | 0.1678 | 0.0200 | 0.0000 | 39.68 | 23.11 | [-0.098, 0.041] | 0.7893 | NO_EDGE |
| mean_reversion | 4 | 2.3848 | -0.0152 | 0.1798 | 0.0360 | 0.0027 | 39.41 | 22.95 | [-0.099, 0.069] | 0.6380 | NO_EDGE |
| hazard | 3 | 2.3329 | -0.0671 | 0.1358 | 0.0213 | 0.0013 | 39.50 | 23.29 | [-0.145, 0.011] | 0.9541 | NO_EDGE |

## Validation (select only)

| Model | Complexity | Mean K | Δ vs null | P4 | P5 | P6 | Mean MCP | Rank metric | CI (HAC) | Adj p | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| random | 0 | 2.3436 | -0.0564 | 0.1718 | 0.0333 | 0.0000 | 39.45 | 23.17 | [-0.170, 0.057] | 0.8354 | NO_EDGE |
| all_history | 1 | 2.3897 | -0.0103 | 0.1615 | 0.0410 | 0.0051 | 39.71 | 23.37 | [-0.135, 0.115] | 1.0000 | NO_EDGE |
| hot | 2 | 2.4308 | 0.0308 | 0.1795 | 0.0282 | 0.0000 | 39.60 | 22.98 | [-0.082, 0.144] | 1.0000 | WEAK_POSITIVE |
| ewf | 3 | 2.4000 | 0.0000 | 0.1795 | 0.0282 | 0.0026 | 39.77 | 23.02 | [-0.114, 0.114] | 1.0000 | NO_EDGE |
| multi_scale_shrinkage | 5 | 2.4026 | 0.0026 | 0.1487 | 0.0205 | 0.0051 | 39.57 | 22.97 | [-0.107, 0.112] | 1.0000 | WEAK_POSITIVE |
| multi_scale_v2 | 6 | 2.4718 | 0.0718 | 0.1641 | 0.0256 | 0.0026 | 39.46 | 22.87 | [-0.051, 0.195] | 1.0000 | WEAK_POSITIVE |
| momentum | 4 | 2.4462 | 0.0462 | 0.1897 | 0.0282 | 0.0000 | 39.64 | 22.71 | [-0.076, 0.168] | 1.0000 | WEAK_POSITIVE |
| mean_reversion | 4 | 2.3538 | -0.0462 | 0.1692 | 0.0282 | 0.0000 | 39.82 | 23.28 | [-0.159, 0.067] | 1.0000 | NO_EDGE |
| hazard | 3 | 2.3795 | -0.0205 | 0.1513 | 0.0256 | 0.0000 | 39.69 | 23.14 | [-0.126, 0.085] | 1.0000 | NO_EDGE |

## Test (confirm once — frozen champion `multi_scale_v2`)

| Model | Mean K | Δ vs null | P4 | P5 | P6 | Mean MCP | Mean winner rank | CI (HAC) | HAC p | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| multi_scale_v2 | 2.3760 | -0.0240 | 0.1330 | 0.0358 | 0.0026 | 39.47 | 23.10 | [-0.137, 0.088] | 0.6624 | NO_EDGE |

## Ablation (Multi-Scale V2 on Validation)

| Feature group | Baseline Mean K | Ablated Mean K | Δ | Label |
|---|---:|---:|---:|---|
| z_freq | 2.4718 | 2.4846 | -0.0128 | HARMFUL |
| momentum_short | 2.4718 | 2.4385 | 0.0333 | HELPFUL |
| momentum_medium | 2.4718 | 2.4769 | -0.0051 | NEUTRAL |
| stability | 2.4718 | 2.4333 | 0.0385 | HELPFUL |
| shrinkage | 2.4718 | 2.4308 | 0.0410 | HELPFUL |
| gap | 2.4718 | 2.4718 | 0.0000 | NEUTRAL |
| mean_reversion | 2.4718 | 2.4718 | 0.0000 | NEUTRAL |

## Fragility / red-team

Label: **`FRAGILE_SIGNAL`**

| Perturbation | Mean K | Lift | Unstable | Notes |
|---|---:|---:|---|---|
| baseline_validation | 2.4718 | 0.0718 | False | reference |
| seed_1 | 2.4718 | 0.0718 | False |  |
| seed_2 | 2.4718 | 0.0718 | False |  |
| seed_7 | 2.4718 | 0.0718 | False |  |
| seed_42 | 2.4718 | 0.0718 | False |  |
| lookback_72 | 2.4718 | 0.0718 | False |  |
| lookback_108 | 2.4718 | 0.0718 | False |  |
| era_early | 2.3692 | -0.0308 | True |  |
| era_middle | 2.3692 | -0.0308 | True |  |
| era_late | 2.6769 | 0.2769 | True |  |
| shuffled_history_control | 2.3462 | -0.0538 | True | control_expected_near_null |
| reverse_peek_harness | 6.0000 | 3.6000 | False | INVALID_AS_PREDICTIVE_EVIDENCE; harness_ok |

## Compression frontier (frozen ranking family; transparency)

Pool-18 gate did **not** pass. Table below is descriptive only — not a claim of algorithmic compression edge.

| Pool | Random Mean K | Model Mean K | Δ | P4 | P5 | P6 | MCP≤m | Tickets | Cost | Evidence |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 18 | 2.4000 | 2.4093 | 0.0093 | 0.1521 | 0.0261 | 0.0013 | 0.0013 | 18564 | 185640000 | WEAK_POSITIVE |
| 17 | 2.2667 | 2.2839 | 0.0173 | 0.1292 | 0.0183 | 0.0007 | 0.0007 | 12376 | 123760000 | WEAK_POSITIVE |
| 16 | 2.1333 | 2.1534 | 0.0201 | 0.1025 | 0.0131 | 0.0007 | 0.0007 | 8008 | 80080000 | WEAK_POSITIVE |
| 15 | 2.0000 | 2.0189 | 0.0189 | 0.0770 | 0.0091 | 0.0000 | 0.0000 | 5005 | 50050000 | WEAK_POSITIVE |
| 14 | 1.8667 | 1.8708 | 0.0041 | 0.0516 | 0.0059 | 0.0000 | 0.0000 | 3003 | 30030000 | WEAK_POSITIVE |
| 13 | 1.7333 | 1.7258 | -0.0075 | 0.0379 | 0.0039 | 0.0000 | 0.0000 | 1716 | 17160000 | NO_EDGE |
| 12 | 1.6000 | 1.5881 | -0.0119 | 0.0261 | 0.0026 | 0.0000 | 0.0000 | 924 | 9240000 | NO_EDGE |
| 11 | 1.4667 | 1.4406 | -0.0261 | 0.0163 | 0.0007 | 0.0000 | 0.0000 | 462 | 4620000 | NO_EDGE |
| 10 | 1.3333 | 1.3022 | -0.0311 | 0.0104 | 0.0007 | 0.0000 | 0.0000 | 210 | 2100000 | NO_EDGE |
| 9 | 1.2000 | 1.1671 | -0.0329 | 0.0091 | 0.0000 | 0.0000 | 0.0000 | 84 | 840000 | NO_EDGE |
| 8 | 1.0667 | 1.0320 | -0.0347 | 0.0033 | 0.0000 | 0.0000 | 0.0000 | 28 | 280000 | NO_EDGE |
| 7 | 0.9333 | 0.9001 | -0.0332 | 0.0020 | 0.0000 | 0.0000 | 0.0000 | 7 | 70000 | NO_EDGE |

## Prospective

Existing append-only freeze for target `#01563` (`hot`/90) remains the chain tip.
V2 did not promote a holdout champion, so **no history rewrite** and no replacement freeze was appended.
See `PROVENANCE_AUDIT.md`.

## Honesty reminders

- Ranking score ≠ probability
- Candidate pool ≠ guaranteed winners
- Cost reduction ≠ algorithmic edge
- `NO_RANKING_EDGE_FOUND` is a valid research result
