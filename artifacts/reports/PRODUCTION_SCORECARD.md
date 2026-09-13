# Production Scorecard

Independent 0–10 scores after P0–P10 audit + Algorithm V2 research.
A feature earns 10/10 only when the full SOURCE→…→DOCUMENTED LIMIT chain exists (§60).
Hard caps from §61 are applied.

## Scores

| Criterion | Score | Notes |
| --- | ---: | --- |
| Python architecture | 8.5 | Clear packages; V2 models registered in engine; no framework sprawl |
| Data ingestion | 8.0 | Official vietlott.vn allowlist, HTTPS, retries; raw body archive still thin |
| Data integrity | 8.5 | Schema/integrity tests; manifest hash; red-team injection tests present |
| Feature engineering | 8.0 | Multi-scale, EWF, momentum/reversion/hazard; anti-leak by walk-forward |
| Ranking engine | 8.5 | Round-1 + V2 dispatch; controls (random / shuffle / reverse-peek) |
| Statistical methodology | 8.5 | Exact Hypergeometric null; HAC + block bootstrap + Holm; effect-size gate |
| Temporal research protocol | 9.0 | 50/25/25; Dev→Val→Test; no Test tuning in V2 CLI |
| Multiplicity control | 8.5 | Holm on V2 Validation family; window Holm retained in Round-1 |
| Prospective governance | 8.0 | Append-only JSONL + hash chain; freeze for `#01563` pending |
| Provenance | 8.0 | Artifacts resolve; dual protocol domains documented; no lockfile |
| Streamlit UX | 8.0 | Metrics-first; raw JSON behind Advanced/Debug (P3) |
| Browser correctness | 9.0 | Real Playwright Chromium E2E (`tests/browser`) |
| Responsive behavior | 7.5 | Smoke across pages; not a full responsive design audit |
| Accessibility | 6.5 | Streamlit defaults; no dedicated a11y suite |
| Test quality | 8.5 | Unit + property + research + browser; V2/inference added |
| CI | 8.5 | Ruff + blocking mypy + pytest + browser-e2e job |
| Security | 7.5 | URL allowlist, size caps; no auth surface (local research app) |
| Observability | 7.5 | Structured log events; not full metrics/tracing |
| Performance | 7.0 | Research in CLI/artifacts; UI mostly consumes artifacts |
| Docker/deployment | 4.0 | Dockerfile exists but **never built/run here**; hard gap |
| Documentation | 8.5 | Protocol/docs + five audit reports |
| Scientific honesty | 9.5 | Explicit `NO_RANKING_EDGE_FOUND`; score≠probability; ML pruned |

## Caps applied

| Cap | Trigger | Effect |
| --- | --- | --- |
| Docker/runtime unverified while Docker claimed | Dockerfile + `docs/deployment.md` | Production verdict cannot be `PRODUCTION_READY` |
| No real-browser E2E | **Cleared** (P3) | Prior 8.9 engineering cap no longer binds |

## Aggregate reading

Engineering is strong for a research Streamlit lab, but **Docker unverified** keeps the
production gate closed. Scientific methodology improved (P4–P7) without manufacturing an edge.

**Production verdict: `NOT_PRODUCTION_READY`**
