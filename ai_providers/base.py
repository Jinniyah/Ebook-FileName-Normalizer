from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProvider(ABC):
    """Abstract base class for AI providers used to identify book metadata."""

    @abstractmethod
    def identify_book(
        self, metadata: Dict[str, Any], text_sample: str
    ) -> Dict[str, Any]:
        """
        Return enriched metadata:
        {
            "title": str | None,
            "author_first": str | None,
            "author_last": str | None,
            "series": str | None,
            "series_number": str | int | None
        }
        """
        raise NotImplementedError
