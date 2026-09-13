#!/usr/bin/env python3
"""Read-only probe of vietlott.vn source availability.

Must NEVER write or corrupt the canonical dataset on success or failure.
Exit codes:
  0 — source reachable / client check passed
  1 — client present but source/structure check failed
  2 — client not implemented yet, or network unreachable (not executed)
"""

from __future__ import annotations

import sys
from typing import Any


def _fail_graceful(code: int, message: str) -> int:
    stream = sys.stderr if code else sys.stdout
    print(message, file=stream)
    return code


def _probe_official_client(client_cls: type[Any]) -> int:
    """Hit landing only — no pagination crawl, no canonical writes."""
    client = client_cls()
    try:
        landing_html, key = client.fetch_landing()
        if not landing_html or not str(landing_html).strip():
            return _fail_graceful(
                1,
                "LIVE VERIFICATION = FAIL: empty landing HTML; "
                "canonical dataset untouched",
            )
        if not key:
            return _fail_graceful(
                1,
                "LIVE VERIFICATION = FAIL: AjaxPro history key missing "
                "(possible SOURCE_SCHEMA_CHANGED); canonical dataset untouched",
            )
        print(
            "LIVE VERIFICATION = PASS "
            f"(landing_bytes={len(landing_html)}, key_len={len(str(key))}; "
            "read-only; canonical dataset untouched)"
        )
        return 0
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()


def main() -> int:
    print("live_source_check: read-only; will not write data/processed or manifests")

    # Prefer the lab's official client when P1 is present.
    try:
        from vietlott_quant_lab.data.client import VietlottOfficialClient

        print("Found vietlott_quant_lab.data.client.VietlottOfficialClient")
        try:
            return _probe_official_client(VietlottOfficialClient)
        except Exception as exc:  # noqa: BLE001 — never crash into a write path
            name = type(exc).__name__
            # Network / Cloudflare → NOT EXECUTED; schema errors → FAIL.
            if name in {"FetchError", "TimeoutError", "ConnectError", "HTTPError"}:
                return _fail_graceful(
                    2,
                    f"LIVE VERIFICATION = NOT EXECUTED: {name}: {exc}. "
                    "Canonical dataset untouched.",
                )
            if "SourceSchemaChanged" in name or "SchemaChanged" in name:
                return _fail_graceful(
                    1,
                    f"LIVE VERIFICATION = FAIL: {name}: {exc}. "
                    "Canonical dataset untouched.",
                )
            return _fail_graceful(
                2,
                f"LIVE VERIFICATION = NOT EXECUTED: probe raised {name}: {exc}. "
                "Canonical dataset untouched.",
            )
    except ImportError:
        pass

    # Fallback: optional hook names if a thinner API appears later.
    for module_path, attr in (
        ("vietlott_quant_lab.data.client", "check_live"),
        ("vietlott_quant_lab.data.client", "probe_source"),
    ):
        try:
            module = __import__(module_path, fromlist=[attr])
            fn = getattr(module, attr, None)
            if callable(fn):
                result = fn()
                ok = (
                    bool(result)
                    if not isinstance(result, dict)
                    else bool(result.get("ok", False))
                )
                print(f"live_source_check result via {attr}: {result!r}")
                if ok:
                    print(
                        "LIVE VERIFICATION = PASS "
                        "(read-only; canonical dataset untouched)"
                    )
                    return 0
                return _fail_graceful(
                    1,
                    "LIVE VERIFICATION = FAIL (structure/source); "
                    "canonical dataset untouched",
                )
        except ImportError:
            continue
        except Exception as exc:  # noqa: BLE001
            return _fail_graceful(
                2,
                f"LIVE VERIFICATION = NOT EXECUTED: {type(exc).__name__}: {exc}. "
                "Canonical dataset untouched.",
            )

    return _fail_graceful(
        2,
        "LIVE VERIFICATION = NOT EXECUTED: official client not available yet. "
        "Expected VietlottOfficialClient.fetch_landing or check_live/probe_source.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
