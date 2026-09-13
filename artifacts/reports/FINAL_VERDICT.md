# Final verdict report

This lab does **not** claim to predict Vietlott results.

> Updated by the P0–P3 Browser-Verified Production Audit pass (see `BASELINE_AUDIT.md` and
> `BROWSER_ACCEPTANCE.md`). This pass touched engineering/UX/CI/docs only — **no algorithm
> research was performed** (P4–P10 of that audit are explicitly deferred to a follow-up
> session), so the scientific verdict and champion configuration below are unchanged from
> before this pass and are re-stated here only for continuity, not re-derived.

## Environment

| Field | Value |
| --- | --- |
| HEAD commit at pass start | `ac7a597a756b27ddb04a06fd9388324bd1108689` (working tree has
  uncommitted changes from this pass — not pushed/committed per operator instruction; see
  `git status`/`git diff` for the exact diff until a commit is made) |
| Python version | 3.14.4 (local audit env); CI pins 3.12 |
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
| Scientific verdict | `NO_RANKING_EDGE_FOUND` (unchanged — no algorithm work this pass) |
| Production verdict | `NOT_PRODUCTION_READY` |

Allowed scientific tokens:  
`NO_RANKING_EDGE_FOUND` | `EXPLORATORY_SIGNAL` | `VALIDATION_SIGNAL` | `HOLDOUT_SIGNAL` | `PROSPECTIVE_SIGNAL`

Allowed production tokens (independent):  
`NOT_PRODUCTION_READY` | `PRODUCTION_READY`

Artifact: `artifacts/experiments/c84b1714266a_c4e8160e291f_3bf36a2e445a.json`

### Why production verdict changed from the prior report's `PRODUCTION_READY`

The prior report's `PRODUCTION_READY` claim was **not independently verifiable** before this
pass and did not survive the audit — see `BASELINE_AUDIT.md` for detail. This pass fixed the
following and each is now independently confirmed:

- ✅ Real browser E2E now exists and passes (27/27, `tests/browser`, real Chromium) — was
  entirely absent before (only `compile()`/import-only checks).
- ✅ `mypy --strict` is now genuinely blocking in CI (`continue-on-error` removed) — 6 real
  type errors were found and fixed first, so the gate turns on clean rather than red.
- ✅ Raw JSON/dict UX shown as primary content (pages 03/04/05/08) moved behind
  "Advanced / Debug", or reformatted as proper metrics/tables — was a scientific-honesty/UX
  gap per §50–52.
- ✅ `protocol_hash` dual-domain ambiguity documented (tournament vs. prospective-freeze
  protocols are, by design, different values) — was previously undocumented and read as a
  provenance break.
- ✅ Degraded states (missing dataset/artifact) verified in a real browser: zero tracebacks
  across all 8 pages; Overview's Production Verdict badge itself correctly flips to
  `NOT_PRODUCTION_READY` when the dataset is absent.

One item remains **unresolved and is the reason this report still says
`NOT_PRODUCTION_READY`**:

- ❌ **Docker is never built or run, in CI or in this audit environment** (Docker is not
  installed here). The repo ships a Dockerfile and documents Docker as a deployment path
  (`docs/deployment.md`), so per this audit's own production-readiness definition
  ("Docker/runtime verified if Docker claimed"), an unverified Dockerfile is a blocking gap,
  not a cosmetic one — it has never been proven to build or serve the app at all.

Two additional, non-blocking items are tracked as backlog (do not block the verdict above,
but should not be forgotten):

- The `data/raw/` "snapshot" is a lightweight sync marker, not the actual fetched HTML/AjaxPro
  bytes — a real audit-trail gap for re-verifying historical parses (see `BASELINE_AUDIT.md`).
- No dependency lock file (`uv.lock`/`poetry.lock`/`requirements*.txt`) exists — reproducible
  installs are not pinned.

**Recommended next step to close out `PRODUCTION_READY`:** build and run the Docker image
(`docker build . && docker run -p 8501:8501 ...`), repeat the browser smoke journey against
the containerized app, and wire that check into CI. Everything else in this checklist is
already green.
