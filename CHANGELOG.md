# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); the project uses semantic versioning.

## [0.2.0] - 2026-06-29

### Added
- `prisma.viz.publication_growth` — review-agnostic publication-year distribution
  bar chart. Accepts a `{year: count}` mapping or a raw iterable of years, with
  optional growth-phase shading and peak-year annotation.
- `prisma.viz.cooccurrence_network` — publication-quality renderer for bibliometric
  networks (keyword co-occurrence, co-authorship, country collaboration). Sizes nodes
  by weighted degree (or a `weight` node attribute), colours them from a Louvain
  `partition` (see `bibliometrics.cluster.run_louvain`), labels the most connected
  nodes, and falls back from Kamada–Kawai to a spring layout when SciPy is absent.
- Smoke tests for the new viz helpers (`tests/test_viz.py`).

## [0.1.0]

- Initial release: OpenAlex ingestion, cross-source deduplication, two-tier
  title–abstract screening, PyMuPDF extraction, MMAT 2018 scoring, PRISMA 2020 flow
  diagrams, and bibliometric clustering with VOSviewer integration.
