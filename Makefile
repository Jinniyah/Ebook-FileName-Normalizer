# -----------------------------
# Virtual environment
# -----------------------------

venv:
	python -m venv .venv

activate:
	@echo "To activate your venv:"
	@echo "PowerShell: .\\.venv\\Scripts\\Activate.ps1"
	@echo "CMD:        .\\.venv\\Scripts\\activate.bat"
	@echo "Linux/Mac:  source .venv/bin/activate"

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
	.venv\Scripts\pytest

# -----------------------------
# Linting & formatting
# -----------------------------

lint:	
	.venv\Scripts\black --check .

format:
	.venv\Scripts\black .

fix:
	.venv\Scripts\black .

# -----------------------------
# Run everything
# -----------------------------

all: lint test