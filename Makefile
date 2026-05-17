# -----------------------------
# Virtual environment
# -----------------------------

venv:
	python -m venv .venv

activate:
	@echo "To activate your virtual environment:"
	@echo "  PowerShell:  .\\.venv\\Scripts\\Activate.ps1"
	@echo "  CMD:         .\\.venv\\Scripts\\activate.bat"
	@echo "  macOS/Linux: source .venv/bin/activate"

# -----------------------------
# Install dependencies
# -----------------------------

install:
	.venv\Scripts\python.exe -m pip install --upgrade pip
	.venv\Scripts\pip install -r requirements.txt

# -----------------------------
# Testing
# -----------------------------

test:
	.venv\Scripts\pytest -v

# -----------------------------
# Linting & formatting
# -----------------------------

lint:
	.venv\Scripts\ruff check .
	.venv\Scripts\black --check .

format:
	.venv\Scripts\black .
	.venv\Scripts\ruff check . --fix

typecheck:
	.venv\Scripts\mypy .

# Run all quality checks (lint + types + tests)
check: lint typecheck test

# -----------------------------
# Run the tool
# -----------------------------

dry-run:
	.venv\Scripts\python main.py --dry-run

run:
	.venv\Scripts\python main.py --live

# -----------------------------
# Maintenance
# -----------------------------

reset-state:
	.venv\Scripts\python main.py --reset-state --dry-run

all: check
