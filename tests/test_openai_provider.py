from unittest.mock import MagicMock, patch
from ai_providers.openai_provider import OpenAIProvider


@patch("ai_providers.openai_provider.OpenAI")
def test_openai_provider_parses_json(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")

    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"title": "A"}'))]
    mock_client.chat.completions.create.return_value = mock_response

    provider = OpenAIProvider()
    result = provider.identify_book({}, "sample")

    assert result["title"] == "A"
    assert "author_first" in result
