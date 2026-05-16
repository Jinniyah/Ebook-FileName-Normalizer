import json
import os
from typing import Dict, Any, List

from config import STATE_FILE


def get_state_file() -> str:
    return os.getenv("STATE_FILE", "state.json")


def load_state():
    state_file = get_state_file()
    if not os.path.exists(state_file):
        return {"processed": []}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    state_file = get_state_file()
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def mark_processed(state, path):
    state["processed"].append(path)
