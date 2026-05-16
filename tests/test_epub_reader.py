from unittest.mock import MagicMock, patch
from epub_reader import extract_epub_metadata, extract_text_sample


@patch("epub_reader.epub.read_epub")
def test_extract_epub_metadata(mock_read):
    mock_book = MagicMock()
    mock_book.get_metadata.side_effect = [
        [("Title", {})],
        [("Author", {})],
        [("ID", {})],
    ]
    mock_read.return_value = mock_book

    result = extract_epub_metadata("file.epub")
    assert result["title"] == "Title"
    assert result["author"] == "Author"
    assert result["identifier"] == "ID"


@patch("epub_reader.epub.read_epub")
def test_extract_text_sample(mock_read):
    mock_item = MagicMock()
    mock_item.get_type.return_value = 9  # ITEM_DOCUMENT
    mock_item.get_body_content.return_value = b"<p>Hello World</p>"

    mock_book = MagicMock()
    mock_book.get_items.return_value = [mock_item]
    mock_read.return_value = mock_book

    result = extract_text_sample("file.epub")
    assert "Hello World" in result
