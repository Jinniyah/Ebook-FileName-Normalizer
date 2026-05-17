"""Provider registry — single place to register AI backend implementations.

To add a new provider:
1. Create ``ai_providers/my_provider.py`` implementing ``AIProvider``.
2. Import it here and add an entry to ``PROVIDERS``.
3. Set ``AI_PROVIDER=my_provider`` in ``.env``.

No changes to ``main.py`` or any other module are required.
"""

from typing import Type

from .base import AIProvider
from .null_provider import NullProvider
from .openai_provider import OpenAIProvider

PROVIDERS: dict[str, Type[AIProvider]] = {
    "openai": OpenAIProvider,
    "null": NullProvider,
}


def get_provider(name: str) -> AIProvider:
    """Instantiate and return the named provider.

    Raises ``ValueError`` with a helpful message listing valid choices if
    *name* is not registered.
    """
    cls = PROVIDERS.get(name.lower())
    if cls is None:
        valid = ", ".join(sorted(PROVIDERS))
        raise ValueError(
            f"Unknown AI provider: {name!r}. Valid choices: {valid}"
        )
    return cls()
