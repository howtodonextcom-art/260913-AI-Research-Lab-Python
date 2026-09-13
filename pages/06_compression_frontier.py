"""Compression Frontier — pool vs containment/cost; prefer artifact, else live subset."""

from __future__ import annotations

import streamlit as st

from vietlott_quant_lab.ranking.engine import ROUND1_MODELS
from vietlott_quant_lab.statistics.bao import cost, tickets
from vietlott_quant_lab.statistics.hypergeometric import expected_k
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.charts import (
    compression_cost_figure,
    compression_frontier_figure,
    cost_vs_containment_figure,
)
from vietlott_quant_lab.ui.loaders import (
    find_compression_artifact,
    latest_tournament_artifact,
    load_dataset_bundle,
)

st.set_page_config(page_title=f"{labels.PAGE_COMPRESSION} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_COMPRESSION)
st.caption("Nested 18→7 · containment (Mean K) · full-bao cost.")

bundle = load_dataset_bundle()
compression = find_compression_artifact()
artifact = latest_tournament_artifact()

rows: list[dict] = []
source_note = ""

if compression is not None:
    raw = compression.get("rows")
    if raw is None and isinstance(compression.get("extra"), dict):
        raw = compression["extra"].get("rows")
    if isinstance(raw, list):
        rows = [r for r in raw if isinstance(r, dict)]
        source_note = "artifact"
        st.success("Đang đọc compression artifact.")

if not rows and bundle.draws:
    default_model = ROUND1_MODELS[0]
    if artifact and artifact.get("model") in ROUND1_MODELS:
        default_model = str(artifact["model"])
    model_id = st.selectbox(
        labels.MODEL_SELECTOR,
        options=list(ROUND1_MODELS),
        index=list(ROUND1_MODELS).index(default_model),
    )
    st.warning(labels.MISSING_COMPRESSION_ARTIFACT)
    st.info("Tính frontier trên đuôi lịch sử (UI) — không thay artifact CLI đầy đủ.")
    max_draws = st.slider(
        "Max draws (tail)",
        min_value=60,
        max_value=min(800, len(bundle.draws)),
        value=min(240, len(bundle.draws)),
    )
    subset = bundle.draws[-int(max_draws) :]
    try:
        from vietlott_quant_lab.research.compression import compression_frontier

        with st.spinner("Computing compression frontier…"):
            frontier = compression_frontier(
                subset,
                model_id=str(model_id),
                lookback=90,
                seed=0,
                min_history=30,
            )
        rows = [r.summary() for r in frontier.rows]
        source_note = f"live_tail n={len(subset)} nested_ok={frontier.nested_ok}"
    except Exception as exc:  # noqa: BLE001
        st.error(f"Không tính được frontier: {exc}")

if not rows:
    st.warning(labels.MISSING_COMPRESSION_ARTIFACT)
    st.info("Hiển thị khung null/cost (không có model Mean K empirical).")
    rows = [
        {
            "pool_size": m,
            "null_mean_k": expected_k(m),
            "model_mean_k": expected_k(m),
            "tickets": tickets(m),
            "cost_vnd": cost(m),
            "evidence_status": "NO_ARTIFACT",
        }
        for m in range(18, 6, -1)
    ]
    source_note = "null_skeleton"

st.caption(f"source=`{source_note}`")
st.subheader(labels.FRONTIER_CHART)
st.plotly_chart(compression_frontier_figure(rows), use_container_width=True)
st.plotly_chart(compression_cost_figure(rows), use_container_width=True)
st.plotly_chart(cost_vs_containment_figure(rows), use_container_width=True)
st.dataframe(rows, use_container_width=True, hide_index=True)
