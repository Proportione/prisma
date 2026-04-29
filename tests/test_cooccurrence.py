from prisma.bibliometrics.cooccurrence import build_cooccurrence_matrix


def test_build_cooccurrence_matrix_min_count():
    docs = [
        ["a", "b", "c"],
        ["a", "b"],
        ["a", "c"],
        ["a"],
        ["b"],
    ]
    vocab, mat = build_cooccurrence_matrix(docs, min_count=2)
    assert "a" in vocab and "b" in vocab and "c" in vocab
    i_a, i_b = vocab.index("a"), vocab.index("b")
    assert mat[i_a, i_b] == 2  # docs 0 and 1


def test_build_cooccurrence_matrix_drops_rare_tokens():
    docs = [["a", "rare-once"], ["a", "b"], ["a", "b"]]
    vocab, _ = build_cooccurrence_matrix(docs, min_count=2)
    assert "rare-once" not in vocab
    assert "a" in vocab and "b" in vocab
