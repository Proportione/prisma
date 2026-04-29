"""MMAT 2018 (Hong et al.) — Mixed Methods Appraisal Tool.

Implements semi-automated heuristic scoring for the **Quantitative Descriptive**
criteria (Q1–Q5). Every assessment is flagged as `auto` and meant to be
reviewed by a human; aim for inter-rater Cohen's kappa >= 0.80.

Reference:
  Hong, Q.N., et al. (2018). The Mixed Methods Appraisal Tool (MMAT)
  version 2018 for information professionals and researchers.
  *Education for Information*, 34(4), 285-291.
  https://doi.org/10.3233/EFI-180221

This module is not affiliated with or endorsed by the MMAT authors.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class Score(str, Enum):
    YES = "Yes"
    NO = "No"
    CANT_TELL = "Can't tell"


class QualityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class MMATCriterion:
    """A single MMAT question with its heuristic indicators."""

    code: str
    question: str
    indicators: list[str] = field(default_factory=list)
    min_for_yes: int = 1
    min_for_cant_tell: int = 0

    def assess(self, text: str) -> tuple[Score, list[str]]:
        text_l = text.lower()
        matched: list[str] = []
        for ind in self.indicators:
            m = re.search(ind, text_l)
            if m:
                matched.append(m.group(0)[:80])
        if len(matched) >= self.min_for_yes:
            return Score.YES, matched
        if len(matched) >= self.min_for_cant_tell:
            return Score.CANT_TELL, matched
        return Score.NO, matched


# Reference rule set — Quantitative Descriptive (most common for SLR/meta-analysis).
MMAT_DESCRIPTIVE_HEURISTICS: list[MMATCriterion] = [
    MMATCriterion(
        code="Q1",
        question="Is the research question clear?",
        indicators=[
            r"research\s*question",
            r"aim\s*(?:of\s*)?(?:this|the)\s*(?:study|paper|research)",
            r"objective\s*(?:of\s*)?(?:this|the)\s*(?:study|paper|research)",
            r"purpose\s*(?:of\s*)?(?:this|the)\s*(?:study|paper|research)",
            r"this\s*(?:study|paper|research)\s*(?:aims|seeks|investigates|examines)",
            r"hypothesis|hypotheses",
        ],
        min_for_yes=1,
    ),
    MMATCriterion(
        code="Q2",
        question="Does the collected data allow to address the research question?",
        indicators=[
            r"data\s*(?:was|were|is|are)\s*(?:collected|obtained|gathered|retrieved)",
            r"dataset|data\s*set",
            r"sample\s*(?:period|size|consists|includes)",
            r"(?:daily|weekly|monthly|quarterly|annual)\s*(?:data|observations)",
            r"time\s*series",
            r"panel\s*data",
        ],
        min_for_yes=1,
    ),
    MMATCriterion(
        code="Q3",
        question="Is the measurement appropriate?",
        indicators=[
            r"methodology|method(?:ological)?\s*(?:section|approach|framework)",
            r"model\s*(?:specification|estimation|selection)",
            r"(?:empirical|econometric|statistical|machine\s*learning)\s*(?:analysis|approach|model)",
            r"(?:train|test|validation)\s*(?:set|sample|split)",
            r"(?:dependent|independent|explanatory)\s*variable",
            r"robustness\s*(?:check|test|analysis)",
        ],
        min_for_yes=1,
    ),
    MMATCriterion(
        code="Q4",
        question="Is the risk of nonresponse bias low?",
        indicators=[
            r"\b\d{2,}\s*(?:observations|data\s*points|records|samples)",
            r"(?:sample|dataset)\s*(?:of|contains|includes)\s*\d{2,}",
            r"\bn\s*=\s*\d{2,}",
            r"(19\d{2}|20[0-2]\d)\s*[-–—to]+\s*(19\d{2}|20[0-2]\d)",
            r"limitation",
            r"generali[sz]ability",
        ],
        min_for_yes=1,
    ),
    MMATCriterion(
        code="Q5",
        question="Is the statistical analysis appropriate to answer the research question?",
        indicators=[
            r"result(?:s)?\s*(?:section|show|indicate|suggest|reveal|demonstrate)",
            r"(?:table|figure)\s*\d",
            r"(?:statistically|significantly)\s*(?:significant|positive|negative)",
            r"p[\s-]*value|p\s*[<>=]\s*0\.\d",
            r"(?:coefficient|estimate)\s*(?:is|are)\s*(?:significant|positive|negative)",
            r"(?:our|the|these)\s*(?:results|findings)\s*(?:suggest|indicate|show|support)",
            r"r[²2]\s*[=:]\s*0\.\d",
        ],
        min_for_yes=2,
        min_for_cant_tell=1,
    ),
]


@dataclass
class MMATAssessment:
    record_id: str
    scores: dict[str, Score] = field(default_factory=dict)
    matched: dict[str, list[str]] = field(default_factory=dict)
    total: float = 0.0
    level: QualityLevel = QualityLevel.LOW
    notes: str = ""


def score_to_num(score: Score) -> float:
    """Yes -> 1.0, Can't tell -> 0.5, No -> 0.0."""
    return {Score.YES: 1.0, Score.CANT_TELL: 0.5, Score.NO: 0.0}[score]


def quality_level(total: float) -> QualityLevel:
    """High >= 4.5, Medium >= 3.0, else Low."""
    if total >= 4.5:
        return QualityLevel.HIGH
    if total >= 3.0:
        return QualityLevel.MEDIUM
    return QualityLevel.LOW


def assess_text(
    record_id: str,
    text: str,
    criteria: list[MMATCriterion] | None = None,
) -> MMATAssessment:
    """Run all criteria against a full-text string. Defaults to the
    quantitative-descriptive heuristics."""
    criteria = criteria or MMAT_DESCRIPTIVE_HEURISTICS
    a = MMATAssessment(record_id=record_id)
    for c in criteria:
        score, matched = c.assess(text)
        a.scores[c.code] = score
        a.matched[c.code] = matched
    a.total = sum(score_to_num(s) for s in a.scores.values())
    a.level = quality_level(a.total)
    return a
