import os
from renamer import build_filename, safe_filename, rename_file


def test_safe_filename_strips_illegal_chars():
    assert safe_filename('A:B*C?"D<>E|') == "ABCDE"


def test_build_filename_basic():
    meta = {
        "author_last": "Doe",
        "author_first": "Jane",
        "series": "My Series",
        "series_number": 3,
        "title": "The Book",
    }
    result = build_filename(meta)
    assert result == "Doe, Jane — My Series #03 — The Book.epub"


def test_build_filename_missing_fields():
    meta = {"title": "X"}
    result = build_filename(meta)
    assert result.startswith("Unknown,")
    assert result.endswith("X.epub")


def test_rename_file(tmp_path):
    old = tmp_path / "old.epub"
    old.write_text("data")

    new_name = "new.epub"
    new_path = rename_file(str(old), new_name)

    assert new_path is not None
    assert os.path.exists(new_path)
    assert not os.path.exists(old)
