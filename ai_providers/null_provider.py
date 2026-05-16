from typing import Any, Dict
from .base import AIProvider


class NullProvider(AIProvider):
    """Fallback provider used when no API key is available."""

    def identify_book(
        self, metadata: Dict[str, Any], text_sample: str
    ) -> Dict[str, Any]:
        # Return metadata unchanged
        return {
            "title": metadata.get("title"),
            "author_first": None,
            "author_last": None,
            "series": None,
            "series_number": None,
        }
