# Deployment

Deploy-agnostic: local venv, Docker, Cloud Run, or Streamlit Cloud can all serve the UI against **local snapshots**. Live crawl is CLI/ops, not a UI dependency.

## Local

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
streamlit run app.py
```

## Docker

Build and run from the repository root:

```bash
docker build -t vietlott-quant-lab .
docker run --rm -p 8501:8501 vietlott-quant-lab
```

If Docker Desktop is installed to a custom path on Windows (not Program Files), put its CLI on `PATH` first, e.g. `D:\DockerDesktop\resources\bin`.

Image details:

- Base: `python:3.12-slim`
- `PROJECT_ROOT=/app` so installed package code resolves `data/` / `artifacts/` under `/app`
- Non-root user `labuser` (uid 10001)
- `HEALTHCHECK` imports `vietlott_quant_lab`
- `CMD`: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
- Canonical `data/processed/*.parquet` + manifests are included for offline UI smoke

Mount `data/` and `artifacts/` as volumes in production if you need durable snapshots outside the image layers.

Smoke evidence: `artifacts/reports/DOCKER_SMOKE.md`.

## Streamlit Cloud / Cloudflare

Official vietlott.vn may return **403** from some cloud egress IPs. The app must remain usable on committed/local snapshots with System Health reporting source unreachable — never silently empty.

## CI

- `.github/workflows/ci.yml` — two jobs:
  - `test` — install, ruff, **mypy (blocking, strict)**, pytest; **no** live fetch.
  - `browser-e2e` — installs Chromium, runs `tests/browser` (real Playwright + Chromium
    against a locally-started `streamlit run app.py` server, local canonical data only);
    uploads screenshots as a build artifact.
- `.github/workflows/live-source-check.yml` — manual (`workflow_dispatch`) and optional schedule; read-only probe via `scripts/live_source_check.py`.

## Environment

See `.env.example`. Do not commit secrets. Settings live under `vietlott_quant_lab.config.settings`.
