"""HTTP allowlist / SSRF guard tests (no network)."""

from __future__ import annotations

import pytest

from vietlott_quant_lab.data.errors import FetchError
from vietlott_quant_lab.data.http import assert_allowed_url


def test_allows_official_https() -> None:
    assert_allowed_url("https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645")


def test_rejects_other_host() -> None:
    with pytest.raises(FetchError):
        assert_allowed_url("https://evil.example/steal")


def test_rejects_http() -> None:
    with pytest.raises(FetchError):
        assert_allowed_url("http://vietlott.vn/")


def test_rejects_credentials_in_url() -> None:
    with pytest.raises(FetchError):
        assert_allowed_url("https://user:pass@vietlott.vn/")


def test_rejects_sensitive_query() -> None:
    with pytest.raises(FetchError):
        assert_allowed_url("https://vietlott.vn/path?api_key=secret")


def test_allows_draw_id_query() -> None:
    assert_allowed_url("https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645?id=00001&nocatche=1")
