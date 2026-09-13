"""Candidate Pool — selector 18→7; Mean K vs null; P4/P5/P6; MCP; lift; evidence."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from vietlott_quant_lab.config.constants import POOL_SIZES
from vietlott_quant_lab.ranking.engine import ROUND1_MODELS
from vietlott_quant_lab.statistics.bao import cost, tickets
from vietlott_quant_lab.statistics.bao import p6 as bao_p6
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.cache import cached_null_tails, cached_ranking
from vietlott_quant_lab.ui.loaders import (
    find_compression_artifact,
    latest_tournament_artifact,
    load_dataset_bundle,
)

st.set_page_config(page_title=f"{labels.PAGE_CANDIDATE_POOL} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_CANDIDATE_POOL)
st.caption("Nested Top-m · null = exact hypergeometric.")

bundle = load_dataset_bundle()
if not bundle.draws:
    st.info(labels.MISSING_DATASET)
    st.stop()

pool_size = st.select_slider(labels.POOL_SIZE, options=list(reversed(POOL_SIZES)), value=18)
model_id = st.selectbox(labels.MODEL_SELECTOR, options=list(ROUND1_MODELS), index=0)

ranking = cached_ranking(
    bundle.draws,
    dataset_hash=bundle.dataset_hash,
    model_id=str(model_id),
    model_version="round1",
    lookback=90,
)
pool = ranking.top_m(int(pool_size))
nulls = cached_null_tails(int(pool_size))

artifact = latest_tournament_artifact()
compression = find_compression_artifact()
evidence = labels.DEFAULT_SCIENTIFIC_VERDICT
model_mean_k = None
mean_mcp = None
emp_p4 = emp_p5 = emp_p6 = None

if compression:
    rows = compression.get("rows")
    if rows is None and isinstance(compression.get("extra"), dict):
        rows = compression["extra"].get("rows")
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and int(r.get("pool_size", -1)) == int(pool_size):
                model_mean_k = r.get("model_mean_k")
                mean_mcp = r.get("mean_mcp")
                emp_p4 = r.get("p_ge_4")
                emp_p5 = r.get("p_ge_5")
                emp_p6 = r.get("p_eq_6")
                evidence = str(r.get("evidence_status") or evidence)
                break

if model_mean_k is None and artifact:
    evidence = str(artifact.get("scientific_verdict") or evidence)
    for key in ("validation_results", "test_results", "test", "validation"):
        block = artifact.get(key) or {}
        if isinstance(block, dict) and "mean_k" in block:
            model_mean_k = block.get("mean_k")
            mean_mcp = block.get("mean_mcp", mean_mcp)
            break
    if model_mean_k is None:
        st.warning(labels.MISSING_ARTIFACT)
elif model_mean_k is None:
    st.warning(labels.MISSING_ARTIFACT)

lift = None
if isinstance(model_mean_k, (int, float)):
    lift = float(model_mean_k) - nulls.mean_k

c1, c2, c3, c4 = st.columns(4)
c1.metric(labels.MEAN_K, f"{model_mean_k:.4f}" if isinstance(model_mean_k, (int, float)) else "—")
c2.metric(labels.RANDOM_MEAN_K, f"{nulls.mean_k:.4f}")
c3.metric(labels.LIFT, f"{lift:+.4f}" if lift is not None else "—")
c4.metric(labels.MCP, f"{mean_mcp:.2f}" if isinstance(mean_mcp, (int, float)) else "—")

tail_rows = [
    {
        "Metric": labels.P4,
        "Null (exact)": f"{nulls.p_ge_4:.6f}",
        "Empirical": f"{emp_p4:.6f}" if isinstance(emp_p4, (int, float)) else "—",
    },
    {
        "Metric": labels.P5,
        "Null (exact)": f"{nulls.p_ge_5:.6f}",
        "Empirical": f"{emp_p5:.6f}" if isinstance(emp_p5, (int, float)) else "—",
    },
    {
        "Metric": labels.P6,
        "Null (exact)": f"{nulls.p_eq_6:.6f}",
        "Empirical": f"{emp_p6:.6f}" if isinstance(emp_p6, (int, float)) else "—",
    },
]
st.dataframe(pd.DataFrame(tail_rows), use_container_width=True, hide_index=True)

m1, m2, m3 = st.columns(3)
m1.metric(labels.EVIDENCE, evidence)
m2.metric("Bao tickets", f"{tickets(int(pool_size)):,}")
m3.metric("Cost (VND)", f"{cost(int(pool_size)):,}")

st.subheader(labels.TOP_M_NUMBERS)
st.code(" ".join(f"{n:02d}" for n in pool))
st.caption(labels.SCORE_NOT_PROBABILITY)

with st.expander(labels.ADVANCED_DEBUG):
    st.json(
        {
            "null_p6_pmf": nulls.p_eq_6,
            "bao_p6_identity": bao_p6(int(pool_size)),
        }
    )
