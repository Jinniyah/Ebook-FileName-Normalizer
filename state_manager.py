import json
import os
from typing import Any, Dict

from config import STATE_FILE


def load_state() -> Dict[str, Any]:
    """Return the persisted state dict, or a fresh default if none exists."""
    if not os.path.exists(STATE_FILE):
        return {"processed": []}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def save_state(state: Dict[str, Any]) -> None:
    """Persist the state dict to disk."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def mark_processed(state: Dict[str, Any], path: str) -> None:
    """Record *path* as processed and immediately flush state to disk.

    Flushing on every mark (rather than only at the end of a run) means
    progress is never lost if the process exits unexpectedly mid-batch.
    """
    state["processed"].append(path)
    save_state(state)
