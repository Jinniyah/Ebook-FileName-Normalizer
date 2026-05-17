from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProvider(ABC):
    """Abstract base class for AI providers used to identify book metadata.

    All concrete providers must implement :meth:`identify_book` with this
    exact signature so they are interchangeable inside the pipeline.
    """

    @abstractmethod
    def identify_book(
        self,
        filename: str,
        metadata: Dict[str, Any],
        text_sample: str,
    ) -> Dict[str, Any]:
        """Return enriched metadata inferred from the supplied inputs.

        Args:
            filename:    The original filename of the EPUB (useful for
                         inferring series / series number from messy names).
            metadata:    DC metadata extracted directly from the EPUB file.
            text_sample: A truncated plain-text sample of the book content.

        Returns:
            A dict with exactly these keys (values may be ``None``):

            .. code-block:: python

                {
                    "title":         str | None,
                    "author_first":  str | None,
                    "author_last":   str | None,
                    "series":        str | None,
                    "series_number": int | str | None,
                }
        """
        raise NotImplementedError
