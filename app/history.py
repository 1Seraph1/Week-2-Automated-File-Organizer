
import json
from pathlib import Path


def load_history(history_file):
    history_file = Path(history_file)

    if not history_file.exists():
        return {
            "version": 1,
            "operations": []
        }

    with history_file.open("r", encoding="utf-8") as file:
        history = json.load(file)

    if (
        not isinstance(history, dict)
        or history.get("version") != 1
        or not isinstance(history.get("operations"), list)
    ):
        raise ValueError("Invalid operation history format.")

    return history


def save_history(history, history_file):
    history_file = Path(history_file)

    history_file.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = history_file.with_name(
        history_file.name + ".tmp"
    )

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

        temporary_file.replace(history_file)

    except OSError:
        if temporary_file.exists():
            temporary_file.unlink()

        raise
