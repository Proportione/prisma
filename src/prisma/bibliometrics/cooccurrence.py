"""Keyword (or any item) co-occurrence matrix from a corpus."""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

import numpy as np


def build_cooccurrence_matrix(
    documents: Iterable[Iterable[str]],
    min_count: int = 5,
    normalize: str | None = None,
) -> tuple[list[str], np.ndarray]:
    """Build a square co-occurrence matrix from a list of token lists.

    Args:
        documents: iterable of token lists (e.g., keywords per paper).
                   Tokens are lowercased and stripped before counting.
        min_count: drop tokens that appear in fewer than this many docs.
        normalize: None | "association" (Eck & Waltman 2009 association strength).

    Returns:
        `(vocab, matrix)` where `vocab[i]` corresponds to row/column i.
    """
    docs = [[t.strip().lower() for t in d if t and t.strip()] for d in documents]
    docs = [list(set(d)) for d in docs]  # binary doc presence

    counts = Counter(t for d in docs for t in d)
    vocab = [t for t, c in counts.items() if c >= min_count]
    vocab.sort()
    idx = {t: i for i, t in enumerate(vocab)}

    n = len(vocab)
    mat = np.zeros((n, n), dtype=np.int64)
    for d in docs:
        present = [idx[t] for t in d if t in idx]
        for i in present:
            for j in present:
                if i != j:
                    mat[i, j] += 1

    if normalize == "association":
        # Association strength: c_ij / (c_i * c_j) — proportional to PMI.
        diag = np.array([counts[t] for t in vocab])
        denom = np.outer(diag, diag).astype(float)
        denom[denom == 0] = 1
        mat_f = mat.astype(float) / denom
        return vocab, mat_f
    return vocab, mat
