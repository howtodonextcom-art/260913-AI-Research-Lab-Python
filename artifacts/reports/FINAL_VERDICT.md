# Final verdict report

Updated after completing P0–P10 of the Browser-Verified Production Audit & Algorithm
Upgrade, plus Docker smoke closeout. Every field below is tied to verified local evidence
(code, tests, artifacts, or explicit inability to verify).

## Environment

| Field | Value |
| --- | --- |
| Starting SHA (audit baseline) | `ac7a597a756b27ddb04a06fd9388324bd1108689` |
| Ending SHA (pre-Docker closeout) | `08afbd692c17b7be800f97874ef026a1a7b6f9d9` |
| Ending SHA (this Docker closeout) | _recorded in follow-up commit after push tip is known_ |
| Branch | `main` |
| Python | 3.14.4 local (CI / Docker pin 3.12) |
| Data latest draw | `#01562` (2026-09-13) |
| Dataset record count | 1562 |
| Dataset hash | `c84b1714266aeebb4d7ea5446bf809143bf4569aa69db2b4ca154061d7fc5b05` |

## Quality gates

| Gate | Result |
| --- | --- |
| Ruff | All checks passed (prior audit tip) |
| Mypy `--strict` | Success (prior audit tip) |
| Pytest (default, excl. browser) | Prior **78 passed** + new `test_settings_project_root` |
| Browser E2E | 27/27 green in P3 (`tests/browser`); not re-run this phase |
| Docker smoke | **PASS** — see `artifacts/reports/DOCKER_SMOKE.md` |

## Champion configuration

| Field | Value |
| --- | --- |
| Round-1 Val selection (historical) | `hot` lookback 90 — Test did not confirm |
| V2 Val selection (max Mean K) | `multi_scale_v2` — **not promoted** |
| Best windows | HOT 90; EWF half-life Dev-selected 90; Multi-Scale 30/60/90/180/365/ALL |
| Best pool | No verified edge at 18 |
| Minimum defensible pool | none (`NO_VERIFIED_18_POOL_EDGE`) |
| Fragility | `FRAGILE_SIGNAL` on Val-selected V2 config |
| ML | `PRUNE_ML` — classical V2 lacked Validation promotion edge |

## Metrics (Test holdout, pool 18)

### Round-1 champion HOT/90 (prior artifact)

| Field | Value |
| --- | --- |
| Mean K | 2.348 |
| Null Mean K | 2.400 |
| Lift | negative |

### Algorithm V2 Val-selected `multi_scale_v2` (confirm-once Test)

| Field | Value |
| --- | --- |
| Mean K | 2.376 |
| Null Mean K | 2.400 |
| Lift | −0.024 |
| HAC one-sided p | 0.662 |
| Mean MCP | (see `algorithm_v2_latest.json`) |
| Mean winner rank | (see artifact) |

Full Dev / Validation / Test tables: `artifacts/reports/ALGORITHM_V2_RESEARCH.md`.

## Evidence phases

| Phase | Status |
| --- | --- |
| Development | Some weak positive Mean K (including finite-sample random lift); none promoted |
| Validation | `multi_scale_v2` highest Mean K (lift ≈ +0.072) but HAC p ≈ 0.13; Holm-adjusted p fails α=0.05 gate |
| Test | Lift negative vs null → not confirmed |
| Prospective | Freeze `#01563` pending (`hot`/90); chain verified; no rewrite |

## Verdicts

| Field | Value |
| --- | --- |
| Scientific verdict | `NO_RANKING_EDGE_FOUND` |
| Production verdict | `PRODUCTION_READY` |

Allowed scientific tokens:  
`NO_RANKING_EDGE_FOUND` | `EXPLORATORY_SIGNAL` | `VALIDATION_SIGNAL` | `HOLDOUT_SIGNAL` | `PROSPECTIVE_SIGNAL`

Allowed production tokens (independent):  
`NOT_PRODUCTION_READY` | `PRODUCTION_READY`

## Baseline vs new algorithms

| Family | Status |
| --- | --- |
| Random, HOT, Multi-Scale V1 | Round-1 baselines retained |
| All-history, EWF, Multi-Scale V2, Momentum, Mean-reversion, Hazard | Implemented + tournamented; rejected for promotion |
| Pair / regime / regularized ML | Skipped (`PRUNE_ML`) |
| Compression 18→7 | Transparency table only; no verified pool-18 edge |

## Unresolved risks

| Severity | Risk |
| --- | --- |
| MEDIUM | No dependency lockfile |
| MEDIUM | `data/raw/` lacks full HTTP body archive |
| LOW | Local Python 3.14 vs CI/Docker 3.12 drift |

## Artifacts

- `artifacts/reports/BASELINE_AUDIT.md`
- `artifacts/reports/BROWSER_ACCEPTANCE.md`
- `artifacts/reports/ALGORITHM_V2_RESEARCH.md`
- `artifacts/reports/PROVENANCE_AUDIT.md`
- `artifacts/reports/PRODUCTION_SCORECARD.md`
- `artifacts/reports/DOCKER_SMOKE.md`
- `artifacts/reports/FINAL_VERDICT.md`
- `artifacts/experiments/algorithm_v2_latest.json`
- `artifacts/prospective/freezes.jsonl`

## Honesty

This lab does **not** claim to predict Vietlott results.
`RANKING SCORE ≠ PROBABILITY`. `NO_RANKING_EDGE_FOUND` is a valid outcome.
