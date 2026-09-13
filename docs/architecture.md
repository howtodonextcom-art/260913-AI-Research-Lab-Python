# Architecture

Vietlott Quant Research Lab is a greenfield Python + Streamlit quantitative research workspace for Mega 6/45. It is **not** a prediction product and does not claim to forecast Vietlott results.

## Layout

```text
app.py
pages/01_overview.py … 08_system_health.py
src/vietlott_quant_lab/{config,data,features,ranking,research,statistics,
                        prospective,optimization,provenance,observability,ui}
data/{raw,processed,snapshots,manifests}
artifacts/{experiments,prospective,reports}
tests/  scripts/  docs/  .github/workflows/
```

## Data flow

```text
vietlott.vn (official)
  → httpx allowlist + rate limit
  → raw snapshots (immutable)
  → parser + schema guard
  → Parquet canonical + DuckDB manifests
  → Number Library 01–45 (leak-safe features)
  → Ranking 01–45 (models A/B/C)
  → Nested Top-m pools 18→7
  → Exact hypergeometric null
  → Window then model tournament
  → Pool-18 gate then compression frontier
  → Prospective hash chain
  → Streamlit reads services/artifacts only
```

## Separation of concerns

| Layer | Responsibility |
| --- | --- |
| `pages/` | UI only — call services; no research logic inline |
| `src/.../data` | Ingest, parse, canonical store, integrity (fail-closed) |
| `src/.../features` | Leak-safe Number Library at cutoff `t` from `draws < t` |
| `src/.../ranking` | Full permutation ranking 01–45 |
| `src/.../statistics` | Exact null, metrics, multiple-testing helpers |
| `src/.../research` | Protocols, tournaments, gates, experiment artifacts |
| `src/.../prospective` | Freeze/score append-only hash chain |
| `scripts/` | Long-running CLI (sync, tournaments, freeze) — not live crawl from UI |

## Stack (Round 1)

Python >= 3.12, Streamlit, httpx, BeautifulSoup4, lxml, Pydantic / pydantic-settings, DuckDB, PyArrow, Pandas, NumPy, SciPy, Plotly, pytest, Hypothesis, ruff, mypy.

LightGBM / OR-Tools are **out of scope** until classical models have a justified baseline.

## Cache and provenance

Streamlit `@st.cache_data` keys must include dataset hash + model version + protocol hash. Prospective mutable state is not cached. Experiment and prospective artifacts pin hashes for reproducibility.

## Verdict tokens

Scientific (choose one): `NO_RANKING_EDGE_FOUND` | `EXPLORATORY_SIGNAL` | `VALIDATION_SIGNAL` | `HOLDOUT_SIGNAL` | `PROSPECTIVE_SIGNAL`

Production (independent): `NOT_PRODUCTION_READY` | `PRODUCTION_READY`

Scores must not be labeled as probabilities unless calibration evidence exists.
