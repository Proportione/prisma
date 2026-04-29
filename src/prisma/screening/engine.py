"""Generic, reproducible title-abstract screening engine.

Two-tier rule system:

  Tier 1 — Hard exclusion: any matching rule excludes the record. Useful for
           ruling out known out-of-scope topics (e.g. medical when reviewing
           business outcomes).

  Tier 2 — Positive signal: the record must match at least one rule from each
           required group (e.g. one "digital signal" rule AND one "business
           KPI" rule AND one "empirical method" rule). Configurable via
           `inclusion.require_all_of`.

Rules are defined in YAML (see `examples/screening_rules.yaml`) so that any
domain can be encoded without changing code. Every decision is traceable to
the specific rule(s) that fired.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from prisma.ingest.ris_io import get_field, parse_ris


class Decision(str, Enum):
    EXCLUDE = "exclude"
    INCLUDE = "include"
    MAYBE = "maybe"


@dataclass
class Rule:
    rule_id: str
    code: str
    description: str
    pattern: re.Pattern
    search_in: str  # "title" | "abstract" | "both"

    def matches(self, title: str, abstract: str) -> str | None:
        haystack = {
            "title": title,
            "abstract": abstract,
            "both": f"{title}\n{abstract}",
        }[self.search_in]
        m = self.pattern.search(haystack)
        return m.group(0) if m else None


@dataclass
class RuleGroup:
    name: str
    description: str
    rules: list[Rule] = field(default_factory=list)


@dataclass
class RuleSet:
    name: str
    description: str
    exclusion: list[Rule] = field(default_factory=list)
    inclusion_groups: dict[str, RuleGroup] = field(default_factory=dict)
    require_all_of: list[str] = field(default_factory=list)


@dataclass
class ScreeningResult:
    record_id: str
    title: str
    decision: Decision
    fired_exclusion: list[tuple[str, str]] = field(default_factory=list)
    fired_inclusion: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    missing_groups: list[str] = field(default_factory=list)


def _compile_rule(d: dict[str, Any]) -> Rule:
    return Rule(
        rule_id=d["id"],
        code=d.get("code", ""),
        description=d.get("description", ""),
        pattern=re.compile(d["pattern"], re.IGNORECASE),
        search_in=d.get("search_in", "both"),
    )


def load_rules(yaml_path: str | Path) -> RuleSet:
    """Load a screening RuleSet from a YAML file."""
    with open(yaml_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    rs = RuleSet(
        name=spec.get("name", "ruleset"),
        description=spec.get("description", ""),
        require_all_of=spec.get("inclusion", {}).get("require_all_of", []),
    )
    for d in spec.get("exclusion", []):
        rs.exclusion.append(_compile_rule(d))
    for gname, gdef in spec.get("inclusion", {}).get("groups", {}).items():
        group = RuleGroup(name=gname, description=gdef.get("description", ""))
        for d in gdef.get("rules", []):
            group.rules.append(_compile_rule(d))
        rs.inclusion_groups[gname] = group
    return rs


def screen_record(record_id: str, title: str, abstract: str, ruleset: RuleSet) -> ScreeningResult:
    """Apply the full ruleset to a single record."""
    result = ScreeningResult(record_id=record_id, title=title, decision=Decision.MAYBE)

    for rule in ruleset.exclusion:
        match = rule.matches(title, abstract)
        if match:
            result.fired_exclusion.append((rule.rule_id, match))
    if result.fired_exclusion:
        result.decision = Decision.EXCLUDE
        return result

    for gname, group in ruleset.inclusion_groups.items():
        fired = []
        for rule in group.rules:
            match = rule.matches(title, abstract)
            if match:
                fired.append((rule.rule_id, match))
        result.fired_inclusion[gname] = fired

    missing = [g for g in ruleset.require_all_of if not result.fired_inclusion.get(g)]
    if missing:
        result.missing_groups = missing
        result.decision = Decision.MAYBE if len(missing) <= 1 else Decision.EXCLUDE
    else:
        result.decision = Decision.INCLUDE
    return result


def screen_records(
    ris_path: str | Path,
    ruleset: RuleSet,
    output_dir: str | Path | None = None,
) -> list[ScreeningResult]:
    """Screen all records in a RIS file. Optionally write CSV outputs."""
    records = parse_ris(ris_path)
    results: list[ScreeningResult] = []
    for i, rec in enumerate(records):
        rid = get_field(rec, "DO") or get_field(rec, "ID") or f"rec-{i:05d}"
        title = get_field(rec, "TI") or get_field(rec, "T1")
        abstract = get_field(rec, "AB")
        results.append(screen_record(rid, title, abstract, ruleset))

    if output_dir:
        _write_outputs(results, Path(output_dir))
    return results


def _write_outputs(results: list[ScreeningResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    decisions_path = output_dir / "screening-decisions.csv"
    with open(decisions_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "decision", "title", "exclusion_rules", "inclusion_groups_fired", "missing_groups"])
        for r in results:
            w.writerow(
                [
                    r.record_id,
                    r.decision.value,
                    r.title,
                    "; ".join(rid for rid, _ in r.fired_exclusion),
                    "; ".join(g for g, fired in r.fired_inclusion.items() if fired),
                    "; ".join(r.missing_groups),
                ]
            )

    audit_path = output_dir / "screening-audit-log.csv"
    with open(audit_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "kind", "rule_id", "match"])
        for r in results:
            for rid, match in r.fired_exclusion:
                w.writerow([r.record_id, "exclusion", rid, match])
            for group, fired in r.fired_inclusion.items():
                for rid, match in fired:
                    w.writerow([r.record_id, f"inclusion:{group}", rid, match])
