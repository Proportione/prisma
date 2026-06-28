"""Publication-year distribution for a bibliometric corpus.

A small, review-agnostic helper that turns a ``{year: count}`` mapping (or a raw
iterable of publication years) into a clean year-by-year bar chart, with optional
growth-phase shading and peak annotation. Decoupled from any specific corpus so it
can be reused across reviews.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

import matplotlib.pyplot as plt

from prisma.viz.config import PALETTE, SEQUENCE, apply_style

Phase = tuple[int, int, str]


def _as_year_counts(data: Mapping[int, int] | Iterable[int]) -> dict[int, int]:
    """Accept either a {year: count} mapping or an iterable of years."""
    if isinstance(data, Mapping):
        return {int(y): int(c) for y, c in data.items()}
    return {int(y): int(c) for y, c in Counter(int(y) for y in data).items()}


def publication_growth(
    data: Mapping[int, int] | Iterable[int],
    output_path: str | Path,
    *,
    title: str = "Publication-year distribution",
    xlabel: str = "publication year",
    ylabel: str = "publications / year",
    phases: Sequence[Phase] | None = None,
    annotate_peak: bool = True,
    figsize: tuple[float, float] = (11, 5),
) -> Path:
    """Render the year-by-year publication distribution as a bar chart.

    Args:
        data: a ``{year: count}`` mapping or an iterable of publication years.
        output_path: where to write the figure (PNG or any matplotlib format).
        phases: optional ``(start_year, end_year, label)`` bands; bars are coloured
            by the phase they fall in and a legend is drawn. Years outside every
            band keep the primary colour.
        annotate_peak: annotate the single highest year.

    Returns:
        The output path.
    """
    apply_style()
    counts = _as_year_counts(data)
    if not counts:
        raise ValueError("publication_growth: no year data to plot")

    years = list(range(min(counts), max(counts) + 1))
    values = [counts.get(y, 0) for y in years]

    def _colour(year: int) -> str:
        if phases:
            for i, (start, end, _label) in enumerate(phases):
                if start <= year <= end:
                    return SEQUENCE[i % len(SEQUENCE)]
        return PALETTE["primary"]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(years, values, color=[_colour(y) for y in years], edgecolor="white", linewidth=0.6, zorder=3)

    if annotate_peak:
        peak_year = max(counts, key=counts.get)
        ax.annotate(
            f"{peak_year}: {counts[peak_year]}",
            xy=(peak_year, counts[peak_year]),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=PALETTE["text"],
        )

    if phases:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=SEQUENCE[i % len(SEQUENCE)], label=label)
            for i, (_s, _e, label) in enumerate(phases)
        ]
        ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    ax.grid(axis="y", color="#ededed", linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path
