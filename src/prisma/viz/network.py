"""Render a bibliometric network (keyword co-occurrence, co-authorship, …).

Takes a :class:`networkx.Graph` — for example the output of
``bibliometrics.cluster.load_pajek_net`` — and draws a publication-quality figure
with node size by degree (or a ``weight`` node attribute), optional cluster colouring
from a Louvain ``partition`` (see ``bibliometrics.cluster.run_louvain``), and labels
for the most connected nodes. Layout defaults to Kamada–Kawai, which spreads dense
maps more legibly than a spring layout.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from prisma.viz.config import PALETTE, SEQUENCE, apply_style


def cooccurrence_network(
    graph: nx.Graph,
    output_path: str | Path,
    *,
    partition: dict | None = None,
    label_top: int = 15,
    weight_attr: str = "weight",
    title: str = "Co-occurrence network",
    layout: str = "kamada_kawai",
    seed: int = 42,
    figsize: tuple[float, float] = (14, 11),
) -> Path:
    """Render an undirected weighted network as a figure.

    Args:
        graph: a ``networkx.Graph``. Edge weights (``weight_attr``) scale edge width;
            a node ``weight`` attribute, if present, scales node size (degree otherwise).
        partition: optional ``{node: cluster_id}`` mapping used to colour nodes.
        label_top: label the N nodes with the highest weighted degree.
        layout: ``"kamada_kawai"`` (default) or ``"spring"``.

    Returns:
        The output path.
    """
    apply_style()
    if graph.number_of_nodes() == 0:
        raise ValueError("cooccurrence_network: graph has no nodes")

    if layout == "kamada_kawai":
        try:
            pos = nx.kamada_kawai_layout(graph, weight=weight_attr)
        except ImportError:  # kamada_kawai needs scipy; fall back gracefully
            pos = nx.spring_layout(graph, seed=seed, weight=weight_attr)
    else:
        pos = nx.spring_layout(graph, seed=seed, weight=weight_attr)

    degree = dict(graph.degree(weight=weight_attr))
    node_weight = nx.get_node_attributes(graph, "weight")
    sizes = [
        80 + 600 * (node_weight.get(n, degree.get(n, 1)) / (max(node_weight.values()) if node_weight else max(degree.values() or [1])))
        for n in graph.nodes()
    ]
    if partition:
        colours = [SEQUENCE[partition.get(n, 0) % len(SEQUENCE)] for n in graph.nodes()]
    else:
        colours = [PALETTE["primary"]] * graph.number_of_nodes()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")

    edge_w = [0.3 + 1.6 * (graph[u][v].get(weight_attr, 1.0)) for u, v in graph.edges()]
    max_ew = max(edge_w) if edge_w else 1.0
    nx.draw_networkx_edges(
        graph, pos, ax=ax, width=[0.2 + 1.4 * w / max_ew for w in edge_w], edge_color="#cfd4d8", alpha=0.6
    )
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=sizes, node_color=colours, edgecolors="white", linewidths=0.8)

    top_nodes = sorted(degree, key=degree.get, reverse=True)[: max(0, label_top)]
    labels = {n: str(n) for n in top_nodes}
    texts = nx.draw_networkx_labels(graph, pos, labels=labels, ax=ax, font_size=9, font_color=PALETTE["text"])
    try:  # optional: nicer label placement if adjustText is installed
        from adjustText import adjust_text

        adjust_text(list(texts.values()), ax=ax)
    except Exception:
        pass

    ax.set_title(title, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path
