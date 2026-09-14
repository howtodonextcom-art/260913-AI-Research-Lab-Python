"""Shared dataset status + optional live sync control for Streamlit pages."""

from __future__ import annotations

from vietlott_quant_lab.config.settings import Settings, get_settings
from vietlott_quant_lab.data.errors import DataLayerError
from vietlott_quant_lab.data.sync import sync_official
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.cache import clear_data_caches
from vietlott_quant_lab.ui.loaders import DatasetBundle, load_dataset_bundle


def format_dataset_headline(bundle: DatasetBundle) -> str:
    """One-line status for banners (no Streamlit dependency)."""
    if not bundle.draws and bundle.manifest is None:
        return labels.DATASET_BANNER_EMPTY
    m = bundle.manifest
    draw_id = (m.last_draw_id if m else None) or (
        bundle.draws[-1].draw_id if bundle.draws else "—"
    )
    draw_date = (m.last_draw_date if m else None) or (
        bundle.draws[-1].draw_date.isoformat() if bundle.draws else "—"
    )
    count = m.record_count if m else len(bundle.draws)
    hash_short = (bundle.dataset_hash[:12] + "…") if bundle.dataset_hash else "—"
    validation = m.validation_status if m else "UNKNOWN"
    return (
        f"Dữ liệu tới: **{draw_date}** (#{draw_id}) · "
        f"{count} kỳ · hash `{hash_short}` · validation `{validation}`"
    )


def render_dataset_status_panel(
    *,
    bundle: DatasetBundle | None = None,
    settings: Settings | None = None,
    show_update: bool = True,
    key_prefix: str = "dataset",
) -> DatasetBundle:
    """Render last-draw metrics and optional Update-data control.

    Import streamlit only at call time so unit tests can import helpers without
    starting a Streamlit runtime.
    """
    import streamlit as st

    cfg = settings or get_settings()
    data = bundle if bundle is not None else load_dataset_bundle(cfg)

    st.subheader(labels.DATASET_SECTION)
    if not data.draws:
        st.info(labels.MISSING_DATASET)
    else:
        m = data.manifest
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(labels.DRAW_COUNT, m.record_count if m else len(data.draws))
        c2.metric(labels.LATEST_DRAW, (m.last_draw_id if m else data.draws[-1].draw_id))
        c3.metric(
            labels.LAST_DRAW_DATE,
            (m.last_draw_date if m else data.draws[-1].draw_date.isoformat()),
        )
        sync_disp = (m.last_sync if m and m.last_sync else "—")
        c4.metric(labels.LAST_SYNC, sync_disp[:19] if sync_disp != "—" else "—")
        st.markdown(format_dataset_headline(data))
        if m:
            st.caption(
                f"{labels.SOURCE}: `{m.source}` · {labels.DATASET_HASH}: `{data.dataset_hash}`"
            )

    if not show_update:
        return data

    st.markdown(f"**{labels.UPDATE_DATA}**")
    st.caption(labels.UPDATE_DATA_HELP)
    clicked = st.button(
        labels.UPDATE_DATA,
        type="primary",
        key=f"{key_prefix}_update_btn",
    )
    if clicked:
        if not cfg.vietlott_allow_live_fetch:
            st.warning(labels.UPDATE_DATA_BLOCKED)
        else:
            with st.spinner("Đang đồng bộ từ vietlott.vn…"):
                try:
                    result = sync_official(settings=cfg, force_full=False)
                except DataLayerError as exc:
                    st.error(f"Sync thất bại (fail-closed): {exc}")
                except Exception as exc:  # noqa: BLE001 — surface to operator
                    st.error(f"Sync lỗi không mong đợi: {exc}")
                else:
                    clear_data_caches()
                    st.success(
                        f"Sync OK · mode=`{result.mode}` · fetched={result.records_fetched} · "
                        f"total={result.record_count} · "
                        f"hash=`{result.dataset_sha256[:12]}…`"
                    )
                    st.rerun()
    st.caption(labels.UPDATE_DATA_CLI)
    return data
