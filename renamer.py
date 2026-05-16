import os
import re
from typing import Dict, Any

FILENAME_PATTERN = re.compile(r"^[^,]+, [^—]+ — .*#\d{2} — .*\.epub$", re.IGNORECASE)


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)


def build_filename(meta: Dict[str, Any]) -> str:
    last = meta.get("author_last") or "Unknown"
    first = meta.get("author_first") or "Unknown"
    title = meta.get("title") or "Unknown"

    series = meta.get("series")
    number = meta.get("series_number")

    if series and number:
        middle = f"{series} #{int(number):02d}"
    elif series:
        middle = f"{series} #ZZ"
    else:
        middle = None

    if middle:
        return f"{last}, {first} — {middle} — {title}.epub"
    else:
        return f"{last}, {first} — {title}.epub"


def rename_file(old_path: str, new_name: str) -> str | None:
    folder = os.path.dirname(old_path)
    new_path = os.path.join(folder, new_name)

    if not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return new_path

    return None
