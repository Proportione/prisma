"""OpenAlex API client for corpus building.

OpenAlex is open access, no API key required. A polite email is recommended
via the `mailto` parameter to be moved into the polite pool (faster + more
reliable). See https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication.
"""
from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import requests

OPENALEX_BASE = "https://api.openalex.org/works"


def openalex_search(
    query: str,
    per_page: int = 100,
    max_records: int | None = None,
    mailto: str | None = None,
    filters: dict[str, str] | None = None,
    sleep: float = 0.1,
) -> Iterator[dict[str, Any]]:
    """Yield works matching `query` from OpenAlex, page by page.

    Args:
        query: full-text search expression (passed to `search` parameter).
        per_page: 1..200, OpenAlex max is 200.
        max_records: stop after this many records (None = all).
        mailto: contact email for the polite pool.
        filters: extra OpenAlex filters, e.g. `{"from_publication_date": "2015-01-01"}`.
        sleep: seconds between page requests.
    """
    cursor = "*"
    fetched = 0
    params: dict[str, str | int] = {
        "search": query,
        "per_page": min(per_page, 200),
        "cursor": cursor,
    }
    if mailto:
        params["mailto"] = mailto
    if filters:
        params["filter"] = ",".join(f"{k}:{v}" for k, v in filters.items())

    while True:
        params["cursor"] = cursor
        r = requests.get(OPENALEX_BASE, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        works = payload.get("results", [])
        if not works:
            break
        for w in works:
            yield w
            fetched += 1
            if max_records is not None and fetched >= max_records:
                return
        cursor = payload.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(sleep)


def work_to_ris(work: dict[str, Any]) -> str:
    """Convert one OpenAlex work to a RIS record."""
    title = (work.get("title") or "").replace("\n", " ").strip()
    year = str(work.get("publication_year") or "")
    doi_url = work.get("doi") or ""
    doi = doi_url.replace("https://doi.org/", "") if doi_url else ""
    abstract = _reconstruct_abstract(work.get("abstract_inverted_index"))
    journal = ""
    primary = work.get("primary_location") or {}
    src = primary.get("source") or {}
    journal = src.get("display_name") or ""

    lines = ["TY  - JOUR", f"TI  - {title}"]
    for au in work.get("authorships", [])[:50]:
        name = (au.get("author") or {}).get("display_name")
        if name:
            lines.append(f"AU  - {name}")
    if year:
        lines.append(f"PY  - {year}")
    if journal:
        lines.append(f"JO  - {journal}")
    if doi:
        lines.append(f"DO  - {doi}")
    for kw in (work.get("keywords") or [])[:20]:
        kw_text = kw.get("display_name") if isinstance(kw, dict) else str(kw)
        if kw_text:
            lines.append(f"KW  - {kw_text}")
    if abstract:
        lines.append(f"AB  - {abstract}")
    lines.append("ER  - ")
    lines.append("")
    return "\n".join(lines)


def _reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    """OpenAlex stores abstracts as an inverted index for licensing reasons."""
    if not inverted_index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted_index.items():
        positions.extend((i, word) for i in idxs)
    positions.sort()
    return " ".join(word for _, word in positions)
