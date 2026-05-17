import os
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

BOOKS_FOLDER: str | None = os.getenv("BOOKS_FOLDER")

TEXT_SAMPLE_LENGTH: int = int(os.getenv("TEXT_SAMPLE_LENGTH", "5000"))

DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"

DEBUG_AI: bool = os.getenv("DEBUG_AI", "false").lower() == "true"

MAX_FILES: int = int(os.getenv("MAX_FILES", "50"))

STATE_FILE: str = os.getenv("STATE_FILE", "state.json")

AUDIT_LOG: str = os.getenv("AUDIT_LOG", "audit_log.csv")
