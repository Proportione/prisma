"""Corpus ingestion: RIS parsing, OpenAlex API, Unpaywall, deduplication."""
from prisma.ingest.dedup import deduplicate
from prisma.ingest.openalex import openalex_search
from prisma.ingest.ris_io import normalize_doi, normalize_title, parse_ris, write_ris
from prisma.ingest.unpaywall import unpaywall_lookup

__all__ = [
    "deduplicate",
    "normalize_doi",
    "normalize_title",
    "openalex_search",
    "parse_ris",
    "unpaywall_lookup",
    "write_ris",
]
