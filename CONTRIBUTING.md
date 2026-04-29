# Contributing

Thanks for considering a contribution. PRISMA is small on purpose; we'd
rather merge a tight PR than a large one.

## Setup

```bash
git clone https://github.com/Proportione/PRISMA.git
cd PRISMA
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,streamlit]"
```

## Before opening a PR

```bash
pytest -q
ruff check src/ tests/
```

## What we tend to merge

- Bug fixes with a regression test.
- New or improved YAML rule sets / taxonomies in `examples/`.
- Documentation, especially in `docs/methodology.md`.
- Performance improvements with a before/after benchmark.

## What we tend to push back on

- Adding heavy dependencies for niche features.
- Domain-specific logic baked into `src/prisma/` — prefer a YAML rule set or
  taxonomy in `examples/` so other domains stay first-class.
- Changes that break the CLI surface without a deprecation note.

## Reporting issues

Please include:

- `prisma --version` output
- A minimal failing example (RIS snippet, YAML rules, or PDF if non-confidential)
- The expected vs. actual behaviour
