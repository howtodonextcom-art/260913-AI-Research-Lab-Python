# Official Vietlott Mega 6/45 data source

Primary source is **vietlott.vn** (public HTML / AjaxPro). This lab does not
treat GitHub/Kaggle mirrors as production truth.

## Endpoints

| Role | Method | Path |
|------|--------|------|
| History landing | GET | `/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645` |
| Draw detail | GET | `/vi/trung-thuong/ket-qua-trung-thuong/645?id={draw_id}&nocatche=1` |
| History pages | POST | `/ajaxpro/Vietlott.PlugIn.WebParts.Game645CompareWebPart,Vietlott.PlugIn.WebParts.ashx` |

AjaxPro POST requires header `X-AjaxPro-Method: ServerSideDrawResult` and a JSON
body with `ORenderInfo`, `Key` (scraped from the landing page), and `PageIndex`.

Observed page size: **8** rows. History starts at draw **`#00001`** (2016-07-20).

HTTP client allowlists host `vietlott.vn` only (HTTPS), uses User-Agent
`vietlott-quant-lab/0.1 (+research)`, timeouts, retry/backoff, and a max
response size. Inter-page delay defaults to ~400ms.

## EOF / crawl-anchor rule (critical)

Never treat an empty or unparsable history page as end-of-history by itself.

- **Full crawl:** only accept empty/short trailing pages after positively
  observing draw `#00001` in parsed row IDs.
- **Incremental crawl:** only accept empty/short trailing pages after positively
  observing the previously synced `latestId` (or any id ≤ that anchor).
- Empty page **before** the anchor → `SOURCE_SCHEMA_CHANGED` (fail closed).
- Missing `doso_output_nd` / `<tbody>` wrapper → `SOURCE_SCHEMA_CHANGED`.
- Exhausting the page budget without reaching the anchor → fetch error, not a
  truncated “success” dataset.

The old Python donor’s `if not fresh: break` EOF pattern is **forbidden**.

## Parsers

1. **Primary:** regex for history rows, `bong_tron` balls, detail header/block.
2. **Fallback:** BeautifulSoup table columns (date / kỳ / bộ số).
3. Both fail (or wrapper missing before anchor) → `SOURCE_SCHEMA_CHANGED`.

## Local artifacts

- Immutable raw snapshots: `data/raw/` (content hash + timestamp; never overwrite).
- Canonical draws: `data/processed/draws_mega645.parquet`.
- Manifest + DuckDB sync state: `data/manifests/`.
- Merge conflicts: reconcile JSON under `data/snapshots/` (canonical not overwritten).

## Sync CLI

```bash
pip install -e ".[dev]"
python -m scripts.sync_official
python -m scripts.sync_official --force
python -m scripts.sync_official --delay 500
```

CI must not hit live Vietlott; use HTML fixtures under `tests/fixtures/`.
Some cloud environments (e.g. Streamlit Cloud) may see Cloudflare 403 — UI
reads local snapshots only and must surface source health, never silent empty.
