"""Integration tests for process_folder() in main.py.

All filesystem and AI operations are mocked so the suite runs offline
with no API keys and no real EPUB files.
"""

from unittest.mock import MagicMock, patch

from main import process_folder


MOCK_AI_RESULT = {
    "title": "Trace",
    "author_first": "Patricia",
    "author_last": "Cornwell",
    "series": "Kay Scarpetta",
    "series_number": 13,
}


@patch("main.extract_epub_metadata", return_value={"title": "Trace"})
@patch("main.extract_text_sample", return_value="sample text")
@patch("main.ai")
@patch("main.rename_file", return_value="/books/Cornwell, Patricia — Kay Scarpetta #13 — Trace.epub")
@patch("main.write_audit_row")
@patch("main.mark_processed")
@patch("main.save_state")
@patch("main.load_state", return_value={"processed": []})
def test_process_folder_renames_epub(
    mock_load,
    mock_save,
    mock_mark,
    mock_audit,
    mock_rename,
    mock_ai,
    mock_text,
    mock_meta,
    tmp_path,
) -> None:
    mock_ai.identify_book.return_value = MOCK_AI_RESULT

    epub = tmp_path / "book.epub"
    epub.write_text("fake epub data")

    process_folder(str(tmp_path), dry_run=False, max_files=50)

    mock_ai.identify_book.assert_called_once()
    mock_rename.assert_called_once()
    mock_audit.assert_called()
    mock_mark.assert_called()


@patch("main.extract_epub_metadata", return_value={"title": "Trace"})
@patch("main.extract_text_sample", return_value="sample text")
@patch("main.ai")
@patch("main.rename_file")
@patch("main.write_audit_row")
@patch("main.mark_processed")
@patch("main.save_state")
@patch("main.load_state", return_value={"processed": []})
def test_dry_run_does_not_rename(
    mock_load,
    mock_save,
    mock_mark,
    mock_audit,
    mock_rename,
    mock_ai,
    mock_text,
    mock_meta,
    tmp_path,
) -> None:
    mock_ai.identify_book.return_value = MOCK_AI_RESULT

    epub = tmp_path / "book.epub"
    epub.write_text("fake epub data")

    process_folder(str(tmp_path), dry_run=True, max_files=50)

    mock_rename.assert_not_called()
    mock_audit.assert_called()


@patch("main.extract_epub_metadata", side_effect=Exception("corrupt"))
@patch("main.write_audit_row")
@patch("main.mark_processed")
@patch("main.save_state")
@patch("main.load_state", return_value={"processed": []})
def test_epub_read_error_is_logged_and_skipped(
    mock_load,
    mock_save,
    mock_mark,
    mock_audit,
    mock_meta,
    tmp_path,
) -> None:
    epub = tmp_path / "bad.epub"
    epub.write_text("not a real epub")

    process_folder(str(tmp_path), dry_run=False, max_files=50)

    # Should log the error row and mark processed without crashing
    mock_audit.assert_called_once()
    row = mock_audit.call_args[0][0]
    assert row["skipped_reason"] == "epub_read_error"
    mock_mark.assert_called_once()


@patch("main.write_audit_row")
@patch("main.mark_processed")
@patch("main.save_state")
@patch("main.load_state", return_value={"processed": []})
def test_non_epub_files_are_skipped(
    mock_load,
    mock_save,
    mock_mark,
    mock_audit,
    tmp_path,
) -> None:
    (tmp_path / "notes.txt").write_text("not a book")
    (tmp_path / "cover.jpg").write_bytes(b"\xff")

    process_folder(str(tmp_path), dry_run=False, max_files=50)

    mock_audit.assert_not_called()
    mock_mark.assert_not_called()


@patch("main.extract_epub_metadata", return_value={"title": "T"})
@patch("main.extract_text_sample", return_value="s")
@patch("main.ai")
@patch("main.rename_file", return_value="/new.epub")
@patch("main.write_audit_row")
@patch("main.mark_processed")
@patch("main.save_state")
@patch("main.load_state", return_value={"processed": []})
def test_max_files_stops_processing(
    mock_load,
    mock_save,
    mock_mark,
    mock_audit,
    mock_rename,
    mock_ai,
    mock_text,
    mock_meta,
    tmp_path,
) -> None:
    mock_ai.identify_book.return_value = MOCK_AI_RESULT

    for i in range(5):
        (tmp_path / f"book{i}.epub").write_text("data")

    process_folder(str(tmp_path), dry_run=False, max_files=2)

    assert mock_rename.call_count == 2
