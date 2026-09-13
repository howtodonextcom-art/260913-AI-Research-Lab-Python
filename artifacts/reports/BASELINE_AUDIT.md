# Baseline Audit

Scope: P0 of the Browser-Verified Production Audit & Algorithm Upgrade master prompt
(`prompts/MASTER PROMPT — Browser-Verified Production Audit & Algorithm Upgrade for Vietlott Quant Research Lab.md`).
This report records reality **before** any fixes in this pass, independently verified by
running the code and inspecting source — not copied from README or the prior
`FINAL_VERDICT.md`.

## Environment

| Field | Value |
| --- | --- |
| HEAD SHA (at audit start) | `ac7a597a756b27ddb04a06fd9388324bd1108689` |
| Branch | `main` (up to date with `origin/main`) |
| `git status` | clean except untracked `prompts/` (this run's master-prompt file) |
| Python (local) | 3.14.4 (only interpreter available on this machine; CI pins 3.12 — see Gaps) |
| Install method | fresh `.venv`, `pip install -e ".[dev]"` |
| Key dependency versions | streamlit 1.63.0, pandas 3.0.5, numpy 2.5.3, duckdb 1.5.5, pyarrow 25.0.1, scipy 1.18.1, plotly 7.0.0, mypy 2.3.1, ruff 0.16.7, pytest 9.1.1 (full freeze retained locally) |

## Dataset

| Field | Value |
| --- | --- |
| First draw | `#00001` (2016-07-20) |
| Latest draw | `#01562` (2026-09-13) |
| Record count | 1562 |
| Dataset SHA-256 | `c84b1714266aeebb4d7ea5446bf809143bf4569aa69db2b4ca154061d7fc5b05` |
| Manifest validation status | `PASS` (`data/manifests/manifest_mega645.json`) |

## Existing experiment / prospective artifacts

| Field | Value |
| --- | --- |
| Experiment artifact | `artifacts/experiments/c84b1714266a_c4e8160e291f_3bf36a2e445a.json` |
| Champion | HOT, lookback 90 (selected on Validation; Test did not confirm) |
| Pool-18 gate | `NO_VERIFIED_18_POOL_EDGE` |
| Prospective chain | `artifacts/prospective/freezes.jsonl` — 1 record, genesis, target draw `#01563` (next undrawn), status **pending** (no `actual_numbers`/score yet) |

## Independently verified verdicts (before this pass)

| Axis | Verdict | Verified how |
| --- | --- | --- |
| Scientific | `NO_RANKING_EDGE_FOUND` | Re-derived from the experiment artifact's own `scientific_verdict`/`pool_gate.status` fields, not just the prose in `FINAL_VERDICT.md` |
| Production (as claimed) | `PRODUCTION_READY` | **Not accepted as-is** — see Gaps below; this claim is contradicted by §61 hard caps (no real browser E2E existed before this pass, mypy was non-blocking) |

## Static quality — before fixes

```
ruff check src tests scripts app.py pages   → All checks passed
mypy src/vietlott_quant_lab                 → 6 errors, 3 files (see below)
pytest -q                                   → 64 passed
```

Mypy errors found (all fixed in this pass — see `PROVENANCE_AUDIT`-adjacent notes below,
full detail in the diff):
1. `ui/labels.py:111` — `VALIDATION` constant defined twice with the same value (harmless at
   runtime, since the second definition simply won — but a real `no-redef` violation and a
   latent footgun if the two were ever meant to diverge). Fixed by removing the duplicate.
2. `data/storage.py` — missing type stubs for `pandas`/`pyarrow`. Added `pandas-stubs` to dev
   deps and `pyarrow.*` to the mypy `ignore_missing_imports` override (pyarrow does not ship
   a `py.typed` marker upstream).
3. `data/storage.py:60-65` (surfaced only *after* adding `pandas-stubs`) — `itertuples()` rows
   are typed as a wide union by pandas-stubs; `int(row.n1)` etc. didn't type-check. Fixed with
   explicit `cast(int, ...)` at the point where the schema is known to be numeric.
4. `data/sync.py:182` — `require_cont = mode == "full" or (existing and ... if existing else False)`
   type-checked as `list[DrawRecord] | bool` instead of `bool`, because `existing and X` types
   as the falsy branch's own type. Not a runtime bug (semantics were already correct — the
   outer ternary's `if existing` guard means the falsy branch of `and` is never taken), but
   fragile and rightly flagged by strict mode. Simplified to
   `mode == "full" or (bool(existing) and existing[0].draw_id == "00001")`.

After fixes: `ruff` clean, `mypy --strict` clean (0 errors), `pytest -q` 64 passed — same
count as before, confirming the mypy fixes were typing-only with no behavior change.

## Gaps found (drove the fix list for P2/P3)

1. **CI mypy gate was cosmetic.** `.github/workflows/ci.yml` ran `mypy` with
   `continue-on-error: true` and a comment claiming this was temporary "P0–P12 scaffolding"
   tolerance. The repo could claim `PRODUCTION_READY` while silently permitting type-checking
   failure — directly the failure mode master-prompt §6/§61 warns against. **Fixed in P3.**
2. **No real browser test existed.** `tests/test_streamlit_smoke.py` only calls `compile()` on
   each page's source and calls loader functions directly in-process — no Streamlit server, no
   DOM, no browser. This is exactly the "compile-test-as-browser-test" pattern master-prompt
   §10/§64 calls out as invalid. **Addressed in P1/P3** (see `BROWSER_ACCEPTANCE.md`).
3. **Raw snapshot is a marker, not the actual fetched page.** `data/raw/*.bin` contains the
   literal text `sync:full:fetched=1562` (22 bytes) — a lightweight audit marker written once
   per sync call, not the actual HTML/AjaxPro response bytes returned by vietlott.vn during
   the crawl. `docs/data-source.md` calls `data/raw/` "immutable raw snapshots" without
   clarifying this, which reads as stronger provenance than what's actually implemented: the
   real page content fetched during `crawl_full`/`crawl_incremental` (in `data/client.py`) is
   discarded after parsing and never persisted. **This is a real audit-trail gap, not a
   cosmetic one** — a corrupted parse could not be independently re-verified against the raw
   page it came from. Given the fix is a data-ingestion pipeline change (persisting real HTTP
   response bodies in `client.py`/`sync.py`), it is **out of the bounded P0–P3 scope** for this
   pass; the doc has been corrected to describe reality accurately rather than overstate it,
   and this is flagged as a **HIGH-priority backlog item** for a future data-engineering pass.
4. **Two independent `protocol_hash` domains** exist (`research/protocol.py`'s
   `ResearchProtocol.protocol_hash()` vs. `prospective/freeze.py`'s own `DEFAULT_PROTOCOL`
   hash) and will never match each other by design — undocumented before this pass. **Fixed
   in P2** (documentation clarification, no hash-chain changes).
5. **No dependency lock file** (`uv.lock`/`poetry.lock`/`requirements*.txt` all absent) —
   reproducible-build risk. Not fixed in this pass (would require choosing/adopting a lock
   tool, which is a separate decision from this audit's scope); flagged as a backlog item.
6. **Raw JSON/dict blocks shown as primary UI content** (not behind an "Advanced/Debug"
   affordance) in 4 of 8 pages — a scientific-honesty/UX gap per §50–52. **Fixed in P2.**
7. **Docker image never built or smoke-tested**, in CI or otherwise, before this pass — the
   Dockerfile's correctness remains **unverified**. Docker is not installed in this local
   audit environment (`docker --version` → command not found), so the planned manual
   build+run+browser smoke check could not be performed here either. This is an honest gap,
   not a pass: `PRODUCTION_READY` cannot rely on any claim about Docker correctness until it
   is actually built and run somewhere. Flagged as an open item for `FINAL_VERDICT.md` and a
   required follow-up (in CI or on a machine with Docker) before Docker deployment is trusted.

## Engineering vs. scientific verdict (independent axes, per master-prompt §5)

These are **not finalized** until P1–P3 fixes and browser acceptance are complete — see
`FINAL_VERDICT.md` (updated at the end of this pass) for the final calls. As of this baseline
snapshot, before any fixes: Production readiness could not be honestly claimed (mypy gate
cosmetic, zero real browser coverage) even though unit-level engineering quality was already
solid (clean ruff, 64/64 tests green, well-layered architecture, leak-guarded features,
hash-chained prospective ledger). Scientific verdict is unaffected by any of this pass's
engineering work: `NO_RANKING_EDGE_FOUND` stands, independently re-derived from the existing
experiment artifact.
