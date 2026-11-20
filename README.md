# PRISMA

**A Python toolkit for systematic literature reviews — by [Proportione](https://proportione.com/investigacion).**

[![CI](https://github.com/Proportione/prisma/actions/workflows/ci.yml/badge.svg)](https://github.com/Proportione/prisma/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19883808.svg)](https://doi.org/10.5281/zenodo.19883808)

Covers the full pipeline of a transparent, reproducible SLR: corpus ingestion (OpenAlex), cross-source deduplication, two-tier title-abstract screening with traceable rule sets, full-text extraction with PyMuPDF, MMAT 2018 quality assessment, PRISMA 2020 flow diagrams, and bibliometric clustering with VOSviewer integration.

**¿Hablas español?** Hay una [guía paso a paso para empezar](docs/guia-para-empezar.md), pensada para quien hace su primera revisión sistemática y no programa a diario.

Built and battle-tested while preparing the doctoral thesis of Javier Cuervo (Universidade de Aveiro, DEGEIT) and the journal articles co-authored with Rui Pedro Figueiredo Marques (ISCA-UA, GOVCOPP). Released as open-source so reviewers can audit the methodology and other researchers can reuse the pipeline.

## Why this exists

Most SLR tooling solves *one* step (e.g. screening, or visualisation, or deduplication). Stitching them together usually means brittle glue scripts that nobody else can re-run a year later. PRISMA bundles the steps that we found we needed every single time, in a single installable Python package, with rule sets in YAML so the *what* is decoupled from the *how*.

## Install

```bash
# CLI + library
pip install "git+https://github.com/Proportione/prisma@v0.2.0"

# + Streamlit demo
pip install "proportione-prisma[streamlit] @ git+https://github.com/Proportione/prisma@v0.2.0"
```

The package is not on PyPI yet, so `pip install proportione-prisma` on its own will not find it. Install from the tagged release as shown above.

Python 3.10+. PyMuPDF, pandas, networkx, rapidfuzz, click, pyyaml, plus matplotlib/seaborn for plots.

## Quickstart (5 commands)

```bash
# 1. Build a small corpus from OpenAlex
prisma ingest openalex \
  --query "google trends forecasting" \
  --max 50 \
  --mailto you@example.com \
  --out data/demo.ris

# 2. (Optional) merge multiple sources, deduplicate
prisma ingest dedup \
  -s openalex-A=data/demo.ris \
  -s scopus-A=data/scopus.ris \
  --out data/

# 3. Screen titles + abstracts with a YAML rule set
prisma screen \
  --in data/corpus-deduplicated.ris \
  --rules examples/screening_rules_signal_kpi.yaml \
  --out data/screening/

# 4. Extract structured data from the PDFs you retrieved
prisma extract \
  --pdfs data/pdfs/ \
  --taxonomy examples/extraction_taxonomy_signal_kpi.yaml \
  --out data/extracted.csv

# 5. Score quality (MMAT 2018) and render the PRISMA flow
prisma quality --pdfs data/pdfs/ --out data/mmat.csv
prisma report --counts examples/prisma_counts_demo.json --out reports/prisma-flow.png
```

The Streamlit demo walks through the same pipeline visually:

```bash
streamlit run streamlit_app/Home.py
```

## What's in the box

| Module | What it does | Reused from |
|---|---|---|
| `prisma.ingest` | OpenAlex search · Unpaywall PDF discovery · RIS I/O · cross-source dedup (DOI + rapidfuzz) | Pub1-Fusion, Pub3 |
| `prisma.screening` | Two-tier rule engine (hard exclusion + multi-group inclusion), YAML-defined, full audit log | Pub3 |
| `prisma.extraction` | PyMuPDF text extraction · section detection · taxonomy-driven field extraction | Pub3, Pub3-keywords |
| `prisma.quality` | MMAT 2018 quantitative-descriptive heuristic scoring (Q1–Q5, High/Medium/Low) | Pub3 |
| `prisma.reporting` | PRISMA 2020 flow diagram from `PRISMACounts` dataclass | Pub3 |
| `prisma.bibliometrics` | VOSviewer `.net` loader · Louvain communities (modularity, density, centrality) · co-occurrence matrix | Pub1-Fusion |
| `prisma.stats` | Correlation tables with Fisher-z CIs · partial correlation · bootstrap CIs · missingness comparison · mixed-model ICC (`prisma correlate`) | 20-60-20 study |
| `prisma.viz` | Matplotlib config with the Proportione brand palette | shared |

## What a reviewer or supervisor will ask

**Which version and DOI do I cite?** Cite the version you ran (`prisma --version`). Each release has its own DOI on Zenodo; v0.2.0 is [10.5281/zenodo.24377800](https://doi.org/10.5281/zenodo.24377800). The general DOI [10.5281/zenodo.19883808](https://doi.org/10.5281/zenodo.19883808) always resolves to the latest release and is the one to use when you refer to the toolkit as a whole.

**Can I reproduce a flow diagram from its inputs?** Yes. The diagram is drawn from a small JSON file of counts and nothing else. The repository ships a synthetic example:

```bash
prisma report --counts examples/prisma_counts_demo.json --out reports/prisma-flow.png
```

The same file and the same version give the same figure. Publish the counts file alongside the figure.

**How are duplicates handled, and where in the flow?** Before screening. `prisma ingest dedup` compares records across sources, first by normalised DOI and then by title similarity (rapidfuzz ratio, 92 by default, adjustable with `--threshold`). The first occurrence is kept. The run writes `corpus-dedup-report.md` with the totals and, for the first 50 removed records, the reason and the source of the record each one duplicates, so the decisions can be spot-checked by hand.

**What does it cover of PRISMA 2020, and what not?** It produces the flow diagram for records identified through databases and registers: identification, screening, eligibility, included, with reasons for exclusion at full text. It does not draw the "other methods" branch of the official template, does not fill in the PRISMA 2020 checklist or the PRISMA-S search checklist, and does not register a protocol. Those remain the authors' work.

**Does it replace the reviewers' judgement?** No. Screening applies the rules you write in YAML and logs which rule fired for each record (`screening-decisions.csv`, `screening-audit-log.csv`); borderline records are marked `maybe` for a person to decide. MMAT scores are heuristic and flagged for human review. Dual screening and the resolution of disagreements happen outside the toolkit.

**Licence?** MIT. See [How to cite](#how-to-cite) for the reference.

## Methodology references

- **PRISMA 2020** — Page, M.J. et al. (2021). *BMJ* 372:n71. https://doi.org/10.1136/bmj.n71
- **MMAT 2018** — Hong, Q.N. et al. (2018). *Education for Information* 34:285-291. https://doi.org/10.3233/EFI-180221
- **Case Survey Method** — Larsson, R. (1993). *Academy of Management Journal* 36(6):1515-1546.
- **Bibliometric methods** — Donthu, N. et al. (2021). *Journal of Business Research* 133:285-296.

## How to cite

If this toolkit informs your research, please cite the software:

> Cuervo, J. & Marques, R.P.F. (2026). *PRISMA: A Python Toolkit for Systematic Literature Reviews* (version 0.2.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.19883808

The same reference is in [CITATION.cff](CITATION.cff), which GitHub turns into BibTeX or APA from the "Cite this repository" button. Where applicable, cite also the articles that introduced the rule sets and taxonomies bundled in `examples/`:

> Cuervo, J. & Marques, R.P.F. (2026). *Where search data meets business intelligence: a bibliometric mapping of the Ibero-American research landscape.* (Accepted with minor revisions, CIDEMA 2025 / McGraw Hill; forthcoming.)

## Trademark / endorsement notice

This toolkit helps authors comply with the **PRISMA 2020 reporting standard**. It is *not* affiliated with, endorsed by, or sponsored by the PRISMA Statement Group or the EQUATOR Network. "PRISMA" here refers to the toolkit name; users remain responsible for following the official PRISMA 2020 checklist when reporting.

## Contributing

Issues and PRs welcome. Please run `ruff check src/` and `pytest -q` before submitting.

## Licence

MIT — see [LICENSE](LICENSE). Copyright © 2026 Proportione, LDA.

## About Proportione

[Proportione](https://proportione.com/?utm_source=github&utm_medium=readme&utm_campaign=prisma) is an independent research and engineering firm working on data-driven decision systems and BI. Our research output, including the studies this toolkit was built for, lives at [proportione.com/investigacion](https://proportione.com/investigacion/?utm_source=github&utm_medium=readme&utm_campaign=prisma).

If your organisation needs an evidence review that others can audit and repeat, [write to us](https://proportione.com/contacto/?utm_source=github&utm_medium=readme&utm_campaign=prisma).
