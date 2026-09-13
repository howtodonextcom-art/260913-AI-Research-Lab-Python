"""Dual parser for official Vietlott Mega 6/45 HTML (regex primary, BS4 fallback)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from typing import Literal
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from vietlott_quant_lab.config.constants import DRAW_SIZE, OFFICIAL_BASE_URL, PARSER_VERSION
from vietlott_quant_lab.data.errors import FetchError, SourceSchemaChangedError
from vietlott_quant_lab.observability.logging import get_logger, log_event

logger = get_logger(__name__)

HistoryPageState = Literal["PARSE_SUCCESS", "PARSE_EMPTY_VALID_PAGE"]

_BALL_RE = re.compile(
    r'<span[^>]*class="[^"]*\bbong_tron\b[^"]*"[^>]*>\s*(\d{1,2})\s*</span>',
    flags=re.IGNORECASE,
)
_HISTORY_ROW_RE = re.compile(
    r"<tr>\s*"
    r"<td>\s*(?P<date>\d{2}/\d{2}/\d{4})\s*</td>\s*"
    r"<td>\s*<a\s+href=\"(?P<href>[^\"]*?id=(?P<id>\d{5})&nocatche=1[^\"]*)\"[^>]*>\s*\d{5}\s*</a>\s*</td>\s*"
    r"<td>(?P<numbers>.*?)</td>\s*"
    r"</tr>",
    flags=re.IGNORECASE | re.DOTALL,
)
_DETAIL_HEADER_RE = re.compile(
    r"Kỳ\s+quay\s+thưởng\s*<b>#(?P<id>\d{5})</b>\s*ngày\s*<b>(?P<date>\d{2}/\d{2}/\d{4})</b>",
    flags=re.IGNORECASE | re.DOTALL,
)
_DETAIL_BLOCK_RE = re.compile(
    r'<div\s+class="day_so_ket_qua_v2"[^>]*>(?P<body>.*?)</div>',
    flags=re.IGNORECASE | re.DOTALL,
)
_HISTORY_KEY_RE = re.compile(
    r"Game645CompareWebPart\.ServerSideDrawResult\(RenderInfo,\s*'(?P<key>[^']+)'",
    flags=re.IGNORECASE,
)
_DATE_SHAPE_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")


@dataclass(frozen=True, slots=True)
class RawHistoryRow:
    draw_id: str
    draw_date: date
    numbers: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class HistoryPageOutcome:
    state: HistoryPageState
    rows: tuple[RawHistoryRow, ...] = ()


def parse_vietnamese_date(value: str) -> date:
    match = _DATE_SHAPE_RE.fullmatch(value.strip())
    if not match:
        raise SourceSchemaChangedError(
            f"expected DD/MM/YYYY date, got {value!r} (SOURCE_SCHEMA_CHANGED)"
        )
    day, month, year = map(int, match.groups())
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise SourceSchemaChangedError(
            f"invalid calendar date {value!r} (SOURCE_SCHEMA_CHANGED)"
        ) from exc


def extract_ball_numbers(fragment: str) -> tuple[int, ...]:
    return tuple(int(m.group(1)) for m in _BALL_RE.finditer(fragment))


def discover_history_key(html: str) -> str:
    match = _HISTORY_KEY_RE.search(html)
    if not match:
        raise SourceSchemaChangedError(
            "AjaxPro history key missing from landing page (SOURCE_SCHEMA_CHANGED)"
        )
    return match.group("key")


def _has_history_wrapper(html: str) -> bool:
    return bool(re.search(r"doso_output_nd", html, flags=re.IGNORECASE)) and bool(
        re.search(r"<tbody", html, flags=re.IGNORECASE)
    )


def _rows_from_regex(html: str) -> list[RawHistoryRow]:
    rows: list[RawHistoryRow] = []
    for match in _HISTORY_ROW_RE.finditer(html):
        numbers = extract_ball_numbers(match.group("numbers"))
        rows.append(
            RawHistoryRow(
                draw_id=match.group("id"),
                draw_date=parse_vietnamese_date(match.group("date")),
                numbers=numbers,
            )
        )
    return rows


def _rows_from_beautifulsoup(html: str) -> list[RawHistoryRow]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one(".doso_output_nd table") or soup.find("table")
    if table is None:
        return []
    rows: list[RawHistoryRow] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 3:
            continue
        date_text = cells[0].get_text(strip=True)
        link = cells[1].find("a", href=True)
        if link is None:
            continue
        href = str(link["href"])
        id_match = re.search(r"id=(\d{5})", href)
        if not id_match:
            continue
        numbers = extract_ball_numbers(str(cells[2]))
        if not numbers:
            # Balls may be plain text: "01 02 03 04 05 06"
            plain = re.findall(r"\b(\d{1,2})\b", cells[2].get_text(" ", strip=True))
            numbers = tuple(int(x) for x in plain[:DRAW_SIZE])
        try:
            rows.append(
                RawHistoryRow(
                    draw_id=id_match.group(1),
                    draw_date=parse_vietnamese_date(date_text),
                    numbers=numbers,
                )
            )
        except SourceSchemaChangedError:
            continue
    return rows


def parse_history_html(html: str, *, trust_empty_page: bool) -> HistoryPageOutcome:
    """Parse one history page.

    Empty/zero-row pages are only valid EOF when ``trust_empty_page`` is True
    (caller has already positively reached the crawl anchor).
    """
    if not _has_history_wrapper(html):
        raise SourceSchemaChangedError(
            "history table wrapper (doso_output_nd/<tbody>) missing (SOURCE_SCHEMA_CHANGED)"
        )

    rows = _rows_from_regex(html)
    parser_used = "regex"
    if not rows:
        rows = _rows_from_beautifulsoup(html)
        parser_used = "beautifulsoup"

    if not rows:
        if trust_empty_page:
            log_event(logger, "history_empty_trusted", parser_version=PARSER_VERSION)
            return HistoryPageOutcome(state="PARSE_EMPTY_VALID_PAGE")
        raise SourceSchemaChangedError(
            "history page has valid wrapper but 0 rows before crawl anchor "
            "(SOURCE_SCHEMA_CHANGED) — refusing to treat as EOF"
        )

    log_event(
        logger,
        "history_parsed",
        rows=len(rows),
        parser=parser_used,
        parser_version=PARSER_VERSION,
    )
    return HistoryPageOutcome(state="PARSE_SUCCESS", rows=tuple(rows))


def parse_detail_html(html: str) -> RawHistoryRow:
    header = _DETAIL_HEADER_RE.search(html)
    if not header:
        # Fallback: scan for #ddddd + date near "Kỳ quay"
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)
        fb = re.search(
            r"Kỳ\s+quay\s+thưởng\s*#(\d{5})\s*ngày\s*(\d{2}/\d{2}/\d{4})",
            text,
            flags=re.IGNORECASE,
        )
        if not fb:
            raise SourceSchemaChangedError(
                "detail page missing draw id/date header (SOURCE_SCHEMA_CHANGED)"
            )
        draw_id, date_str = fb.group(1), fb.group(2)
    else:
        draw_id, date_str = header.group("id"), header.group("date")

    block = _DETAIL_BLOCK_RE.search(html)
    if block:
        numbers = extract_ball_numbers(block.group("body"))
    else:
        soup = BeautifulSoup(html, "lxml")
        block_el = soup.select_one(".day_so_ket_qua_v2")
        if block_el is None:
            raise SourceSchemaChangedError(
                "detail page missing result ball block (SOURCE_SCHEMA_CHANGED)"
            )
        numbers = extract_ball_numbers(str(block_el))

    if len(numbers) != DRAW_SIZE:
        raise SourceSchemaChangedError(
            f"detail page expected {DRAW_SIZE} balls, got {len(numbers)} (SOURCE_SCHEMA_CHANGED)"
        )

    return RawHistoryRow(
        draw_id=draw_id,
        draw_date=parse_vietnamese_date(date_str),
        numbers=numbers,
    )


def parse_ajax_envelope(text: str) -> str:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FetchError("AjaxPro response is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise FetchError("AjaxPro response is not a JSON object")
    if payload.get("error"):
        raise FetchError(f"AjaxPro error: {payload['error']}")
    value = payload.get("value")
    if not isinstance(value, dict):
        raise FetchError("AjaxPro response missing 'value'")
    if value.get("Error"):
        raise FetchError(f"Vietlott history error: {value.get('InfoMessage') or value!r}")
    html = value.get("HtmlContent")
    if not isinstance(html, str):
        raise FetchError("AjaxPro response missing HtmlContent")
    return html


def absolute_detail_url(href: str, *, base: str = OFFICIAL_BASE_URL) -> str:
    return urljoin(f"{base.rstrip('/')}/", href.lstrip("/"))
