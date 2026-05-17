import csv
import os
from datetime import datetime, timezone
from typing import Any, Dict

from config import AUDIT_LOG

HEADER = [
    "timestamp",
    "original_filename",
    "new_filename",
    "title",
    "author_first",
    "author_last",
    "series",
    "series_number",
    "ai_used",
    "renamed",
    "skipped_reason",
]


def init_audit_log() -> None:
    """Create the audit log CSV with headers if it does not already exist."""
    if not os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
            writer.writeheader()


def write_audit_row(row: Dict[str, Any]) -> None:
    """Append a single action record to the audit log.

    The ``timestamp`` field is injected automatically (UTC ISO 8601).
    Any extra keys in *row* are silently ignored so callers don't need to
    be updated when the schema gains new optional columns.
    """
    row.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with open(AUDIT_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
        writer.writerow(row)
