"""Tests for the PRISMA flow diagram."""
from matplotlib.patches import FancyArrowPatch

from prisma.reporting import prisma_flow
from prisma.reporting.prisma_flow import PRISMACounts, render_flow


def test_side_arrows_point_away_from_main_column(tmp_path, monkeypatch):
    """Exclusion boxes sit to the right; their arrows must leave the main column."""
    drawn: list[tuple[tuple[float, float], tuple[float, float]]] = []

    class RecordingArrow(FancyArrowPatch):
        def __init__(self, start, end, **kwargs):
            drawn.append((start, end))
            super().__init__(start, end, **kwargs)

    monkeypatch.setattr(prisma_flow, "FancyArrowPatch", RecordingArrow)
    counts = PRISMACounts(
        identified_per_source={"A": 10, "B": 5},
        deduplicated=12,
        duplicates_removed=3,
        screened_title_abstract=12,
        excluded_title_abstract=4,
        sought_for_retrieval=8,
        not_retrieved=1,
        assessed_full_text=7,
        excluded_full_text={"Out of scope": 2},
        included=5,
    )
    render_flow(counts, tmp_path / "flow.png")

    horizontal = [(s, e) for s, e in drawn if s[1] == e[1]]
    assert len(horizontal) >= 4
    for start, end in horizontal:
        assert start[0] < end[0], f"arrow at y={start[1]} points back to the main column"
