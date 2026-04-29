"""Taxonomy-driven field extraction from PDF text.

A taxonomy maps `field_name -> [(pattern, label, priority)]`. For each field,
the engine scans the text and returns the highest-priority label whose pattern
matched, plus the offset and snippet for traceability.

Taxonomies are YAML files in `examples/` so any domain can be expressed
without code changes. See `examples/taxonomies/signal_kpi.yaml` for the
Signal-KPI taxonomy used in Cuervo & Marques (2026).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class FieldPattern:
    pattern: re.Pattern
    label: str
    priority: int = 0


@dataclass
class ExtractionField:
    name: str
    description: str = ""
    patterns: list[FieldPattern] = field(default_factory=list)
    multi: bool = False  # if True, return all matches, not just the best


@dataclass
class ExtractionTaxonomy:
    name: str
    description: str
    fields: dict[str, ExtractionField] = field(default_factory=dict)


def load_taxonomy(yaml_path: str | Path) -> ExtractionTaxonomy:
    """Load an extraction taxonomy from YAML."""
    with open(yaml_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    tax = ExtractionTaxonomy(
        name=spec.get("name", "taxonomy"),
        description=spec.get("description", ""),
    )
    for fname, fdef in spec.get("fields", {}).items():
        ef = ExtractionField(
            name=fname,
            description=fdef.get("description", ""),
            multi=fdef.get("multi", False),
        )
        for p in fdef.get("patterns", []):
            ef.patterns.append(
                FieldPattern(
                    pattern=re.compile(p["pattern"], re.IGNORECASE),
                    label=p["label"],
                    priority=p.get("priority", 0),
                )
            )
        tax.fields[fname] = ef
    return tax


@dataclass
class FieldHit:
    field: str
    label: str
    snippet: str
    offset: int


def extract_field(text: str, ef: ExtractionField) -> list[FieldHit]:
    """Return matching FieldHits for a single field.

    For non-multi fields, only the highest-priority match is returned.
    """
    hits: list[FieldHit] = []
    for fp in ef.patterns:
        for m in fp.pattern.finditer(text):
            snippet = text[max(0, m.start() - 60) : m.end() + 60].replace("\n", " ")
            hits.append(FieldHit(field=ef.name, label=fp.label, snippet=snippet, offset=m.start()))
            if not ef.multi:
                break
    if not ef.multi and hits:
        # keep highest-priority only
        priorities = {fp.label: fp.priority for fp in ef.patterns}
        hits.sort(key=lambda h: priorities.get(h.label, 0), reverse=True)
        return [hits[0]]
    return hits


def extract_record(text: str, taxonomy: ExtractionTaxonomy) -> dict[str, Any]:
    """Apply the full taxonomy to a single document's text.

    Returns a dict keyed by field name. Each value is either a single label
    (str) for non-multi fields, or a list of labels for multi fields. The raw
    FieldHits are stored under the special key `_audit`.
    """
    out: dict[str, Any] = {"_audit": {}}
    for fname, ef in taxonomy.fields.items():
        hits = extract_field(text, ef)
        out["_audit"][fname] = hits
        if not hits:
            out[fname] = None if not ef.multi else []
        elif ef.multi:
            seen = set()
            uniq = []
            for h in hits:
                if h.label not in seen:
                    seen.add(h.label)
                    uniq.append(h.label)
            out[fname] = uniq
        else:
            out[fname] = hits[0].label
    return out
