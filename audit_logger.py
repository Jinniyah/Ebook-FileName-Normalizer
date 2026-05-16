import csv
import os
from typing import Dict, Any

from config import AUDIT_LOG

HEADER = [
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
    if not os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)


def write_audit_row(row: Dict[str, Any]) -> None:
    with open(AUDIT_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                row.get("original_filename"),
                row.get("new_filename"),
                row.get("title"),
                row.get("author_first"),
                row.get("author_last"),
                row.get("series"),
                row.get("series_number"),
                row.get("ai_used"),
                row.get("renamed"),
                row.get("skipped_reason"),
            ]
        )
