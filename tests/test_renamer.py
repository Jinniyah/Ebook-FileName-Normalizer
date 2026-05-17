"""Tests for renamer.py — filename building, sanitization, and rename logic."""

import os

import pytest

from renamer import FILENAME_PATTERN, build_filename, rename_file, safe_filename


# ---------------------------------------------------------------------------
# safe_filename
# ---------------------------------------------------------------------------


def test_safe_filename_strips_illegal_chars() -> None:
    # All Windows-illegal characters should be replaced with an em dash
    result = safe_filename('A:B*C?"D<>E|F\\G/H')
    assert ":" not in result
    assert "*" not in result
    assert "?" not in result
    assert '"' not in result
    assert "<" not in result
    assert ">" not in result
    assert "|" not in result


def test_safe_filename_strips_trailing_dot_and_space() -> None:
    assert safe_filename("Book Title. ") == "Book Title."
    # rstrip only removes trailing, not leading
    assert safe_filename(" Book") == " Book"


# ---------------------------------------------------------------------------
# build_filename
# ---------------------------------------------------------------------------


def test_build_filename_with_series() -> None:
    meta = {
        "author_last": "Doe",
        "author_first": "Jane",
        "series": "My Series",
        "series_number": 3,
        "title": "The Book",
    }
    assert build_filename(meta) == "Doe, Jane — My Series #03 — The Book.epub"


def test_build_filename_without_series() -> None:
    meta = {
        "author_last": "Doe",
        "author_first": "Jane",
        "title": "Standalone Novel",
    }
    assert build_filename(meta) == "Doe, Jane — Standalone Novel.epub"


def test_build_filename_series_without_number() -> None:
    meta = {
        "author_last": "Doe",
        "author_first": "Jane",
        "series": "Orphan Series",
        "series_number": None,
        "title": "Unknown Position",
    }
    assert build_filename(meta) == "Doe, Jane — Orphan Series #ZZ — Unknown Position.epub"


def test_build_filename_missing_author_fields() -> None:
    meta = {"title": "X"}
    result = build_filename(meta)
    assert result.startswith("Unknown, ")
    assert result.endswith("X.epub")


def test_build_filename_zero_pads_series_number() -> None:
    meta = {
        "author_last": "Smith",
        "author_first": "Bob",
        "series": "S",
        "series_number": 1,
        "title": "T",
    }
    assert "#01" in build_filename(meta)


# ---------------------------------------------------------------------------
# FILENAME_PATTERN — already-normalized detection
# ---------------------------------------------------------------------------


def test_pattern_matches_series_format() -> None:
    name = "Cornwell, Patricia — Kay Scarpetta #13 — Trace.epub"
    assert FILENAME_PATTERN.match(name)


def test_pattern_matches_standalone_format() -> None:
    name = "Doe, Jane — Standalone Novel.epub"
    assert FILENAME_PATTERN.match(name)


def test_pattern_rejects_raw_filename() -> None:
    name = "Trace_ Scarpetta (Book 13) (Kay Scarpetta)_nodrm.epub"
    assert not FILENAME_PATTERN.match(name)


# ---------------------------------------------------------------------------
# rename_file
# ---------------------------------------------------------------------------


def test_rename_file_succeeds(tmp_path: pytest.TempPathFactory) -> None:
    old = tmp_path / "old.epub"
    old.write_text("data")

    new_path = rename_file(str(old), "new.epub")

    assert new_path is not None
    assert os.path.exists(new_path)
    assert not os.path.exists(old)


def test_rename_file_returns_none_on_conflict(tmp_path: pytest.TempPathFactory) -> None:
    old = tmp_path / "old.epub"
    old.write_text("data")
    (tmp_path / "new.epub").write_text("already here")

    result = rename_file(str(old), "new.epub")

    assert result is None
    assert os.path.exists(old)  # original untouched
