"""Streamlit page: bibliometric clustering + co-occurrence demo."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from prisma.bibliometrics.cluster import cluster_summary, load_pajek_net, run_louvain
from prisma.bibliometrics.cooccurrence import build_cooccurrence_matrix
from prisma.viz.config import PALETTE, SEQUENCE, apply_style

st.set_page_config(page_title="Bibliometrics — PRISMA", page_icon="🕸️", layout="wide")

st.markdown('<h1 style="color:#5F322F">Bibliometric analysis</h1>', unsafe_allow_html=True)
st.write(
    "Louvain community detection on a VOSviewer `.net` graph, plus a keyword "
    "co-occurrence matrix from a list of documents."
)

apply_style()

tab_cluster, tab_cooc = st.tabs(["VOSviewer clusters", "Keyword co-occurrence"])

with tab_cluster:
    upload = st.file_uploader(
        "Upload a VOSviewer Pajek .net file (or .net export from network analysis)",
        type=["net"],
        help="Export from VOSviewer: File → Save → .net format.",
    )

    if upload is None:
        st.info(
            "No graph yet. Upload a `.net` file from VOSviewer. The demo below "
            "uses a synthetic network so you can see the output format."
        )
        # Build a synthetic graph for demo
        import networkx as nx

        G = nx.connected_caveman_graph(4, 7)
        G = nx.relabel_nodes(G, {n: int(n) for n in G.nodes})
        for u, v in G.edges():
            G[u][v]["weight"] = 1.0
        for n in G.nodes:
            G.nodes[n]["label"] = f"kw{n:02d}"
    else:
        tmp = Path("/tmp") / "uploaded_graph.net"
        tmp.write_bytes(upload.getvalue())
        G = load_pajek_net(tmp)

    resolution = st.slider("Louvain resolution", 0.5, 2.0, 1.0, 0.1)
    partition, modularity = run_louvain(G, resolution=resolution)
    stats = cluster_summary(G, partition)

    c1, c2, c3 = st.columns(3)
    c1.metric("Nodes", G.number_of_nodes())
    c2.metric("Edges", G.number_of_edges())
    c3.metric("Modularity", f"{modularity:.3f}")

    df = pd.DataFrame(
        [
            {
                "cluster": s.cluster_id,
                "size": s.size,
                "centrality": round(s.centrality, 3),
                "density": round(s.density, 3),
                "top_labels": ", ".join(s.top_labels[:5]),
            }
            for s in stats
        ]
    ).sort_values("size", ascending=False)
    st.dataframe(df, use_container_width=True)

    # Strategic diagram (Callon et al. 1991)
    fig, ax = plt.subplots(figsize=(7, 5))
    sizes = np.array([s.size for s in stats])
    ax.scatter(
        [s.centrality for s in stats],
        [s.density for s in stats],
        s=sizes * 80,
        c=[SEQUENCE[i % len(SEQUENCE)] for i in range(len(stats))],
        edgecolors=PALETTE["text"],
        linewidths=1.2,
        alpha=0.85,
    )
    for s in stats:
        ax.annotate(
            f"C{s.cluster_id}",
            (s.centrality, s.density),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
            color=PALETTE["text"],
        )
    ax.set_xlabel("Centrality (mean degree centrality)")
    ax.set_ylabel("Density (internal edge density)")
    ax.set_title("Strategic diagram (Callon et al., 1991)")
    st.pyplot(fig, clear_figure=True)


with tab_cooc:
    st.write("Provide one document per line, with keywords separated by `;`.")
    default = (
        "google trends; forecasting; tourism; spain\n"
        "google trends; sales; retail; brazil\n"
        "twitter; sentiment; stock returns\n"
        "google trends; forecasting; unemployment; portugal\n"
        "tripadvisor; reviews; hotels; mexico\n"
        "google trends; forecasting; gdp; argentina\n"
        "twitter; sentiment; cryptocurrency\n"
        "wikipedia; pageviews; box office\n"
        "google trends; forecasting; tourism; portugal\n"
    )
    raw = st.text_area("Documents (one per line)", value=default, height=200)
    min_count = st.slider("Min token count", 1, 5, 2)
    docs = [line.split(";") for line in raw.strip().splitlines() if line.strip()]
    vocab, mat = build_cooccurrence_matrix(docs, min_count=min_count)

    if not vocab:
        st.warning("No tokens above min_count. Lower the threshold or add more docs.")
    else:
        st.caption(f"Vocab size: {len(vocab)} terms")
        df = pd.DataFrame(mat, index=vocab, columns=vocab)
        st.dataframe(df, use_container_width=True)

        fig, ax = plt.subplots(figsize=(0.4 * len(vocab) + 2, 0.4 * len(vocab) + 2))
        im = ax.imshow(mat, cmap="OrRd")
        ax.set_xticks(range(len(vocab)))
        ax.set_yticks(range(len(vocab)))
        ax.set_xticklabels(vocab, rotation=45, ha="right")
        ax.set_yticklabels(vocab)
        ax.set_title("Co-occurrence")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        st.pyplot(fig, clear_figure=True)
