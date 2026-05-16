import pytest
from ai_providers.base import AIProvider


def test_ai_provider_is_abstract():
    class Bad(AIProvider):
        pass

    with pytest.raises(TypeError):
        Bad()
