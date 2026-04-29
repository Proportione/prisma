"""PRISMA 2020 flow diagram (Page et al. 2021, BMJ 372:n71).

Render a clean, single-figure PRISMA flow with the four standard phases:
Identification, Screening, Eligibility, Included. Counts are passed as a
`PRISMACounts` dataclass so the diagram is decoupled from any specific review.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from prisma.viz.config import PALETTE, apply_style


@dataclass
class PRISMACounts:
    """Counts for each PRISMA 2020 phase. Set fields to None to omit a row."""

    identified_per_source: dict[str, int] = field(default_factory=dict)
    deduplicated: int | None = None
    duplicates_removed: int | None = None
    screened_title_abstract: int | None = None
    excluded_title_abstract: int | None = None
    sought_for_retrieval: int | None = None
    not_retrieved: int | None = None
    assessed_full_text: int | None = None
    excluded_full_text: dict[str, int] = field(default_factory=dict)
    included: int | None = None

    @property
    def total_identified(self) -> int:
        return sum(self.identified_per_source.values())


def render_flow(
    counts: PRISMACounts,
    output_path: str | Path,
    title: str = "PRISMA 2020 flow diagram",
    note: str = "",
) -> Path:
    """Render the PRISMA 2020 flow diagram as PNG (or any matplotlib format)."""
    apply_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 13))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 16)
    ax.axis("off")

    box_main = {
        "boxstyle": "round,pad=0.6",
        "facecolor": "#F5F1EE",
        "edgecolor": PALETTE["primary"],
        "linewidth": 1.5,
    }
    box_excl = {
        "boxstyle": "round,pad=0.5",
        "facecolor": "#FFFFFF",
        "edgecolor": PALETTE["secondary"],
        "linewidth": 1.0,
    }
    box_incl = {
        "boxstyle": "round,pad=0.7",
        "facecolor": "#E8EFE0",
        "edgecolor": PALETTE["accent_olive"],
        "linewidth": 2.5,
    }

    def arrow(x1: float, y1: float, x2: float, y2: float) -> None:
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="->",
                mutation_scale=15,
                color=PALETTE["text"],
                linewidth=1.4,
            )
        )

    ax.text(6, 15.5, title, ha="center", fontsize=14, fontweight="bold", color=PALETTE["primary"])

    # ── Identification
    y = 14.0
    ax.text(2, y, "IDENTIFICATION", ha="left", fontsize=11, fontweight="bold", color=PALETTE["primary"])
    src_text = "\n".join(f"{k}: n = {v}" for k, v in counts.identified_per_source.items()) or "(no sources)"
    ax.text(6, 13.0, f"Records identified\n{src_text}\nTotal: n = {counts.total_identified}",
            ha="center", fontsize=9, bbox=box_main)
    if counts.duplicates_removed:
        ax.text(10, 13.0, f"Duplicates removed\n(n = {counts.duplicates_removed})",
                ha="center", fontsize=9, bbox=box_excl)
        arrow(8.7, 13.0, 7.6, 13.0)

    if counts.deduplicated is not None:
        ax.text(6, 11.3, f"Records after deduplication\n(n = {counts.deduplicated})",
                ha="center", fontsize=10, fontweight="bold", bbox=box_main)
        arrow(6, 12.4, 6, 11.9)

    # ── Screening
    ax.text(2, 10.0, "SCREENING", ha="left", fontsize=11, fontweight="bold", color=PALETTE["primary"])
    if counts.screened_title_abstract is not None:
        ax.text(6, 9.0, f"Records screened\n(title + abstract)\n(n = {counts.screened_title_abstract})",
                ha="center", fontsize=9, bbox=box_main)
        arrow(6, 10.7, 6, 9.7)
    if counts.excluded_title_abstract:
        ax.text(10, 9.0, f"Excluded\n(n = {counts.excluded_title_abstract})",
                ha="center", fontsize=9, bbox=box_excl)
        arrow(7.5, 9.0, 8.7, 9.0)

    # ── Eligibility
    ax.text(2, 7.6, "ELIGIBILITY", ha="left", fontsize=11, fontweight="bold", color=PALETTE["primary"])
    if counts.sought_for_retrieval is not None:
        ax.text(6, 6.6, f"Reports sought for retrieval\n(n = {counts.sought_for_retrieval})",
                ha="center", fontsize=9, bbox=box_main)
        arrow(6, 8.3, 6, 7.3)
    if counts.not_retrieved:
        ax.text(10, 6.6, f"Not retrieved\n(n = {counts.not_retrieved})",
                ha="center", fontsize=9, bbox=box_excl)
        arrow(7.5, 6.6, 8.7, 6.6)
    if counts.assessed_full_text is not None:
        ax.text(6, 4.8, f"Reports assessed for eligibility\n(n = {counts.assessed_full_text})",
                ha="center", fontsize=9, bbox=box_main)
        arrow(6, 6.0, 6, 5.5)
    if counts.excluded_full_text:
        excl_lines = "\n".join(f"· {k}: {v}" for k, v in counts.excluded_full_text.items())
        ax.text(10, 4.8, f"Excluded\n{excl_lines}", ha="center", fontsize=8, bbox=box_excl, va="center")
        arrow(7.5, 4.8, 8.7, 4.8)

    # ── Included
    ax.text(2, 3.2, "INCLUDED", ha="left", fontsize=11, fontweight="bold", color=PALETTE["accent_olive"])
    if counts.included is not None:
        ax.text(6, 2.0, f"Studies included in synthesis\n(n = {counts.included})",
                ha="center", fontsize=11, fontweight="bold", bbox=box_incl)
        arrow(6, 4.2, 6, 2.7)

    if note:
        ax.text(6, 0.3, note, ha="center", fontsize=7, fontstyle="italic", color=PALETTE["text"])

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path
