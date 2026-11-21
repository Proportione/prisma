# Changelog

All notable changes to `proportione-prisma` are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `prisma extract` and `prisma quality`: the rows of the output CSV now follow the sorted order of the PDF paths; before, they followed the order the filesystem returned. PDFs whose name starts with a dot, or that sit inside a folder whose name starts with a dot, are no longer processed.

### Fixed

- PRISMA flow diagram: the arrow to "Duplicates removed" now leaves the "Records identified" box instead of pointing back at it.
- `iter_pdfs` no longer returns the `._name.pdf` companions that macOS archives add (also under `__MACOSX/`). They roughly doubled the file count of a folder and are not readable as PDFs.

## [0.2.0] — 2026-11-19

### Added

- `prisma.stats`: reviewer-proof correlation/robustness helpers — `fisher_ci`, `correlation_table` (Pearson + Fisher-z CI + Spearman, overall and per stratum), `partial_correlation`, `bootstrap_ci` (small-cell fragility), `missingness_compare` (selection-bias check via Mann-Whitney), and `mixed_model_icc` (random-intercept clustering + ICC; optional `statsmodels` extra). New `prisma correlate` CLI command. Adds `scipy` as a core dependency and a `[stats]` optional extra. Extracted while hardening the statistical rigour of the 20-60-20 AI-permitted-assessment study (Cuervo, 2026, Universidade de Aveiro).

### Changed

- Zenodo metadata in `.zenodo.json`: ORCID for both authors, related identifiers and extended keywords.

### Fixed

- Streamlit configuration no longer contains a local path.

## [0.1.0] — 2026-04-29

### Added

- Initial public release.
- `prisma.ingest`: OpenAlex search, Unpaywall PDF discovery, RIS I/O, cross-source deduplication (DOI matching plus rapidfuzz title-author similarity).
- `prisma.screening`: two-tier rule engine (hard exclusion + multi-group inclusion), YAML-defined, full audit log.
- `prisma.extraction`: PyMuPDF text extraction, section detection, taxonomy-driven field extraction.
- `prisma.quality`: MMAT 2018 quantitative-descriptive heuristic scoring (Q1–Q5, High/Medium/Low).
- `prisma.reporting`: PRISMA 2020 flow diagram from `PRISMACounts` dataclass.
- `prisma.bibliometrics`: VOSviewer `.net` loader, Louvain communities, co-occurrence matrix.
- `prisma.viz`: matplotlib config with the Proportione brand palette.
- Streamlit demo (`streamlit_app/`) walking through the full pipeline.
- CLI (`prisma`) covering ingest / screen / extract / quality / report.
- Zenodo archive with DOI [`10.5281/zenodo.19883809`](https://doi.org/10.5281/zenodo.19883809).
- Cited in: Pub3-v2 (Cuervo & Marques, 2026, ibero-american bibliometric mapping, accepted, CIDEMA 2025, forthcoming).
