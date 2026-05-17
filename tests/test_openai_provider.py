"""Tests for OpenAIProvider — JSON parsing, fallback, and response handling."""

from unittest.mock import MagicMock, patch

import pytest

from ai_providers.openai_provider import OpenAIProvider


def _make_provider(mock_openai: MagicMock, monkeypatch, response_content: str) -> OpenAIProvider:
    """Helper: set up a patched OpenAIProvider with a fixed response string."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=response_content))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    return OpenAIProvider()


@patch("ai_providers.openai_provider.OpenAI")
def test_parses_clean_json(mock_openai, monkeypatch) -> None:
    provider = _make_provider(
        mock_openai,
        monkeypatch,
        '{"title": "Trace", "author_first": "Patricia", "author_last": "Cornwell", '
        '"series": "Kay Scarpetta", "series_number": 13}',
    )
    result = provider.identify_book("Trace.epub", {}, "sample text")

    assert result["title"] == "Trace"
    assert result["author_last"] == "Cornwell"
    assert result["series_number"] == 13


@patch("ai_providers.openai_provider.OpenAI")
def test_parses_json_wrapped_in_markdown(mock_openai, monkeypatch) -> None:
    """Model sometimes wraps JSON in ```json fences — parser must handle it."""
    provider = _make_provider(
        mock_openai,
        monkeypatch,
        '```json\n{"title": "T", "author_first": null, "author_last": null, '
        '"series": null, "series_number": null}\n```',
    )
    result = provider.identify_book("T.epub", {}, "")
    assert result["title"] == "T"


@patch("ai_providers.openai_provider.OpenAI")
def test_all_keys_present_on_partial_response(mock_openai, monkeypatch) -> None:
    """Every required key must be present even if the model omits some."""
    provider = _make_provider(mock_openai, monkeypatch, '{"title": "Only Title"}')
    result = provider.identify_book("book.epub", {}, "")

    for key in ["title", "author_first", "author_last", "series", "series_number"]:
        assert key in result


@patch("ai_providers.openai_provider.OpenAI")
def test_returns_empty_dict_defaults_on_garbage_response(mock_openai, monkeypatch) -> None:
    provider = _make_provider(mock_openai, monkeypatch, "Sorry, I cannot help with that.")
    result = provider.identify_book("book.epub", {}, "")
    # Should not raise; all keys present with None defaults
    assert result.get("title") is None


@patch("ai_providers.openai_provider.OpenAI")
def test_raises_on_missing_api_key(mock_openai, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import importlib, config, ai_providers.openai_provider as oai
    importlib.reload(config)
    importlib.reload(oai)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        oai.OpenAIProvider()
