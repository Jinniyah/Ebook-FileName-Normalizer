# 📚 Ebook-Normalizer

> **Local-first, AI-assisted metadata enrichment and filename normalization pipeline for EPUB libraries.**

Ebook-Normalizer scans a folder of `.epub` files, extracts embedded metadata and content samples, enriches missing or malformed fields using a pluggable LLM provider, and renames each file into a consistent, library-sortable format:

```
Lastname, Firstname — Series #01 — Title.epub
Lastname, Firstname — Title.epub
```

Designed for personal ebook libraries with messy, inconsistent filenames from DRM-stripped or downloaded files — normalized once, maintained forever.

---

## ✨ Features

| Feature | Description |
|---|---|
| **EPUB Metadata Extraction** | Reads embedded `DC:title`, `DC:creator`, and `DC:identifier` fields from any valid EPUB file |
| **AI-Assisted Enrichment** | Sends filename + metadata + text sample to an LLM to infer title, author, series, and series number |
| **Pluggable AI Providers** | Abstract `AIProvider` base class with a central registry; ships with OpenAI and a `NullProvider` fallback for offline use |
| **Filename Normalization** | Deterministic, sortable output format with invalid-character sanitization |
| **Dry-Run Mode** | Preview all renames without touching the filesystem — on by default |
| **Idempotent Processing** | JSON state file tracks processed paths; re-runs skip already-handled files; state is flushed after every file |
| **Audit Trail** | Every file action is written to a timestamped CSV for review and rollback planning |
| **Safe Defaults** | `DRY_RUN=true`, `MAX_FILES=50` cap, conflict detection prevents overwrites |
| **CLI Flags** | `--dry-run`, `--live`, `--max-files`, `--reset-state` override `.env` settings per run |

---

## 🏛️ Architecture

```
EPUB Files
    │
    ▼
┌─────────────────┐
│  epub_reader.py │  ← Extract DC metadata + text sample
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  ai_providers/       │  ← Enrich via LLM (strategy pattern)
│    registry.py       │       OpenAI | Null | custom
│    base.py           │
│    openai_provider.py│
│    null_provider.py  │
└────────┬─────────────┘
         │
         ▼
┌─────────────────┐
│   renamer.py    │  ← Build + sanitize normalized filename
└────────┬────────┘
         │
    ┌────┴──────┐
    ▼           ▼
┌──────────┐  ┌──────────────┐
│ state_   │  │ audit_logger │
│ manager  │  │    .py       │
│ .py      │  └──────────────┘
└──────────┘   CSV audit trail
 JSON state
 (flushed each file)
```

`main.py` orchestrates the pipeline. Each module has a single, well-defined responsibility with no circular dependencies.

---

## 📦 Installation

**Prerequisites:** Python 3.11+, an OpenAI API key (optional — the `NullProvider` fallback works without one)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Ebook-Normalizer.git
cd Ebook-Normalizer

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (CMD)
.\.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

Or via Makefile:

```bash
make venv
make install
```

---

## 🔧 Configuration

```bash
cp .env.example .env
# Edit .env with your values
```

```ini
# --- AI Provider ---
AI_PROVIDER=openai          # Supported: openai | null
OPENAI_API_KEY=sk-...       # Leave blank to use NullProvider (offline mode)

# --- Library ---
BOOKS_FOLDER=C:\Users\you\Books   # Path to your EPUB library

# --- Safety ---
DRY_RUN=true                # true = preview only, no files renamed (recommended first run)
MAX_FILES=50                # Hard cap per run — prevents runaway API usage

# --- AI Tuning ---
TEXT_SAMPLE_LENGTH=5000     # Characters of book content sent to the LLM

# --- Storage ---
STATE_FILE=state.json       # Tracks which files have been processed
AUDIT_LOG=audit_log.csv     # Full record of every file action

# --- Debugging ---
DEBUG_AI=false              # true = print raw LLM JSON to stdout
```

> **Security note:** Never commit your `.env` file. It is listed in `.gitignore` by default.

---

## ▶️ Usage

```bash
# Preview proposed renames (no files touched)
python main.py --dry-run

# Apply renames for real
python main.py --live

# Override the per-run file cap
python main.py --live --max-files 100

# Clear state and reprocess everything
python main.py --reset-state --dry-run
```

Or via Makefile:

```bash
make dry-run    # preview
make run        # live rename
```

### Recommended first-run workflow

```bash
# Step 1 — Preview
python main.py --dry-run

# Step 2 — Review audit_log.csv
# Step 3 — Apply
python main.py --live
```

---

## 🧪 Testing

```bash
pytest -v
# or
make test
```

The test suite covers:

- Filename building, sanitization, and `FILENAME_PATTERN` matching (`test_renamer.py`)
- State persistence, reload, and idempotency (`test_state_manager.py`)
- OpenAI provider JSON parsing, fallback, and error handling (`test_openai_provider.py`)
- Provider registry and abstract base class enforcement (`test_ai_provider_base.py`)
- Full pipeline integration with mocked I/O (`test_main.py`)

All external API calls and filesystem writes are mocked — the suite runs fully offline.

---

## 🧹 Linting & Formatting

```bash
# Format code
make format       # black + ruff --fix

# Check without modifying
make lint         # ruff check + black --check

# Type checking
make typecheck    # mypy

# All checks + tests
make check
```

Tool configuration lives in `pyproject.toml`:

- **black** — line length 88, target Python 3.11
- **ruff** — rules E, F, I, B (errors, pyflakes, isort, bugbear)
- **mypy** — strict mode, `ignore_missing_imports = true`

---

## 📁 Project Structure

```
Ebook-Normalizer/
├── ai_providers/               # Pluggable LLM provider layer
│   ├── base.py                 # Abstract AIProvider interface
│   ├── registry.py             # Provider registry — add new providers here
│   ├── openai_provider.py      # OpenAI GPT-4o-mini implementation
│   ├── null_provider.py        # Offline fallback (metadata passthrough)
│   └── __init__.py
├── tests/                      # pytest test suite (fully offline)
│   ├── test_renamer.py
│   ├── test_state_manager.py
│   ├── test_main.py
│   ├── test_openai_provider.py
│   └── test_ai_provider_base.py
├── main.py                     # Pipeline orchestrator + CLI entry point
├── config.py                   # Environment variable loading (dotenv)
├── epub_reader.py              # EPUB metadata + text extraction
├── renamer.py                  # Filename building + sanitization + rename
├── state_manager.py            # JSON state — tracks processed files
├── audit_logger.py             # CSV audit trail writer
├── pyproject.toml              # Tool configuration + project metadata
├── requirements.txt            # Runtime + dev dependencies (pinned)
├── Makefile                    # Developer convenience targets
├── .env.example                # Configuration template
├── DESIGN_DECISIONS.md         # Architecture rationale
├── THREAT_MODEL.md             # STRIDE security analysis
├── CONTRIBUTING.md             # Development setup + extension guide
└── .env                        # Local secrets — NOT committed
```

---

## 🔌 Adding a New AI Provider

The provider system uses a registry pattern — adding a backend requires changes to exactly two files.

**1.** Create `ai_providers/my_provider.py`:

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

**2.** Register it in `ai_providers/registry.py`:

```python
from .my_provider import MyProvider

PROVIDERS = {
    "openai": OpenAIProvider,
    "null":   NullProvider,
    "my_provider": MyProvider,   # ← add this line
}
```

**3.** Set `AI_PROVIDER=my_provider` in `.env`. Done.

---

## 📊 Audit Log Schema

Every file is recorded in `audit_log.csv` regardless of outcome:

| Column | Description |
|---|---|
| `timestamp` | UTC ISO 8601 timestamp of the action |
| `original_filename` | File name before any action |
| `new_filename` | Proposed or applied normalized name |
| `title` | Title resolved by AI / embedded metadata |
| `author_first` | First name |
| `author_last` | Last name |
| `series` | Series name (if detected) |
| `series_number` | Series position (if detected) |
| `ai_used` | `yes` / `no` |
| `renamed` | `yes` / `no` |
| `skipped_reason` | `dry_run` · `already_normalized` · `epub_read_error` · `name_conflict` |

---

## 🛡️ Security & Privacy

See [`THREAT_MODEL.md`](THREAT_MODEL.md) for the full STRIDE analysis. Key points:

- **Local-first** — EPUB files never leave your machine
- **Minimal data exposure** — only truncated text samples are sent to the LLM
- **API key protection** — stored in `.env`, excluded from version control
- **No shell execution** — no `subprocess`, no dynamic code loading
- **Conflict-safe** — renames are skipped if the target filename already exists

---

## 🧠 Design Decisions

See [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md) for rationale on all key architectural choices: provider abstraction, state management, audit log schema, filename format, prompt design, and more.

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development setup and the guide for adding new AI providers.

---

## 📄 License

MIT License — see [`LICENSE.txt`](LICENSE.txt) for details.
