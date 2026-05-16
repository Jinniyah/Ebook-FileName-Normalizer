import json
from state_manager import load_state, save_state, mark_processed


def test_load_state_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    state = load_state()
    assert state == {"processed": []}


def test_save_and_load_state(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    monkeypatch.setenv("STATE_FILE", str(path))

    save_state({"processed": ["a"]})
    loaded = load_state()
    assert loaded["processed"] == ["a"]


def test_mark_processed():
    state = {"processed": []}
    mark_processed(state, "x")
    assert state["processed"] == ["x"]
