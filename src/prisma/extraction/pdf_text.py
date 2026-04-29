"""PDF full-text extraction using PyMuPDF (fitz).

Returns text per page and helper utilities for section detection (Methods,
Results, Discussion) which are the typical anchors for SLR data extraction.
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError("PyMuPDF is required. Install with: pip install pymupdf") from exc


@dataclass
class PageText:
    page: int
    text: str


SECTION_HEADERS = {
    "abstract": r"^\s*(abstract|resumo|resumen)\b",
    "introduction": r"^\s*(1\.?\s*)?introduction\b",
    "methods": r"^\s*(\d\.?\s*)?(methods?|methodology|materials and methods)\b",
    "results": r"^\s*(\d\.?\s*)?results\b",
    "discussion": r"^\s*(\d\.?\s*)?discussion\b",
    "conclusion": r"^\s*(\d\.?\s*)?(conclusions?|concluding remarks)\b",
    "references": r"^\s*(references|bibliography)\b",
}


def extract_pdf_text(pdf_path: str | Path, max_pages: int | None = None) -> list[PageText]:
    """Return per-page text. `max_pages` truncates very long PDFs."""
    pages: list[PageText] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            if max_pages is not None and i >= max_pages:
                break
            pages.append(PageText(page=i + 1, text=page.get_text("text")))
    return pages


def extract_section(pages: list[PageText], section: str) -> str:
    """Extract a named section (`methods`, `results`, etc.) from the document.

    Heuristic: find the first line matching the section header and concatenate
    until the next known section header. Imperfect for non-standard layouts
    but works for the great majority of journal articles.
    """
    if section not in SECTION_HEADERS:
        raise ValueError(f"Unknown section '{section}'. Available: {list(SECTION_HEADERS)}")
    start_pat = re.compile(SECTION_HEADERS[section], re.IGNORECASE | re.MULTILINE)
    other_pats = [
        re.compile(p, re.IGNORECASE | re.MULTILINE)
        for k, p in SECTION_HEADERS.items()
        if k != section
    ]

    full_text = "\n".join(p.text for p in pages)
    m = start_pat.search(full_text)
    if not m:
        return ""
    start = m.end()
    next_starts = [p.search(full_text, pos=start) for p in other_pats]
    next_pos = min((m.start() for m in next_starts if m), default=len(full_text))
    return full_text[start:next_pos].strip()


def iter_pdfs(directory: str | Path) -> Iterator[Path]:
    """Yield all PDF paths under `directory`."""
    yield from Path(directory).rglob("*.pdf")
