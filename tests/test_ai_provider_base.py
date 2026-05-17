"""Tests for AIProvider abstract base class and the provider registry."""

import pytest

from ai_providers.base import AIProvider
from ai_providers.registry import get_provider, PROVIDERS
from ai_providers.null_provider import NullProvider


# ---------------------------------------------------------------------------
# Abstract base class enforcement
# ---------------------------------------------------------------------------


def test_cannot_instantiate_abstract_provider() -> None:
    with pytest.raises(TypeError):
        AIProvider()  # type: ignore[abstract]


def test_concrete_subclass_must_implement_identify_book() -> None:
    class Incomplete(AIProvider):
        pass  # missing identify_book

    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# NullProvider — smoke test the interface
# ---------------------------------------------------------------------------


def test_null_provider_returns_all_keys() -> None:
    provider = NullProvider()
    result = provider.identify_book("book.epub", {"title": "T"}, "sample")

    for key in ["title", "author_first", "author_last", "series", "series_number"]:
        assert key in result


def test_null_provider_passes_through_title() -> None:
    provider = NullProvider()
    result = provider.identify_book("book.epub", {"title": "My Book"}, "")
    assert result["title"] == "My Book"


def test_null_provider_returns_none_for_missing_metadata() -> None:
    provider = NullProvider()
    result = provider.identify_book("book.epub", {}, "")
    assert result["title"] is None


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_registry_contains_expected_providers() -> None:
    assert "openai" in PROVIDERS
    assert "null" in PROVIDERS


def test_get_provider_null_returns_null_provider() -> None:
    provider = get_provider("null")
    assert isinstance(provider, NullProvider)


def test_get_provider_is_case_insensitive() -> None:
    provider = get_provider("NULL")
    assert isinstance(provider, NullProvider)


def test_get_provider_raises_on_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unknown AI provider"):
        get_provider("nonexistent_provider")
