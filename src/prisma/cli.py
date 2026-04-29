"""PRISMA CLI — `prisma <command>`.

Subcommands
-----------
- ingest openalex   Build a RIS corpus from an OpenAlex search.
- ingest dedup      Cross-source deduplication (DOI + fuzzy title).
- screen            Apply a YAML rule set to a RIS corpus.
- extract           Extract fields from PDFs using a YAML taxonomy.
- quality           MMAT 2018 quality assessment from PDF text.
- report            Render a PRISMA 2020 flow diagram from a JSON counts file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from prisma import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="prisma")
def main() -> None:
    """PRISMA — a research transparency toolkit by Proportione, LDA.

    https://github.com/Proportione/prisma
    """


@main.group()
def ingest() -> None:
    """Build and clean a corpus."""


@ingest.command("openalex")
@click.option("--query", required=True, help="Free-text search expression.")
@click.option("--max", "max_records", type=int, default=200, show_default=True)
@click.option("--mailto", required=True, help="Polite-pool contact email.")
@click.option("--out", "output", required=True, type=click.Path(dir_okay=False))
def ingest_openalex(query: str, max_records: int, mailto: str, output: str) -> None:
    """Search OpenAlex and write a RIS corpus."""
    from prisma.ingest.openalex import openalex_search, work_to_ris

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for w in openalex_search(query, mailto=mailto, max_records=max_records):
            f.write(work_to_ris(w))
            n += 1
    click.echo(f"Wrote {n} records to {out}")


@ingest.command("dedup")
@click.option(
    "--source",
    "-s",
    "sources",
    multiple=True,
    required=True,
    help="LABEL=PATH (repeatable), e.g. -s scopus-A=data/a.ris -s openalex-A=data/oa.ris",
)
@click.option("--out", "output_dir", required=True, type=click.Path(file_okay=False))
@click.option("--basename", default="corpus", show_default=True)
@click.option("--threshold", type=int, default=92, show_default=True, help="Fuzzy title threshold")
def ingest_dedup(sources: tuple[str, ...], output_dir: str, basename: str, threshold: int) -> None:
    """Deduplicate one or more RIS files."""
    from prisma.ingest.dedup import deduplicate, write_outputs

    parsed: dict[str, str] = {}
    for s in sources:
        if "=" not in s:
            raise click.UsageError(f"Source must be LABEL=PATH, got: {s}")
        label, path = s.split("=", 1)
        parsed[label] = path

    result = deduplicate(parsed, fuzzy_threshold=threshold)
    write_outputs(result, output_dir, basename=basename)
    click.echo(
        f"Total raw: {result.raw_total} | unique: {len(result.unique)} | "
        f"duplicates: {len(result.duplicates)}"
    )


@main.command()
@click.option("--in", "ris_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--rules", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--out", "output_dir", required=True, type=click.Path(file_okay=False))
def screen(ris_path: str, rules: str, output_dir: str) -> None:
    """Title-abstract screening with a YAML rule set."""
    from collections import Counter

    from prisma.screening.engine import load_rules, screen_records

    ruleset = load_rules(rules)
    results = screen_records(ris_path, ruleset, output_dir=output_dir)
    tally = Counter(r.decision.value for r in results)
    click.echo(f"Total: {len(results)} | " + " | ".join(f"{k}: {v}" for k, v in tally.items()))


@main.command()
@click.option("--pdfs", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--taxonomy", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--out", "output_csv", required=True, type=click.Path(dir_okay=False))
@click.option("--max-pages", type=int, default=30, show_default=True)
def extract(pdfs: str, taxonomy: str, output_csv: str, max_pages: int) -> None:
    """Extract taxonomy-defined fields from PDFs."""
    import csv

    from prisma.extraction.patterns import extract_record, load_taxonomy
    from prisma.extraction.pdf_text import extract_pdf_text, iter_pdfs

    tax = load_taxonomy(taxonomy)
    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["pdf", *tax.fields.keys()]
    rows: list[dict] = []
    for p in iter_pdfs(pdfs):
        pages = extract_pdf_text(p, max_pages=max_pages)
        text = "\n".join(pg.text for pg in pages)
        rec = extract_record(text, tax)
        rec.pop("_audit", None)
        rec["pdf"] = p.name
        for k, v in list(rec.items()):
            if isinstance(v, list):
                rec[k] = "; ".join(v)
        rows.append(rec)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    click.echo(f"Extracted {len(rows)} PDFs → {out}")


@main.command()
@click.option("--pdfs", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--out", "output_csv", required=True, type=click.Path(dir_okay=False))
@click.option("--max-pages", type=int, default=30, show_default=True)
def quality(pdfs: str, output_csv: str, max_pages: int) -> None:
    """Score PDFs with MMAT 2018 quantitative descriptive heuristics."""
    import csv

    from prisma.extraction.pdf_text import extract_pdf_text, iter_pdfs
    from prisma.quality.mmat import assess_text

    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for p in iter_pdfs(pdfs):
        pages = extract_pdf_text(p, max_pages=max_pages)
        text = "\n".join(pg.text for pg in pages)
        a = assess_text(p.name, text)
        row = {"pdf": p.name, "total": a.total, "level": a.level.value}
        row.update({code: score.value for code, score in a.scores.items()})
        rows.append(row)

    if not rows:
        click.echo("No PDFs found.", err=True)
        sys.exit(1)
    fieldnames = list(rows[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    click.echo(f"Assessed {len(rows)} PDFs → {out}")


@main.command()
@click.option("--counts", required=True, type=click.Path(exists=True, dir_okay=False),
              help="JSON file matching the PRISMACounts schema.")
@click.option("--out", "output", required=True, type=click.Path(dir_okay=False))
@click.option("--title", default="PRISMA 2020 flow diagram", show_default=True)
@click.option("--note", default="", show_default=False)
def report(counts: str, output: str, title: str, note: str) -> None:
    """Render a PRISMA 2020 flow diagram from a counts JSON."""
    from prisma.reporting.prisma_flow import PRISMACounts, render_flow

    with open(counts, encoding="utf-8") as f:
        data = json.load(f)
    pc = PRISMACounts(**data)
    out_path = render_flow(pc, output, title=title, note=note)
    click.echo(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
