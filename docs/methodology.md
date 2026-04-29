# Methodology

PRISMA wraps four well-established methodological standards into one Python package.

## Reporting standard — PRISMA 2020

Every flow diagram produced by `prisma report` follows the four-phase
structure of the **PRISMA 2020 statement** (Page et al., 2021):

1. **Identification** — records identified per source and after deduplication.
2. **Screening** — records screened on title and abstract; records excluded.
3. **Eligibility** — reports sought for retrieval, not retrieved, and assessed
   for eligibility, with reasons for exclusion at the full-text stage.
4. **Included** — studies (or reports) included in the synthesis.

> Page, M.J., McKenzie, J.E., Bossuyt, P.M., et al. (2021). *The PRISMA 2020
> statement: an updated guideline for reporting systematic reviews.* BMJ
> 372:n71. https://doi.org/10.1136/bmj.n71

This toolkit helps authors comply with PRISMA 2020 reporting; it is not
affiliated with or endorsed by the PRISMA Statement Group or the EQUATOR
Network.

## Quality assessment — MMAT 2018

`prisma quality` implements heuristic auto-scoring against the **Mixed Methods
Appraisal Tool** version 2018, quantitative-descriptive criteria (Q1–Q5).
Heuristic indicators are documented per criterion in
`src/prisma/quality/mmat.py`. Auto-scores are flagged for human review;
target inter-rater reliability is Cohen's κ ≥ 0.80.

> Hong, Q.N., Fàbregues, S., Bartlett, G., Boardman, F., Cargo, M., Dagenais,
> P., et al. (2018). *The Mixed Methods Appraisal Tool (MMAT) version 2018
> for information professionals and researchers.* Education for Information,
> 34(4), 285-291. https://doi.org/10.3233/EFI-180221

## Coding standard — case survey method

`prisma extract` implements the **case survey** approach (Larsson, 1993):
each included study is treated as a unit of observation, and structured
variables are coded from full text using a pre-specified taxonomy. Patterns
are taxonomy-driven (YAML) and every coding decision carries a snippet
audit trail.

> Larsson, R. (1993). *Case survey methodology: Quantitative analysis of
> patterns across case studies.* Academy of Management Journal, 36(6),
> 1515-1546.

## Bibliometric methods — Donthu et al. (2021)

`prisma.bibliometrics` follows the methodological guidance of Donthu et al.
(2021): co-occurrence and clustering as core techniques for thematic
mapping, with normalisation by association strength (Eck & Waltman, 2009)
when desired. The Louvain algorithm (Blondel et al., 2008) is used for
community detection on VOSviewer-exported networks; cluster characterisation
follows the strategic-diagram framework of Callon et al. (1991).

> Donthu, N., Kumar, S., Mukherjee, D., Pandey, N., & Lim, W.M. (2021). *How
> to conduct a bibliometric analysis: An overview and guidelines.* Journal
> of Business Research, 133, 285-296.
> https://doi.org/10.1016/j.jbusres.2021.04.070

## Reproducibility checklist

When you publish results obtained with PRISMA, share:

- The input corpora (or queries used to build them).
- The exact rule-set / taxonomy YAML files used (commit hash if from a fork).
- The version of `proportione-prisma` (`prisma --version`).
- Any manual decisions logged on top of automated outputs.

Together, these inputs allow a third party to re-execute the pipeline and
obtain the same outputs.
