"""System Health — source, parser, integrity, freshness, duckdb, artifacts, chain."""

from __future__ import annotations

import streamlit as st

from vietlott_quant_lab import __version__
from vietlott_quant_lab.config.constants import PARSER_VERSION
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.loaders import build_system_health, list_experiment_artifacts

st.set_page_config(page_title=f"{labels.PAGE_SYSTEM_HEALTH} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_SYSTEM_HEALTH)
st.caption(labels.HEALTH_UNKNOWN_NETWORK)

health = build_system_health(app_version=__version__)
artifacts = list_experiment_artifacts()

rows = [
    (labels.SOURCE_REACHABLE, health.source_status),
    (labels.PARSER_STATUS, f"{health.parser_status} (const {PARSER_VERSION})"),
    (
        labels.DATASET_INTEGRITY,
        labels.STATUS_PASS
        if health.integrity_ok is True
        else labels.STATUS_FAIL
        if health.integrity_ok is False
        else labels.STATUS_MISSING,
    ),
    (labels.DATASET_FRESHNESS, health.freshness),
    (
        labels.DUCKDB_STATUS,
        f"{labels.STATUS_OK if health.duckdb_ok else labels.STATUS_MISSING} · {health.duckdb_path}",
    ),
    (labels.EXPERIMENT_ARTIFACTS, str(health.artifact_count)),
    (
        labels.PROSPECTIVE_CHAIN,
        health.prospective_message
        if health.prospective_chain_ok is None
        else (labels.CHAIN_OK if health.prospective_chain_ok else labels.CHAIN_FAIL),
    ),
    (labels.APP_VERSION, health.app_version),
]

for name, value in rows:
    st.write(f"**{name}:** `{value}`")

st.subheader("Chi tiết")
detail_rows = [
    (labels.DATASET_HASH, health.dataset_hash),
    (labels.DRAW_COUNT, health.record_count),
    (labels.LAST_SYNC, health.last_sync),
    (labels.VALIDATION, health.validation_status),
]
for name, value in detail_rows:
    st.write(f"**{name}:** `{value}`")
if health.integrity_issues:
    with st.expander(labels.ADVANCED_DEBUG):
        st.json({"integrity_issues": list(health.integrity_issues[:10])})

if health.integrity_ok is False:
    st.error(labels.STATUS_FAIL)
    for issue in health.integrity_issues[:30]:
        st.write(f"- {issue}")

st.subheader(labels.EXPERIMENT_ARTIFACTS)
if not artifacts:
    st.warning(labels.MISSING_ARTIFACT)
else:
    st.dataframe(
        [
            {
                "experiment_id": a.experiment_id,
                "kind": a.kind,
                "model": a.model,
                "scientific_verdict": a.scientific_verdict,
                "generated_at": a.generated_at,
                "path": a.path.name,
            }
            for a in artifacts
        ],
        use_container_width=True,
        hide_index=True,
    )
