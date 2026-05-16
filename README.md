# 📚 EPUB Metadata Normalizer
Local‑first, AI‑assisted metadata enrichment pipeline for EPUB libraries.

This project scans a folder of `.epub` files, extracts embedded metadata and text samples, enriches missing fields using an LLM provider, and normalizes filenames into a consistent, sortable format:

Lastname, Firstname — Series #01 — Title.epub

It is designed to be:

- Local‑first (no cloud storage, no uploads)
- LLM‑agnostic (OpenAI today, pluggable providers tomorrow)
- Auditable (CSV logs + JSON state tracking)
- Safe (dry‑run mode, MAX_FILES limit, filename sanitization)
- Enterprise‑grade (tests, linting, type checking, architecture docs)

---

# 🚀 Features

✔ EPUB Metadata Extraction  
✔ AI‑Assisted Metadata Enrichment  
✔ Filename Normalization  
✔ Safety & Auditability  
✔ Tooling & Quality (pytest, ruff, black, mypy)

---

# 🧱 Architecture

EPUB → Metadata Extractor → Text Sampler → AI Provider → Filename Builder → Rename Engine → Audit Log + State Manager

---

# 📦 Installation

1. Clone the repo  
2. Create a virtual environment  
3. Install dependencies  

---

# 🔧 Configuration

Create a `.env` file:

OPENAI_API_KEY=your_openai_key_here  
AI_PROVIDER=openai  
DRY_RUN=true  
MAX_FILES=50  
TEXT_SAMPLE_LENGTH=5000  
STATE_FILE=state.json  
AUDIT_LOG=audit_log.csv  

---

# ▶️ Usage

from main import process_folder  
process_folder(BOOKS_FOLDER)

Or:

python main.py

---

# 🧪 Testing

pytest

---

# 🧹 Linting & Formatting

ruff check .  
black .  
mypy .

---

# 📁 Project Structure

(ai_providers, epub_reader, renamer, state_manager, audit_logger, config, main, tests, docs)

---

# 🧠 Design Decisions

See DESIGN_DECISIONS.md

---

# 🔐 Threat Model

See THREAT_MODEL.md

---

# 🛠 Extending the System

Implement a new AIProvider subclass and update AI_PROVIDER in .env

---

# 📄 License

MIT License.

---

# 🎯 Summary

This project demonstrates:

- Real‑world AI/ML integration  
- Clean, modular Python architecture  
- Enterprise‑grade engineering practices  
- Local‑first, privacy‑respecting design  
- A fully tested, auditable batch‑processing pipeline