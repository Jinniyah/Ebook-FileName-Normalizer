import os
import re
from typing import Dict, Any

FILENAME_PATTERN = re.compile(r"^[^,]+, [^—]+ — .*#\d{2} — .*\.epub$", re.IGNORECASE)

INVALID_CHARS = r'[\\/:*?"<>|]'


def sanitize_filename(name: str) -> str:
    name = re.sub(INVALID_CHARS, "—", name)
    return name.rstrip(" .")



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

    safe_name = sanitize_filename(new_name)

    new_path = os.path.join(folder, safe_name)

    if not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return new_path

    return None
