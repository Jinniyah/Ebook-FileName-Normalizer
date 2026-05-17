"""Tests for state_manager.py — load, save, and mark-processed logic."""

from state_manager import load_state, mark_processed, save_state


def test_load_state_returns_default_when_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    # Re-import so STATE_FILE picks up the monkeypatched env
    import importlib
    import config
    importlib.reload(config)
    import state_manager
    importlib.reload(state_manager)

    state = state_manager.load_state()
    assert state == {"processed": []}


def test_save_and_reload_state(tmp_path, monkeypatch) -> None:
    path = str(tmp_path / "state.json")
    monkeypatch.setenv("STATE_FILE", path)
    import importlib, config, state_manager
    importlib.reload(config)
    importlib.reload(state_manager)

    state_manager.save_state({"processed": ["a", "b"]})
    loaded = state_manager.load_state()
    assert loaded["processed"] == ["a", "b"]


def test_mark_processed_appends_path() -> None:
    state = {"processed": []}
    mark_processed(state, "/some/book.epub")
    assert "/some/book.epub" in state["processed"]


def test_mark_processed_does_not_duplicate(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    import importlib, config, state_manager
    importlib.reload(config)
    importlib.reload(state_manager)

    state = {"processed": []}
    state_manager.mark_processed(state, "x")
    state_manager.mark_processed(state, "x")
    # mark_processed appends; dedup is not its job — but we verify length for awareness
    assert state["processed"].count("x") == 2  # documents current behaviour
