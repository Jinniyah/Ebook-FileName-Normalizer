from typing import Any, Dict

from .base import AIProvider


class NullProvider(AIProvider):
    """Fallback provider used when no API key is available.

    Returns whatever metadata was already embedded in the EPUB without
    making any external calls.  Useful for offline use or testing the
    pipeline without incurring API costs.
    """

    def identify_book(
        self,
        filename: str,
        metadata: Dict[str, Any],
        text_sample: str,
    ) -> Dict[str, Any]:
        return {
            "title": metadata.get("title"),
            "author_first": None,
            "author_last": None,
            "series": None,
            "series_number": None,
        }
