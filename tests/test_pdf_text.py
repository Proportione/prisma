"""Tests for prisma.extraction.pdf_text.iter_pdfs."""

from prisma.extraction.pdf_text import iter_pdfs


def test_iter_pdfs_finds_pdfs_in_subfolders(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "notes.txt").write_text("x")

    assert [p.name for p in iter_pdfs(tmp_path)] == ["a.pdf", "b.pdf"]


def test_iter_pdfs_skips_hidden_and_appledouble_files(tmp_path):
    # macOS tar and zip add a "._name.pdf" companion to every file; it is not a PDF.
    (tmp_path / "a.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "._a.pdf").write_bytes(b"\x00\x05\x16\x07")
    (tmp_path / ".hidden.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "__MACOSX").mkdir()
    (tmp_path / "__MACOSX" / "._a.pdf").write_bytes(b"\x00\x05\x16\x07")

    assert [p.name for p in iter_pdfs(tmp_path)] == ["a.pdf"]


def test_iter_pdfs_skips_pdfs_inside_hidden_folders(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / ".cache").mkdir()
    (tmp_path / ".cache" / "c.pdf").write_bytes(b"%PDF-1.4")

    assert [p.name for p in iter_pdfs(tmp_path)] == ["a.pdf"]


def test_iter_pdfs_returns_paths_in_sorted_order(tmp_path, monkeypatch):
    names = ["c.pdf", "a.pdf", "b.pdf"]
    for name in names:
        (tmp_path / name).write_bytes(b"%PDF-1.4")
    # The filesystem may return any order: force an unsorted one.
    monkeypatch.setattr(
        type(tmp_path), "rglob", lambda self, pattern: iter(self / n for n in names)
    )

    assert [p.name for p in iter_pdfs(tmp_path)] == ["a.pdf", "b.pdf", "c.pdf"]
