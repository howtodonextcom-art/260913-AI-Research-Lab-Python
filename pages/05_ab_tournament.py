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
if isinstance(champion, dict):
    st.write(champion)

verdict = artifact.get("scientific_verdict") or labels.DEFAULT_SCIENTIFIC_VERDICT
holdout = artifact.get("holdout_status") or (artifact.get("extra") or {}).get("holdout_status")
st.write(
    {
        labels.SCIENTIFIC_VERDICT: verdict,
        labels.HOLDOUT_STATUS: holdout or "—",
        labels.PROTOCOL_HASH: artifact.get("protocol_hash"),
        labels.DATASET_HASH: artifact.get("dataset_hash"),
    }
)

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

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"**{labels.DEVELOPMENT}**")
    st.json(artifact.get("development_results") or artifact.get("development") or {})
with c2:
    st.markdown(f"**{labels.VALIDATION}**")
    st.json(artifact.get("validation_results") or artifact.get("validation") or {})
with c3:
    st.markdown(f"**{labels.TEST}**")
    st.json(artifact.get("test_results") or artifact.get("test") or {})

st.subheader("Artifacts")
for summary in list_experiment_artifacts()[:10]:
    with st.expander(summary.path.name):
        st.code(json.dumps(summary.payload, indent=2, ensure_ascii=False)[:4000])
