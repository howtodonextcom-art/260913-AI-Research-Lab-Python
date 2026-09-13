"""Real-Chromium E2E acceptance for all 8 Streamlit pages across the mandatory
viewport matrix (desktop/tablet/mobile). See artifacts/reports/BROWSER_ACCEPTANCE.md
for the human-readable report this suite backs.

Not a substitute test: this drives an actual `streamlit run app.py` server with a
real Chromium browser (Playwright), not `compile()`/import-only checks.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page

SCREENSHOT_DIR = (
    Path(__file__).resolve().parents[2] / "artifacts" / "reports" / "browser_screenshots"
)

VIEWPORTS = {
    "desktop": (1440, 900),
    "tablet": (768, 1024),
    "mobile": (390, 844),
}

PAGES = [
    "overview",
    "data_library",
    "number_lab",
    "candidate_pool",
    "ab_tournament",
    "compression_frontier",
    "prospective",
    "system_health",
]

TRACEBACK_MARKERS = (
    "Traceback (most recent call last)",
    "This app has encountered an error",
    "streamlit.errors.",
)

# Streamlit's own frontend polls `_stcore/health` and `_stcore/host-config` relative
# to the current path; on a direct deep-link into a sub-page (e.g. `/overview`) this
# resolves to `/overview/_stcore/health`, which 404s — a benign Streamlit-internal
# quirk (the page still renders and functions correctly), not an app defect. The
# generic "Failed to load resource" console message is just an echo of that same
# network failure, so it is allowlisted too, in lockstep with the network check.
_BENIGN_404_SUFFIXES = ("/_stcore/health", "/_stcore/host-config")
_GENERIC_RESOURCE_LOAD_ERROR = (
    "Failed to load resource: the server responded with a status of 404 (Not Found)"
)


def _is_benign_network_failure(status: int, url: str) -> bool:
    return status == 404 and url.endswith(_BENIGN_404_SUFFIXES)


def _render_and_check(page: Page, base_url: str, slug: str, viewport_name: str) -> str:
    page.goto(f"{base_url}/{slug}", wait_until="load", timeout=30_000)
    # No permanent "running" spinner.
    page.wait_for_selector('[data-testid="stStatusWidget"]', state="hidden", timeout=15_000)
    # Streamlit reruns the script (and briefly clears the DOM) on first paint after a
    # direct deep-link; poll rather than sleep-once so a mid-rerun snapshot can't be
    # mistaken for a genuinely blank page.
    body_text = ""
    for _ in range(20):
        body_text = page.inner_text("body")
        if body_text.strip():
            break
        page.wait_for_timeout(250)
    assert body_text.strip(), f"{slug}: blank page at {viewport_name}"
    for marker in TRACEBACK_MARKERS:
        assert marker not in body_text, f"{slug}: uncaught traceback rendered at {viewport_name}"
    # Let Streamlit's per-widget loading skeletons resolve before the evidence screenshot,
    # so the saved image reflects settled content instead of a mid-render placeholder.
    for _ in range(20):
        if page.locator('[data-testid="stSkeleton"]').count() == 0:
            break
        page.wait_for_timeout(250)
    body_text = page.inner_text("body")
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOT_DIR / f"{slug}_{viewport_name}.png"), full_page=True)
    return body_text


@pytest.mark.browser
@pytest.mark.parametrize("slug", PAGES)
@pytest.mark.parametrize("viewport_name", list(VIEWPORTS))
def test_page_renders_without_error(
    streamlit_base_url: str, make_page, slug: str, viewport_name: str
) -> None:
    width, height = VIEWPORTS[viewport_name]
    page = make_page(width, height)
    console_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    failed_requests: list[str] = []
    page.on(
        "response",
        lambda resp: failed_requests.append(f"{resp.status} {resp.url}")
        if resp.status >= 400 and not _is_benign_network_failure(resp.status, resp.url)
        else None,
    )

    _render_and_check(page, streamlit_base_url, slug, viewport_name)

    real_console_errors = [e for e in console_errors if e != _GENERIC_RESOURCE_LOAD_ERROR]
    assert not real_console_errors, f"{slug}@{viewport_name}: console errors: {real_console_errors}"
    assert not failed_requests, f"{slug}@{viewport_name}: failed requests: {failed_requests}"

    box = page.locator("body").bounding_box()
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    if box is not None:
        assert scroll_width <= width + 40, (
            f"{slug}@{viewport_name}: horizontal overflow "
            f"(scrollWidth={scroll_width}, viewport={width})"
        )


@pytest.mark.browser
def test_number_lab_widget_changes_output(streamlit_base_url: str, make_page) -> None:
    page = make_page(1440, 900)
    page.goto(f"{streamlit_base_url}/number_lab", wait_until="load", timeout=30_000)
    page.wait_for_timeout(1500)

    combo = page.get_by_role("combobox", name="Chọn số (01–45)")
    metric_before = page.locator('[data-testid="stMetricValue"]').first.inner_text()

    combo.click()
    page.wait_for_timeout(200)
    combo.fill("23")
    page.wait_for_timeout(400)
    page.locator('[role="option"]').first.click()
    page.wait_for_timeout(1500)

    assert combo.input_value() == "23"
    metric_after = page.locator('[data-testid="stMetricValue"]').first.inner_text()
    assert metric_after != metric_before, "Number Lab: changing number did not change metrics"


@pytest.mark.browser
def test_candidate_pool_model_selector_changes_pool(streamlit_base_url: str, make_page) -> None:
    page = make_page(1440, 900)
    page.goto(f"{streamlit_base_url}/candidate_pool", wait_until="load", timeout=30_000)
    page.wait_for_timeout(1500)

    code_before = page.locator("code").first.inner_text()
    combo = page.get_by_role("combobox", name="Model ranking")
    combo.click()
    page.wait_for_timeout(200)
    options = page.locator('[role="option"]')
    assert options.count() >= 2
    options.nth(1).click()
    page.wait_for_timeout(1500)

    code_after = page.locator("code").first.inner_text()
    assert code_after != code_before, "Candidate Pool: changing model did not change the pool"


@pytest.mark.browser
def test_candidate_pool_size_changes_metrics(streamlit_base_url: str, make_page) -> None:
    page = make_page(1440, 900)
    page.goto(f"{streamlit_base_url}/candidate_pool", wait_until="load", timeout=30_000)
    page.wait_for_timeout(1500)

    numbers_before = page.locator("code").first.inner_text().split()
    assert len(numbers_before) == 18, "default pool size should be 18"

    # The select_slider's real <input type="range"> is visually hidden (accessible-hidden
    # thumb pattern); force the click past Playwright's visibility check, then drive it
    # with arrow keys — increasing the underlying index walks the reversed option list
    # (18, 17, ..., 7) toward smaller pool sizes.
    slider_input = page.locator('input[type="range"]').first
    slider_input.click(force=True)
    for _ in range(6):
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(150)
    page.wait_for_timeout(800)

    numbers_after = page.locator("code").first.inner_text().split()
    assert len(numbers_after) < 18, "reducing pool size did not shrink the Top-m list"
    assert set(numbers_after).issubset(set(numbers_before)), (
        "nested Top-m invariant violated: smaller pool must be a subset of pool 18"
    )
