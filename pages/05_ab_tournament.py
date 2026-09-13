"""A/B Tournament — show tournament artifact; winner from engine, not hard-coded."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.loaders import latest_tournament_artifact, list_experiment_artifacts

st.set_page_config(page_title=f"{labels.PAGE_AB_TOURNAMENT} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_AB_TOURNAMENT)
st.caption("Winner do research engine ghi trong artifact — UI không hard-code.")

artifact = latest_tournament_artifact()
if not artifact:
    st.info(labels.MISSING_ARTIFACT)
    st.stop()

champion = artifact.get("champion")
winner = None
if isinstance(champion, dict):
    winner = champion.get("model_id") or champion.get("model")
elif champion:
    winner = champion
else:
    winner = artifact.get("model") or (artifact.get("extra") or {}).get("winner")

st.subheader(labels.TOURNAMENT_WINNER)
st.code(str(winner) if winner is not None else "— (no champion in artifact)")

verdict = artifact.get("scientific_verdict") or labels.DEFAULT_SCIENTIFIC_VERDICT
holdout = artifact.get("holdout_status") or (artifact.get("extra") or {}).get("holdout_status")
v1, v2 = st.columns(2)
v1.metric(labels.SCIENTIFIC_VERDICT, verdict)
v2.metric(labels.HOLDOUT_STATUS, holdout or "—")
h1, h2 = st.columns(2)
h1.metric(labels.PROTOCOL_HASH, str(artifact.get("protocol_hash") or "—")[:16] + "…")
h2.metric(labels.DATASET_HASH, str(artifact.get("dataset_hash") or "—")[:16] + "…")
if isinstance(champion, dict):
    with st.expander(labels.ADVANCED_DEBUG):
        st.json(champion)

scores = artifact.get("scores")
if isinstance(scores, list) and scores:
    st.subheader("Model scores")
    rows = []
    for s in scores:
        if not isinstance(s, dict):
            continue
        dev = s.get("development") if isinstance(s.get("development"), dict) else {}
        val = s.get("validation") if isinstance(s.get("validation"), dict) else {}
        rows.append(
            {
                "model_id": s.get("model_id"),
                "lookback": s.get("lookback"),
                "complexity": s.get("complexity"),
                "dev_mean_k": dev.get("mean_k"),
                "val_mean_k": val.get("mean_k"),
            }
        )
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

phase_blocks = {
    labels.DEVELOPMENT: artifact.get("development_results") or artifact.get("development") or {},
    labels.VALIDATION: artifact.get("validation_results") or artifact.get("validation") or {},
    labels.TEST: artifact.get("test_results") or artifact.get("test") or {},
}

st.subheader("Mean K by phase")
phase_scores: dict[str, dict[str, float]] = {}
for phase_label, block in phase_blocks.items():
    scores_list = block.get("scores") if isinstance(block, dict) else None
    if isinstance(scores_list, list):
        for entry in scores_list:
            if isinstance(entry, dict) and "model_id" in entry:
                phase_scores.setdefault(str(entry["model_id"]), {})[phase_label] = entry.get(
                    "mean_k"
                )
if phase_scores:
    table_rows = [
        {
            "model_id": model_id,
            labels.DEVELOPMENT: vals.get(labels.DEVELOPMENT),
            labels.VALIDATION: vals.get(labels.VALIDATION),
            labels.TEST: vals.get(labels.TEST),
        }
        for model_id, vals in phase_scores.items()
    ]
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
else:
    st.info(labels.MISSING_ARTIFACT)

with st.expander(labels.ADVANCED_DEBUG):
    c1, c2, c3 = st.columns(3)
    for col, phase_label in zip(
        (c1, c2, c3), (labels.DEVELOPMENT, labels.VALIDATION, labels.TEST), strict=True
    ):
        with col:
            st.markdown(f"**{phase_label}**")
            st.json(phase_blocks[phase_label])

st.subheader("Artifacts")
for summary in list_experiment_artifacts()[:10]:
    with st.expander(summary.path.name):
        st.code(json.dumps(summary.payload, indent=2, ensure_ascii=False)[:4000])
