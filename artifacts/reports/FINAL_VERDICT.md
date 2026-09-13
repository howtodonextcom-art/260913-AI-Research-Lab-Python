# Final verdict report

This lab does **not** claim to predict Vietlott results.

## Environment

| Field | Value |
| --- | --- |
| HEAD commit | (local workspace; run `git rev-parse HEAD` when repo initialized) |
| Python version | 3.12+ (dev ran on available local interpreter) |
| Data latest draw | `#01562` (2026-09-13) |
| Dataset hash | `c84b1714266aeebb4d7ea5446bf809143bf4569aa69db2b4ca154061d7fc5b05` |
| Total draws | 1562 |

## Champion configuration

| Field | Value |
| --- | --- |
| Best model | `hot` (lookback 90) — selected on Validation; Test did not confirm |
| Best windows | 90 (HOT); Multi-Scale Shrinkage uses 30/60/90/180/365/ALL |
| Best pool | No verified edge at 18 |
| Minimum defensible pool | none (`NO_VERIFIED_18_POOL_EDGE`) |

## Metrics (holdout / Test, pool 18, champion HOT)

| Field | Value |
| --- | --- |
| Mean K | 2.348 |
| Random Mean K | 2.400 |
| P4 lift | empirical below/near null (see artifact) |
| P5 lift | empirical below/near null |
| P6 lift | 0 observed jackpot containment in Test window |
| MCP distribution | mean MCP ≈ 39.6 (no compression edge) |

## Evidence phases

| Phase | Status / notes |
| --- | --- |
| Development | HOT exploratory lift possible |
| Validation | Champion = HOT (simpler than Multi-Scale when comparable) |
| Test | Lift negative vs null → not confirmed |
| Prospective | Freeze machinery available; run `python -m scripts.freeze_prospective` |

## Verdicts

| Field | Value |
| --- | --- |
| Scientific verdict | `NO_RANKING_EDGE_FOUND` |
| Production verdict | `PRODUCTION_READY` (engineering) |

Allowed scientific tokens:  
`NO_RANKING_EDGE_FOUND` | `EXPLORATORY_SIGNAL` | `VALIDATION_SIGNAL` | `HOLDOUT_SIGNAL` | `PROSPECTIVE_SIGNAL`

Allowed production tokens (independent):  
`NOT_PRODUCTION_READY` | `PRODUCTION_READY`

Artifact: `artifacts/experiments/c84b1714266a_c4e8160e291f_3bf36a2e445a.json`
