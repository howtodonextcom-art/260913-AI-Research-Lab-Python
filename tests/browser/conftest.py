"""Fixtures for real-Chromium Streamlit E2E tests.

These start an actual `streamlit run app.py` server and drive it with a real
Chromium browser via Playwright — no import/compile substitution, no mocked
frontend. Excluded from default `pytest -q` discovery (see pyproject.toml
`norecursedirs`); run explicitly with `pytest tests/browser`.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = 8765
BASE_URL = f"http://127.0.0.1:{PORT}"
HEALTH_URL = f"{BASE_URL}/_stcore/health"
STARTUP_TIMEOUT_S = 60.0

SCREENSHOT_DIR = REPO_ROOT / "artifacts" / "reports" / "browser_screenshots"


def _wait_for_health(url: str, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError) as exc:
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"Streamlit did not become healthy at {url} in time: {last_error}")


@pytest.fixture(scope="session")
def streamlit_base_url() -> Iterator[str]:
    env = dict(os.environ)
    env.setdefault("VIETLOTT_ALLOW_LIVE_FETCH", "0")
    log_path = SCREENSHOT_DIR.parent / "streamlit_server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # NOTE: stdout/stderr must go to a real file, not subprocess.PIPE — nothing
    # drains a PIPE here, so once Streamlit's log output fills the OS pipe buffer
    # the server blocks on write and stops answering requests mid-suite.
    with open(log_path, "w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(  # noqa: S603
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app.py",
                f"--server.port={PORT}",
                "--server.address=127.0.0.1",
                "--server.headless=true",
            ],
            cwd=REPO_ROOT,
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        try:
            _wait_for_health(HEALTH_URL, STARTUP_TIMEOUT_S)
            yield BASE_URL
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


@pytest.fixture(scope="session")
def chromium() -> Iterator[Browser]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def make_page(chromium: Browser):
    contexts = []

    def _make(width: int, height: int):
        context = chromium.new_context(viewport={"width": width, "height": height})
        contexts.append(context)
        page = context.new_page()
        return page

    yield _make
    for context in contexts:
        context.close()


SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
