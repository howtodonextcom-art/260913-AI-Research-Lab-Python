"""Guarded httpx client for official vietlott.vn only (SSRF allowlist)."""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

from vietlott_quant_lab.config.constants import (
    HTTP_MAX_RESPONSE_BYTES,
    HTTP_USER_AGENT,
    OFFICIAL_ALLOWED_HOST,
)
from vietlott_quant_lab.data.errors import FetchError
from vietlott_quant_lab.observability.logging import get_logger, log_event

logger = get_logger(__name__)

RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({408, 425, 429, 500, 502, 503, 504})
_SENSITIVE_QUERY_KEYS: frozenset[str] = frozenset(
    {"password", "passwd", "token", "apikey", "api_key", "secret", "auth", "credential"}
)


@dataclass(frozen=True, slots=True)
class HttpResponse:
    url: str
    status_code: int
    text: str
    content: bytes


def assert_allowed_url(url: str, *, allowed_host: str = OFFICIAL_ALLOWED_HOST) -> None:
    """Reject anything that is not https://{allowed_host}/... without credentials."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise FetchError(f"only https is allowed, got scheme={parsed.scheme!r} for {url!r}")
    if parsed.username or parsed.password:
        raise FetchError("credentials in URL are forbidden")
    host = (parsed.hostname or "").lower()
    if host != allowed_host.lower():
        raise FetchError(f"host {host!r} is not allowlisted (only {allowed_host!r})")
    if parsed.query:
        for key in parse_qs(parsed.query, keep_blank_values=True):
            if key.lower() in _SENSITIVE_QUERY_KEYS:
                raise FetchError(f"forbidden credential-like query key {key!r} in URL")


class GuardedHttpClient:
    """httpx wrapper: allowlist host, timeout, retry/backoff, max bytes, fixed UA."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        max_response_bytes: int = HTTP_MAX_RESPONSE_BYTES,
        user_agent: str = HTTP_USER_AGENT,
        allowed_host: str = OFFICIAL_ALLOWED_HOST,
        max_retries: int = 3,
        client: httpx.Client | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_response_bytes = max_response_bytes
        self.user_agent = user_agent
        self.allowed_host = allowed_host
        self.max_retries = max_retries
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=False,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml",
            },
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> GuardedHttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> HttpResponse:
        return self._request("GET", url, headers=headers)

    def post(
        self,
        url: str,
        *,
        content: bytes | str,
        headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        return self._request("POST", url, content=content, headers=headers)

    def _request(
        self,
        method: str,
        url: str,
        *,
        content: bytes | str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        assert_allowed_url(url, allowed_host=self.allowed_host)
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    url,
                    content=content,
                    headers=dict(headers) if headers else None,
                )
                body = response.content
                if len(body) > self.max_response_bytes:
                    raise FetchError(
                        f"response exceeded {self.max_response_bytes} bytes for {url}"
                    )
                if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                    log_event(
                        logger,
                        "http_retry",
                        method=method,
                        url=url,
                        status=response.status_code,
                        attempt=attempt,
                    )
                    time.sleep(0.8 * attempt)
                    continue
                if response.status_code >= 400:
                    raise FetchError(f"HTTP {response.status_code} for {method} {url}")
                return HttpResponse(
                    url=str(response.url),
                    status_code=response.status_code,
                    text=body.decode(response.encoding or "utf-8", errors="replace"),
                    content=body,
                )
            except FetchError:
                raise
            except httpx.HTTPError as exc:
                last_error = exc
                log_event(
                    logger,
                    "http_network_error",
                    method=method,
                    url=url,
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt >= self.max_retries:
                    raise FetchError(f"network error for {method} {url}: {exc}") from exc
                time.sleep(0.8 * attempt)
        raise FetchError(f"failed {method} {url}: {last_error}")


def build_ajax_history_body(page_index: int, key: str) -> dict[str, Any]:
    """AjaxPro ServerSideDrawResult request body (page size observed as 8)."""
    return {
        "ORenderInfo": {
            "SiteId": "main.frontend.vi",
            "SiteAlias": "main.vi",
            "UserSessionId": "",
            "SiteLang": "vi",
            "IsPageDesign": False,
            "ExtraParam1": "",
            "ExtraParam2": "",
            "ExtraParam3": "",
            "SiteURL": "",
            "WebPage": None,
            "SiteName": "Vietlott",
            "OrgPageAlias": None,
            "PageAlias": None,
            "FullPageAlias": None,
            "RefKey": None,
            "System": 1,
        },
        "Key": key,
        "GameDrawId": "",
        "ArrayNumbers": [[""] * 18 for _ in range(6)],
        "CheckMulti": False,
        "PageIndex": page_index,
    }
