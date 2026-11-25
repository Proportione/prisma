"""Cross-source deduplication for RIS corpora.

Strategy:
  1. Exact DOI match (primary key after normalization).
  2. Fuzzy title match (Levenshtein ratio via rapidfuzz, default >= 92),
     unless both records carry a DOI and the DOIs differ. Such pairs (parts of
     a series, a comment on an article, two versions of one work) are kept
     and listed in `possible_versions` for a reviewer to resolve.

Each unique record is tagged with its source label for provenance. Returns
both the unique set and a structured audit trail of all duplicate decisions.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rapidfuzz import fuzz

from prisma.ingest.ris_io import (
    Record,
    get_all_fields,
    get_field,
    normalize_doi,
    normalize_title,
    parse_ris,
    write_ris,
)

DEFAULT_FUZZY_THRESHOLD = 92


@dataclass
class DedupResult:
    """Outcome of a deduplication run."""

    unique: list[tuple[str, Record]] = field(default_factory=list)
    duplicates: list[dict] = field(default_factory=list)
    possible_versions: list[dict] = field(default_factory=list)
    source_overlap: dict[str, set[str]] = field(default_factory=dict)
    raw_total: int = 0
    fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD


def _record_to_csv_row(record: Record, source_tag: str) -> dict[str, str]:
    title = get_field(record, "TI") or get_field(record, "T1")
    doi = normalize_doi(get_field(record, "DO"))
    year = get_field(record, "PY") or get_field(record, "Y1")
    journal = get_field(record, "JO") or get_field(record, "T2") or get_field(record, "JF")
    return {
        "doi": doi,
        "title": title,
        "year": year[:4] if year else "",
        "journal": journal,
        "authors": "; ".join(get_all_fields(record, "AU")),
        "keywords": "; ".join(get_all_fields(record, "KW")),
        "abstract": get_field(record, "AB")[:500],
        "source": source_tag,
    }


def deduplicate(
    sources: dict[str, str | Path],
    fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD,
) -> DedupResult:
    """Deduplicate a set of RIS files keyed by source label.

    Args:
        sources: mapping `{source_label: ris_filepath}`. Convention:
                 prefix labels with the database (e.g. `scopus-A`, `openalex-B`)
                 to enable cross-database overlap statistics.
        fuzzy_threshold: minimum rapidfuzz ratio to treat two titles as the
                         same record. 92 is conservative; tune via tests.

    Returns:
        DedupResult with unique records, duplicate audit, and overlap stats.
    """
    all_records: list[tuple[str, str, Record]] = []  # (db, label, record)
    for label, filepath in sources.items():
        path = Path(filepath)
        if not path.exists():
            continue
        db = label.split("-", 1)[0]
        for rec in parse_ris(path):
            all_records.append((db, label, rec))

    seen_dois: dict[str, str] = {}
    seen_titles: dict[str, tuple[str, str]] = {}  # title -> (db, doi)
    unique: list[tuple[str, Record]] = []
    duplicates: list[dict] = []
    possible_versions: list[dict] = []
    overlap: dict[str, set[str]] = defaultdict(set)

    for db, label, record in all_records:
        doi = normalize_doi(get_field(record, "DO"))
        title_raw = get_field(record, "TI") or get_field(record, "T1")
        title_norm = normalize_title(title_raw)
        is_dup = False
        reason = ""
        dup_of = ""

        if doi and doi in seen_dois:
            is_dup, reason, dup_of = True, "DOI match", seen_dois[doi]
            overlap[doi].add(db)
        elif title_norm:
            version_of: dict | None = None
            for seen_t, (seen_src, seen_doi) in seen_titles.items():
                ratio = fuzz.ratio(title_norm, seen_t)
                if ratio < fuzzy_threshold:
                    continue
                if doi and seen_doi and doi != seen_doi:
                    if version_of is None:
                        version_of = {
                            "source": label,
                            "title": title_raw[:120],
                            "doi": doi,
                            "doi_of_match": seen_doi,
                            "title_ratio": round(ratio),
                            "match_source": seen_src,
                        }
                    continue
                is_dup, reason, dup_of = True, f"fuzzy title ({ratio:.0f}%)", seen_src
                overlap[title_norm].add(db)
                break
            if not is_dup and version_of is not None:
                possible_versions.append(version_of)

        if is_dup:
            duplicates.append(
                {
                    "source": label,
                    "title": title_raw[:120],
                    "doi": doi,
                    "reason": reason,
                    "duplicate_of": dup_of,
                }
            )
        else:
            unique.append((db, record))
            if doi:
                seen_dois[doi] = db
                overlap[doi].add(db)
            if title_norm:
                seen_titles[title_norm] = (db, doi)
                overlap[title_norm].add(db)

    return DedupResult(
        unique=unique,
        duplicates=duplicates,
        possible_versions=possible_versions,
        source_overlap=dict(overlap),
        raw_total=len(all_records),
        fuzzy_threshold=fuzzy_threshold,
    )


def write_outputs(result: DedupResult, output_dir: str | Path, basename: str = "corpus") -> None:
    """Write the deduplicated corpus to RIS + CSV and a Markdown audit report."""
    import csv

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ris_path = output_dir / f"{basename}-deduplicated.ris"
    write_ris(result.unique, ris_path)

    csv_path = output_dir / f"{basename}-deduplicated.csv"
    fieldnames = ["doi", "title", "year", "journal", "authors", "keywords", "abstract", "source"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for source_tag, record in result.unique:
            writer.writerow(_record_to_csv_row(record, source_tag or ""))

    report_path = output_dir / f"{basename}-dedup-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Deduplication Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Fuzzy threshold**: {result.fuzzy_threshold}% (Levenshtein ratio)\n\n")
        f.write("## Results\n\n")
        f.write(f"- Total raw records: {result.raw_total}\n")
        f.write(f"- Duplicates removed: {len(result.duplicates)}\n")
        f.write(f"- Unique records: {len(result.unique)}\n")
        f.write(f"- Possible versions kept (similar title, different DOI): {len(result.possible_versions)}\n\n")
        if result.duplicates:
            f.write("## Duplicates Detail (first 50)\n\n")
            f.write("| # | Source | Dup of | Reason | Title |\n")
            f.write("|---|--------|--------|--------|-------|\n")
            for i, dup in enumerate(result.duplicates[:50], 1):
                title = dup["title"].replace("|", "\\|")
                f.write(f"| {i} | {dup['source']} | {dup['duplicate_of']} | {dup['reason']} | {title} |\n")
        if result.possible_versions:
            if result.duplicates:
                f.write("\n")
            f.write("## Possible versions kept (similar title, different DOI)\n\n")
            f.write("Not removed. Resolve by hand: a later version of the same work, or a distinct paper.\n\n")
            f.write("| # | Source | DOI | Matched DOI | Ratio | Title |\n")
            f.write("|---|--------|-----|-------------|-------|-------|\n")
            for i, v in enumerate(result.possible_versions, 1):
                title = v["title"].replace("|", "\\|")
                f.write(f"| {i} | {v['source']} | {v['doi']} | {v['doi_of_match']} | {v['title_ratio']}% | {title} |\n")
