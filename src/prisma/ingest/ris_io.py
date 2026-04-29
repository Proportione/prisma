"""RIS file parsing and writing utilities.

Supports the common RIS tag set (TY, TI/T1, AU, PY/Y1, JO/T2/JF, KW, AB, DO, ER).
Records are represented as a list of (tag, value) tuples to preserve duplicate
tags (e.g., multiple AU entries) and original ordering.
"""
from __future__ import annotations

import re
from pathlib import Path

Record = list[tuple[str, str]]

_TAG_RE = re.compile(r"^([A-Z][A-Z0-9])  - (.*)$")


def parse_ris(filepath: str | Path) -> list[Record]:
    """Parse a RIS file into a list of records.

    Each record is a list of (tag, value) tuples. New records are detected
    by the `TY` tag; the closing `ER` tag is consumed but not retained.
    """
    records: list[Record] = []
    current: Record = []
    with open(filepath, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n\r")
            m = _TAG_RE.match(line)
            if not m:
                continue
            tag, value = m.group(1), m.group(2)
            if tag == "TY" and current:
                records.append(current)
                current = []
            if tag == "ER":
                continue
            current.append((tag, value))
    if current:
        records.append(current)
    return records


def get_field(record: Record, tag: str) -> str:
    """Return the first value for `tag`, stripped, or '' if absent."""
    for t, v in record:
        if t == tag:
            return v.strip()
    return ""


def get_all_fields(record: Record, tag: str) -> list[str]:
    """Return all values for `tag`, stripped."""
    return [v.strip() for t, v in record if t == tag]


def normalize_title(title: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)
    return re.sub(r"\s+", " ", title).strip()


def normalize_doi(doi: str) -> str:
    """Strip DOI URL/scheme prefixes and lowercase."""
    doi = doi.lower().strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return re.sub(r"^doi:\s*", "", doi)


def record_to_ris(record: Record, source_tag: str | None = None) -> str:
    """Serialize a record back to RIS text. Optional `N1 - source:<tag>` provenance."""
    lines = [f"{tag}  - {value}" for tag, value in record]
    if source_tag:
        lines.append(f"N1  - source:{source_tag}")
    lines.append("ER  - ")
    lines.append("")
    return "\n".join(lines)


def write_ris(records: list[tuple[str | None, Record]], output_path: str | Path) -> None:
    """Write `(source_tag, record)` pairs to a RIS file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for source_tag, record in records:
            f.write(record_to_ris(record, source_tag))
