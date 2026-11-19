
import json
import pytest

from app.history import load_history, save_history


def test_load_history_when_file_does_not_exist(tmp_path):
    history_file = tmp_path / "history.json"

    history = load_history(history_file)

    assert history == {
        "version": 1,
        "operations": []
    }


def test_save_and_load_history(tmp_path):
    history_file = tmp_path / "history.json"

    history = {
        "version": 1,
        "operations": [
            {
                "original": "data/report.pdf",
                "destination": "output/Documents/report.pdf",
                "status": "moved"
            }
        ]
    }

    save_history(history, history_file)

    loaded_history = load_history(history_file)

    assert loaded_history == history


def test_load_history_rejects_invalid_json(tmp_path):
    history_file = tmp_path / "history.json"
    history_file.write_text("{invalid json")

    with pytest.raises(json.JSONDecodeError):
        load_history(history_file)


def test_load_history_rejects_invalid_structure(tmp_path):
    history_file = tmp_path / "history.json"

    history_file.write_text(
        json.dumps({"version": 2, "operations": []})
    )

    with pytest.raises(ValueError):
        load_history(history_file)
