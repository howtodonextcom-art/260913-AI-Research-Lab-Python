"""Smoke test: package imports cleanly."""

from __future__ import annotations


def test_package_import() -> None:
    import vietlott_quant_lab

    assert vietlott_quant_lab.__version__
    assert isinstance(vietlott_quant_lab.__version__, str)


def test_config_constants() -> None:
    from vietlott_quant_lab.config import LOOKBACK_WINDOWS, POOL_SIZES, PRODUCT_MEGA645

    assert PRODUCT_MEGA645 == "mega645"
    assert 18 in POOL_SIZES
    assert 7 in POOL_SIZES
    assert "ALL" in LOOKBACK_WINDOWS
