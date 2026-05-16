from unittest.mock import patch, MagicMock
from main import process_folder


@patch("main.extract_epub_metadata", return_value={"title": "T"})
@patch("main.extract_text_sample", return_value="sample")
@patch("main.ai")
@patch("main.rename_file", return_value="/new.epub")
@patch("main.write_audit_row")
@patch("main.mark_processed")
@patch("main.save_state")
def test_process_folder_basic(
    mock_save,
    mock_mark,
    mock_write,
    mock_rename,
    mock_ai,
    mock_text,
    mock_meta,
    tmp_path,
):
    mock_ai.identify_book.return_value = {
        "title": "T",
        "author_first": "A",
        "author_last": "B",
        "series": "S",
        "series_number": 1,
    }

    epub = tmp_path / "book.epub"
    epub.write_text("data")

    process_folder(str(tmp_path))

    assert mock_ai.identify_book.called
    assert mock_write.called
    assert mock_mark.called
