# Contributing

Contributions and extensions are welcome.

---

## Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Ebook-Normalizer.git
cd Ebook-Normalizer

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
# PowerShell:
.\.venv\Scripts\Activate.ps1
# CMD:
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 4. Install all dependencies (runtime + dev tools)
pip install -r requirements.txt
```

Or use the Makefile:

```bash
make venv
make install
```

---

## Running Quality Checks

```bash
# Format code
make format

# Lint (ruff + black check)
make lint

# Type check
make typecheck

# Run tests
make test

# All of the above
make check
```

---

## Adding a New AI Provider

1. Create `ai_providers/my_provider.py` implementing `AIProvider`:

```python
from .base import AIProvider
from typing import Any, Dict

class MyProvider(AIProvider):
    def identify_book(
        self,
        filename: str,
        metadata: Dict[str, Any],
        text_sample: str,
    ) -> Dict[str, Any]:
        # Call your LLM here
        return {
            "title": ...,
            "author_first": ...,
            "author_last": ...,
            "series": ...,
            "series_number": ...,
        }
```

2. Register it in `ai_providers/registry.py`:

```python
from .my_provider import MyProvider

PROVIDERS: dict[str, Type[AIProvider]] = {
    "openai": OpenAIProvider,
    "null":   NullProvider,
    "my_provider": MyProvider,   # ← add this line
}
```

3. Set `AI_PROVIDER=my_provider` in your `.env`.

No changes to `main.py` or any other module are required.

---

## Code Style

- **Formatter:** black (line length 88)
- **Linter:** ruff (rules E, F, I, B)
- **Type checker:** mypy (strict mode)
- **Python version:** 3.11+

All CI checks must pass before a PR is merged.
