# Signal-KPI taxonomy

A reference taxonomy for SLRs studying how **digital signals** anticipate
**business outcomes (KPIs)**. Used in:

> Cuervo, J. & Marques, R.P.F. (2026). *Where search data meets business
> intelligence: a bibliometric mapping of the Ibero-American research
> landscape.* (Manuscript under review.)

The taxonomy is shipped in two YAML files:

- `examples/screening_rules_signal_kpi.yaml` — title-abstract screening rules
- `examples/extraction_taxonomy_signal_kpi.yaml` — full-text extraction taxonomy

## Signal categories (S1–S4)

| Code | Category | Examples |
|------|----------|----------|
| S1 | Search & query data | Google Trends, Baidu Index, Naver Trend, search volume, query log |
| S2 | Social / sentiment | Twitter / X, Facebook, Weibo, sentiment scores |
| S3 | Reviews & ratings | TripAdvisor, Booking.com, Yelp, Amazon reviews |
| S4 | Web traffic & attention | Wikipedia pageviews, web traffic, app downloads, click-through |

## KPI categories (K1–K5)

| Code | Category | Examples |
|------|----------|----------|
| K1 | Sales & demand | Revenue, sales volume, tourist arrivals, hotel occupancy, RevPAR |
| K2 | Financial markets | Stock returns, exchange rates, cryptocurrencies |
| K3 | Macroeconomic | GDP, unemployment, inflation, consumer confidence |
| K4 | Real estate | House prices, rental prices, property transactions |
| K5 | Other business | Box office, car registrations, energy demand, insurance claims |

## Effect direction

`positive`, `negative`, `mixed`, `null` — extracted from results / discussion
sections via pattern matching on conventional academic phrasing.

## Adapting to other domains

Copy either YAML file, edit the patterns, and pass the new file as `--rules`
(screening) or `--taxonomy` (extraction). The engine does not care about
the specific labels — anything that matches a pattern becomes the value.
