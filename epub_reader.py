from typing import Dict, Any

from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

from config import TEXT_SAMPLE_LENGTH


def extract_epub_metadata(path: str) -> Dict[str, Any]:
    """Extract basic metadata from an EPUB file."""
    book = epub.read_epub(path)

    title = book.get_metadata("DC", "title")
    author = book.get_metadata("DC", "creator")
    identifier = book.get_metadata("DC", "identifier")

    return {
        "title": title[0][0] if title else None,
        "author": author[0][0] if author else None,
        "identifier": identifier[0][0] if identifier else None,
    }


def extract_text_sample(path: str) -> str:
    """Extract a text sample from the EPUB content."""
    book = epub.read_epub(path)
    text_chunks: list[str] = []
    total_len = 0

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_body_content(), "html.parser")
            chunk = soup.get_text()
            if not chunk:
                continue

            remaining = TEXT_SAMPLE_LENGTH - total_len
            if remaining <= 0:
                break

            text_chunks.append(chunk[:remaining])
            total_len += len(chunk[:remaining])

            if total_len >= TEXT_SAMPLE_LENGTH:
                break

    return "".join(text_chunks)
