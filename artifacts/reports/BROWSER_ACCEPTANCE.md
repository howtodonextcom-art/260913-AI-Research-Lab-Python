# Browser Acceptance Report

Scope: P1 of the Browser-Verified Production Audit master prompt. All checks below were
performed against a real `streamlit run app.py` server driven by real Chromium (Playwright),
never `compile()`/import-only substitutes. Test suite: `tests/browser/test_pages_e2e.py`
(excluded from default `pytest -q` discovery; run explicitly with `pytest tests/browser`).

## Result summary

```
27 passed in ~35-40s  (tests/browser)
```

- 24 render checks: 8 pages × 3 mandatory viewports (1440×900 desktop, 768×1024 tablet,
  390×844 mobile) — page loads, no uncaught traceback text, no blank page, no permanent
  "running" spinner, no console errors beyond a known benign Streamlit-internal one (see
  below), no failed network requests, no horizontal overflow.
- 3 interaction checks: Number Lab number selector changes the feature metrics; Candidate
  Pool model selector changes the Top-m list; Candidate Pool size slider shrinks the pool
  and preserves the nested Top-m subset invariant.
- Full-page screenshots for all 24 page×viewport combinations saved under
  `artifacts/reports/browser_screenshots/`.

## Real defect found and fixed during this pass

The first suite run **hung indefinitely** on every single page. Root cause: the test
harness (`tests/browser/conftest.py`) launched `streamlit run app.py` with
`stdout=subprocess.PIPE` but never drained the pipe. Once Streamlit's log output filled the
OS pipe buffer, the server process blocked on writing to stdout and stopped answering HTTP
requests — a classic subprocess deadlock, not an app bug. Fixed by redirecting the
subprocess's stdout/stderr to a log file instead of an undrained pipe. This is exactly the
category of failure a compile-only test (the previous `test_streamlit_smoke.py`) could never
have caught, since it never starts a real server process.

## Known benign noise (allowlisted, not a defect)

On a direct deep-link into any sub-page (e.g. opening `/candidate_pool` directly rather than
navigating there from `/`), Streamlit's own frontend briefly polls `_stcore/health` and
`_stcore/host-config` relative to the *current* path (e.g. `/candidate_pool/_stcore/health`),
which 404s. The page still renders and functions correctly regardless — this is a
Streamlit-framework quirk, not an app defect, and it reproduces identically on every page.
The test suite allowlists exactly these two suffixes (`_BENIGN_404_SUFFIXES` in
`test_pages_e2e.py`) so it can't mask a real failed request or console error elsewhere.

## Per-page acceptance (master prompt §12–§20)

| Page | Renders (3 viewports) | Notes |
| --- | --- | --- |
| Overview | ✅ | Scientific verdict, dataset count/hash, evidence level all visible without reading JSON. |
| Data Library | ✅ | Filters render; dataframe of draws with official-source link column shown. |
| Number Lab | ✅ | Changing the number selector changes gap/gap_z/momentum/shrinkage metrics live (verified: number 01→23 changed `gap` 6→4) — no stale-cache issue found. Raw feature JSON now behind "Advanced / Debug" (was primary content before this pass). |
| Candidate Pool | ✅ | Changing model or pool size updates Mean K / Random Mean K / Lift / MCP and the Top-m list; nested Top-m subset invariant verified programmatically (pool 18 → smaller pool is always a subset). P4/P5/P6 now a formatted table (was a raw dict before this pass). |
| A/B Tournament | ✅ | Development/Validation/Test Mean K now a single comparison table per model (was three separate raw `st.json` blocks before this pass); champion, scientific verdict, holdout status, protocol/dataset hash all visible as metrics, not buried in JSON. |
| Compression Frontier | ✅ | No compression artifact exists on disk yet, so the page correctly falls back to live-tail computation (documented, visible fallback banner) rather than crashing or silently hiding the gap — exercises the 3-tier fallback (artifact → live tail → static skeleton) described in the page's own code. |
| Prospective | ✅ | Hash-chain status, frozen/pending/scored counts all visible; explicitly read-only, no long-lived cache (per its own caption). |
| System Health | ✅ | Every health line (source, parser, integrity, freshness, DuckDB, artifacts, prospective chain, app version) is independently computed and could plausibly go red — not a hardcoded-green panel (confirmed by code: each check in `build_system_health` is wrapped in its own try/except). |

## Degraded-state check (master prompt §58)

Ran the app a second time with `PROJECT_ROOT` pointed at an empty directory (no dataset, no
artifacts, no prospective chain) — simulating the "dataset absent" / "artifact absent"
failure-injection scenarios without touching real data. Result across all 8 pages: **zero
tracebacks**, every page rendered a friendly, actionable message (e.g. "Chưa có dataset
canonical. Chạy `python -m scripts.sync_official` rồi mở lại trang."). Notably, the Overview
page's own **Production Verdict badge automatically flips to `NOT_PRODUCTION_READY`** when
the dataset is missing — this is a real, code-driven check, not a cosmetic label. Screenshots
saved under `artifacts/reports/browser_screenshots/degraded/`.

## Not covered in this pass (documented, not silently skipped)

- Live-source failure injection against a mocked/broken vietlott.vn response (schema drift,
  truncated page) — covered at the unit level by `tests/test_parser.py`/`test_integrity.py`
  already, but not re-verified through the browser in this pass.
- Docker build/run — **not performed**. Docker is not installed in this local audit
  environment, so the planned manual build+run+browser smoke check could not run here (see
  `BASELINE_AUDIT.md`). Dockerfile correctness remains unverified; do not treat Docker
  deployment as validated until this is actually run, in CI or on a machine with Docker.
- CI execution of this suite happens in P3 (this file only documents the local run).
