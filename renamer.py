import os
import re
from typing import Any, Dict

# Matches both valid normalized formats:
#   Lastname, Firstname — Series #01 — Title.epub
#   Lastname, Firstname — Title.epub
FILENAME_PATTERN = re.compile(
    r"^[^,]+, [^—]+(— .+ #\d{2} — .+|— [^—]+)\.epub$",
    re.IGNORECASE,
)

INVALID_CHARS = r'[\\/:*?"<>|]'


def safe_filename(name: str) -> str:
    """Replace filesystem-illegal characters and strip trailing junk."""
    name = re.sub(INVALID_CHARS, "—", name)
    return name.rstrip(" .")


# Keep the old name as an alias so existing internal callers still work.
sanitize_filename = safe_filename


def build_filename(meta: Dict[str, Any]) -> str:
    """Construct a normalized EPUB filename from metadata fields.

    Output formats:
        ``Lastname, Firstname — Series #01 — Title.epub``
        ``Lastname, Firstname — Title.epub``
    """
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
    return f"{last}, {first} — {title}.epub"


def rename_file(old_path: str, new_name: str) -> str | None:
    """Rename *old_path* to *new_name* in the same directory.

    Returns the new full path on success, or ``None`` if the target
    already exists (conflict — no overwrite).
    """
    folder = os.path.dirname(old_path)
    safe_name = safe_filename(new_name)
    new_path = os.path.join(folder, safe_name)

    if not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return new_path

    return None
