# Changelog

All notable changes to `proportione-prisma` are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `prisma.stats`: reviewer-proof correlation/robustness helpers — `fisher_ci`, `correlation_table` (Pearson + Fisher-z CI + Spearman, overall and per stratum), `partial_correlation`, `bootstrap_ci` (small-cell fragility), `missingness_compare` (selection-bias check via Mann-Whitney), and `mixed_model_icc` (random-intercept clustering + ICC; optional `statsmodels` extra). New `prisma correlate` CLI command. Adds `scipy` as a core dependency and a `[stats]` optional extra. Extracted while hardening the statistical rigour of the 20-60-20 AI-permitted-assessment study (Cuervo, 2026, Universidade de Aveiro).
- Pub1-Fusion (Cuervo & Marques, 2026, *From search queries to strategic decisions: a hybrid systematic and bibliometric review of digital signals in business forecasting*) submitted to International Journal of Information Management — citation slot reserved for the next release once the editorial decision lands.

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
- Cited in: Pub3-v2 (Cuervo & Marques, 2026, ibero-american bibliometric mapping, under review at CIDEMA II McGraw Hill).
