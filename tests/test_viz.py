"""Smoke tests for the review-agnostic viz helpers."""
import matplotlib

matplotlib.use("Agg")

import networkx as nx  # noqa: E402

from prisma.viz import cooccurrence_network, publication_growth


def test_publication_growth_from_mapping(tmp_path):
    out = publication_growth(
        {2018: 10, 2019: 22, 2020: 31, 2021: 28},
        tmp_path / "growth.png",
        phases=[(2018, 2019, "early"), (2020, 2021, "late")],
    )
    assert out.exists() and out.stat().st_size > 0


def test_publication_growth_from_iterable(tmp_path):
    years = [2019, 2019, 2020, 2020, 2020, 2021]
    out = publication_growth(years, tmp_path / "growth2.png")
    assert out.exists() and out.stat().st_size > 0


def test_cooccurrence_network(tmp_path):
    g = nx.Graph()
    g.add_weighted_edges_from([("a", "b", 3.0), ("b", "c", 1.0), ("a", "c", 2.0), ("c", "d", 1.0)])
    partition = {"a": 0, "b": 0, "c": 1, "d": 1}
    out = cooccurrence_network(g, tmp_path / "net.png", partition=partition, label_top=2)
    assert out.exists() and out.stat().st_size > 0
