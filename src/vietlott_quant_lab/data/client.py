"""Official Vietlott Mega 6/45 crawler (anchor-verified EOF)."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import urljoin

from vietlott_quant_lab.config.constants import (
    AJAX_COMPARE_PATH,
    DEFAULT_MAX_HISTORY_PAGES,
    DETAIL_PATH_TEMPLATE,
    FIRST_DRAW_ID,
    HISTORY_PAGE_SIZE,
    HISTORY_PATH,
    HTTP_USER_AGENT,
    OFFICIAL_BASE_URL,
)
from vietlott_quant_lab.data.errors import FetchError, SourceSchemaChangedError
from vietlott_quant_lab.data.http import GuardedHttpClient, build_ajax_history_body
from vietlott_quant_lab.data.parser import (
    RawHistoryRow,
    discover_history_key,
    parse_ajax_envelope,
    parse_detail_html,
    parse_history_html,
)
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.observability.logging import get_logger, log_event

logger = get_logger(__name__)

CrawlMode = Literal["exact", "at-or-below"]


class VietlottOfficialClient:
    """Paginated history crawler with EOF anchored on #00001 or prior latestId."""

    def __init__(
        self,
        *,
        http: GuardedHttpClient | None = None,
        base_url: str = OFFICIAL_BASE_URL,
        page_delay_ms: int = 400,
        max_pages: int = DEFAULT_MAX_HISTORY_PAGES,
        user_agent: str = HTTP_USER_AGENT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.page_delay_ms = page_delay_ms
        self.max_pages = max_pages
        self._owns_http = http is None
        self.http = http or GuardedHttpClient(user_agent=user_agent)

    def close(self) -> None:
        if self._owns_http:
            self.http.close()

    def __enter__(self) -> VietlottOfficialClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def history_url(self) -> str:
        return urljoin(f"{self.base_url}/", HISTORY_PATH.lstrip("/"))

    def detail_url(self, draw_id: str) -> str:
        path = DETAIL_PATH_TEMPLATE.format(draw_id=draw_id)
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    def ajax_url(self) -> str:
        return urljoin(f"{self.base_url}/", AJAX_COMPARE_PATH.lstrip("/"))

    def fetch_landing(self) -> tuple[str, str]:
        """Return (landing_html, ajax_key)."""
        url = self.history_url()
        response = self.http.get(url)
        key = discover_history_key(response.text)
        return response.text, key

    def fetch_history_page_html(self, page_index: int, key: str) -> str:
        if page_index < 0:
            raise ValueError("page_index must be >= 0")
        body = json.dumps(
            build_ajax_history_body(page_index, key),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        response = self.http.post(
            self.ajax_url(),
            content=body.encode("utf-8"),
            headers={
                "Accept": "application/json,text/plain,*/*",
                "Content-Type": "text/plain; charset=utf-8",
                "X-AjaxPro-Method": "ServerSideDrawResult",
                "User-Agent": self.http.user_agent,
            },
        )
        return parse_ajax_envelope(response.text)

    def fetch_draw(self, draw_id: str) -> DrawRecord:
        url = self.detail_url(draw_id)
        response = self.http.get(url)
        raw = parse_detail_html(response.text)
        return self._to_draw_record(raw, source_url=url)

    def crawl_full(self) -> list[DrawRecord]:
        rows = self._crawl(FIRST_DRAW_ID, mode="exact")
        return [self._to_draw_record(r, source_url=self._row_source_url(r)) for r in rows]

    def crawl_incremental(self, latest_id: str) -> list[DrawRecord]:
        """Fetch draws newer than ``latest_id``; stop after positively reaching it."""
        rows = self._crawl(latest_id, mode="at-or-below")
        return [self._to_draw_record(r, source_url=self._row_source_url(r)) for r in rows]

    def _crawl(self, anchor_id: str, *, mode: CrawlMode) -> list[RawHistoryRow]:
        landing_html, key = self.fetch_landing()
        reached_anchor = False
        collected: list[RawHistoryRow] = []

        for page in range(self.max_pages):
            html = (
                landing_html if page == 0 else self.fetch_history_page_html(page, key)
            )

            # CRITICAL: trust empty only AFTER positively reaching the anchor.
            outcome = parse_history_html(html, trust_empty_page=reached_anchor)

            if outcome.state == "PARSE_EMPTY_VALID_PAGE":
                break

            page_rows = list(outcome.rows)
            if not reached_anchor:
                if mode == "exact":
                    reached_anchor = any(r.draw_id == anchor_id for r in page_rows)
                else:
                    reached_anchor = any(int(r.draw_id) <= int(anchor_id) for r in page_rows)

            if mode == "at-or-below":
                collected.extend(r for r in page_rows if int(r.draw_id) > int(anchor_id))
            else:
                collected.extend(page_rows)

            is_short_page = len(page_rows) < HISTORY_PAGE_SIZE
            # Stop on short page OR after seeing the anchor on this page.
            # Never treat "no fresh ids" alone as EOF before the anchor.
            if is_short_page or reached_anchor:
                break

            if page + 1 < self.max_pages:
                time.sleep(self.page_delay_ms / 1000.0)

        if not reached_anchor:
            if mode == "exact":
                raise FetchError(
                    f"full crawl never observed draw #{FIRST_DRAW_ID} after "
                    f"{self.max_pages} pages — refusing truncated dataset"
                )
            raise FetchError(
                f"incremental crawl never reached known anchor #{anchor_id} after "
                f"{self.max_pages} pages — source may have changed"
            )

        log_event(
            logger,
            "crawl_complete",
            mode=mode,
            anchor_id=anchor_id,
            collected=len(collected),
        )
        return collected

    def _row_source_url(self, row: RawHistoryRow) -> str:
        return self.detail_url(row.draw_id)

    @staticmethod
    def _to_draw_record(row: RawHistoryRow, *, source_url: str) -> DrawRecord:
        # Schema validates uniqueness / range / sort; raise SourceSchemaChanged if bad.
        try:
            return DrawRecord(
                draw_id=row.draw_id,
                draw_date=row.draw_date,
                numbers=tuple(row.numbers),
                source_url=source_url,
                fetched_at=datetime.now(UTC),
            )
        except Exception as exc:
            raise SourceSchemaChangedError(
                f"invalid draw row {row.draw_id}: {exc} (SOURCE_SCHEMA_CHANGED)"
            ) from exc
