"""VOSviewer integration + Louvain community detection.

Reads Pajek `.net` files exported from VOSviewer, runs Louvain community
detection, and produces per-cluster summary statistics suitable for the
strategic diagram of Callon et al. (1991): centrality x density.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

try:
    import community as community_louvain  # python-louvain
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "python-louvain is required. Install with: pip install python-louvain"
    ) from exc


@dataclass
class ClusterStats:
    cluster_id: int
    size: int
    top_labels: list[str]
    centrality: float  # mean degree centrality of cluster nodes
    density: float  # internal edge density


def load_pajek_net(filepath: str | Path) -> nx.Graph:
    """Load a VOSviewer-exported Pajek .net file into a NetworkX graph.

    Supports `*Vertices` blocks with `id "label"` and `*Edges` / `*Arcs`
    blocks with optional weights.
    """
    G = nx.Graph()
    section = None
    with open(filepath, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            low = line.lower()
            if low.startswith("*vertices"):
                section = "vertices"
                continue
            if low.startswith("*edges") or low.startswith("*arcs"):
                section = "edges"
                continue
            if section == "vertices":
                m = re.match(r'(\d+)\s+"([^"]+)"', line)
                if m:
                    G.add_node(int(m.group(1)), label=m.group(2))
            elif section == "edges":
                parts = line.split()
                if len(parts) >= 2:
                    weight = float(parts[2]) if len(parts) >= 3 else 1.0
                    G.add_edge(int(parts[0]), int(parts[1]), weight=weight)
    return G


def run_louvain(G: nx.Graph, resolution: float = 1.0, seed: int = 42) -> tuple[dict[int, int], float]:
    """Run Louvain community detection. Returns `(partition, modularity)`."""
    partition = community_louvain.best_partition(
        G, weight="weight", resolution=resolution, random_state=seed
    )
    modularity = community_louvain.modularity(partition, G, weight="weight")
    return partition, modularity


def cluster_summary(
    G: nx.Graph,
    partition: dict[int, int],
    top_n_labels: int = 8,
) -> list[ClusterStats]:
    """Produce per-cluster statistics for a strategic diagram."""
    nodes_by_cluster: dict[int, list[int]] = defaultdict(list)
    for node, cid in partition.items():
        nodes_by_cluster[cid].append(node)

    deg_cent = nx.degree_centrality(G)
    out: list[ClusterStats] = []
    for cid, nodes in sorted(nodes_by_cluster.items()):
        sub = G.subgraph(nodes)
        size = sub.number_of_nodes()
        density = 0.0 if size < 2 else nx.density(sub)
        centrality = sum(deg_cent.get(n, 0) for n in nodes) / max(size, 1)
        labels = [G.nodes[n].get("label", str(n)) for n in nodes]
        # Top labels by node degree as a quick "what is this cluster about" hint
        top = sorted(nodes, key=lambda n: G.degree(n, weight="weight"), reverse=True)[:top_n_labels]
        out.append(
            ClusterStats(
                cluster_id=cid,
                size=size,
                top_labels=[G.nodes[n].get("label", str(n)) for n in top] or labels[:top_n_labels],
                centrality=centrality,
                density=density,
            )
        )
    return out
