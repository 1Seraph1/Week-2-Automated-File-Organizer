
import json
import pytest

from app.organizer import (
    organize_files,
    rollback_operations,
    rollback_from_history,
    recover_pending_operations
)


def test_organize_files_dry_run(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("image content")

    files = [file]

    result = organize_files(
        files,
        output,
        source_directory=source,
        dry_run=True
    )

    assert result == []
    assert file.exists()
    assert not output.exists()


def test_organize_files_moves_file(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("image content")

    result = organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False
    )

    destination = output / "Images" / "photo.jpg"

    assert len(result) == 1
    assert destination.exists()
    assert not file.exists()


def test_organize_files_unknown_extension(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    source.mkdir()

    file = source / "archive.xyz"
    file.write_text("unknown content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False
    )

    assert (output / "Other" / "archive.xyz").exists()


def test_organize_files_without_extension(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    source.mkdir()

    file = source / "README"
    file.write_text("some content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False
    )

    assert (output / "Other" / "README").exists()


def test_organize_files_empty_list(tmp_path):
    output = tmp_path / "output"

    result = organize_files(
        [],
        output,
        source_directory=tmp_path,
        dry_run=False
    )

    assert result == []
    assert not output.exists()


def test_organize_files_preserves_structure(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"

    nested = source / "projects" / "images"
    nested.mkdir(parents=True)

    file = nested / "photo.jpg"
    file.write_text("image content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False,
        preserve_structure=True
    )

    assert (
        output / "Images" / "projects" / "images" / "photo.jpg"
    ).exists()


def test_organize_files_flattens_structure(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"

    nested = source / "projects"
    nested.mkdir(parents=True)

    file = nested / "photo.jpg"
    file.write_text("image content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False,
        preserve_structure=False
    )

    assert (output / "Images" / "photo.jpg").exists()


def test_organize_files_handles_permission_error(tmp_path, monkeypatch):
    import shutil

    source = tmp_path / "data"
    output = tmp_path / "output"
    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("image content")

    def raise_permission_error(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(shutil, "move", raise_permission_error)

    result = organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False
    )

    assert result == []
    assert file.exists()


def test_organize_files_handles_existing_destination(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("new image")

    existing = output / "Images" / "photo.jpg"
    existing.parent.mkdir(parents=True)
    existing.write_text("existing image")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False
    )

    assert existing.read_text() == "existing image"
    assert (existing.parent / "photo_1.jpg").exists()


def test_organize_files_persistent_history(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    history_file = tmp_path / "history.json"

    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("image content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False,
        history_file=history_file
    )

    history = json.loads(history_file.read_text())

    assert len(history["operations"]) == 1
    assert history["operations"][0]["status"] == "moved"


def test_dry_run_does_not_create_history(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    history_file = tmp_path / "history.json"

    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("image content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=True,
        history_file=history_file
    )

    assert not history_file.exists()
    assert file.exists()


def test_rollback_from_history(tmp_path):
    source = tmp_path / "data"
    output = tmp_path / "output"
    history_file = tmp_path / "history.json"

    source.mkdir()

    file = source / "photo.jpg"
    file.write_text("image content")

    organize_files(
        [file],
        output,
        source_directory=source,
        dry_run=False,
        history_file=history_file
    )

    rollback_from_history(history_file)

    assert file.exists()
    assert not (output / "Images" / "photo.jpg").exists()

    history = json.loads(history_file.read_text())
    assert history["operations"][0]["status"] == "rolled_back"


def test_recover_pending_operation_detects_completed_move(tmp_path):
    original = tmp_path / "data" / "photo.jpg"
    destination = tmp_path / "output" / "photo.jpg"
    history_file = tmp_path / "history.json"

    destination.parent.mkdir(parents=True)
    destination.write_text("image content")

    history = {
        "version": 1,
        "operations": [{
            "original": str(original),
            "destination": str(destination),
            "status": "pending"
        }]
    }

    history_file.write_text(json.dumps(history))

    counts = recover_pending_operations(history_file)

    updated = json.loads(history_file.read_text())

    assert updated["operations"][0]["status"] == "moved"
    assert counts["moved"] == 1


def test_recover_pending_operation_detects_uncompleted_move(tmp_path):
    original = tmp_path / "data" / "photo.jpg"
    destination = tmp_path / "output" / "photo.jpg"
    history_file = tmp_path / "history.json"

    original.parent.mkdir(parents=True)
    original.write_text("image content")

    history = {
        "version": 1,
        "operations": [{
            "original": str(original),
            "destination": str(destination),
            "status": "pending"
        }]
    }

    history_file.write_text(json.dumps(history))

    counts = recover_pending_operations(history_file)

    updated = json.loads(history_file.read_text())

    assert updated["operations"][0]["status"] == "not_moved"
    assert counts["not_moved"] == 1


def test_recover_pending_operation_detects_both_files(tmp_path):
    original = tmp_path / "data" / "photo.jpg"
    destination = tmp_path / "output" / "photo.jpg"
    history_file = tmp_path / "history.json"

    original.parent.mkdir(parents=True)
    destination.parent.mkdir(parents=True)

    original.write_text("original")
    destination.write_text("destination")

    history = {
        "version": 1,
        "operations": [{
            "original": str(original),
            "destination": str(destination),
            "status": "pending"
        }]
    }

    history_file.write_text(json.dumps(history))

    counts = recover_pending_operations(history_file)

    updated = json.loads(history_file.read_text())

    assert updated["operations"][0]["status"] == "needs_review"
    assert counts["needs_review"] == 1


def test_recover_pending_operation_detects_missing_file(tmp_path):
    original = tmp_path / "data" / "photo.jpg"
    destination = tmp_path / "output" / "photo.jpg"
    history_file = tmp_path / "history.json"

    history = {
        "version": 1,
        "operations": [{
            "original": str(original),
            "destination": str(destination),
            "status": "pending"
        }]
    }

    history_file.write_text(json.dumps(history))

    counts = recover_pending_operations(history_file)

    updated = json.loads(history_file.read_text())

    assert updated["operations"][0]["status"] == "missing"
    assert counts["missing"] == 1


def test_persistent_rollback_does_not_overwrite_original(tmp_path):
    original = tmp_path / "data" / "report.pdf"
    destination = tmp_path / "output" / "Documents" / "report.pdf"
    history_file = tmp_path / "history.json"

    original.parent.mkdir(parents=True)
    destination.parent.mkdir(parents=True)

    original.write_text("Original content")
    destination.write_text("Moved content")

    history = {
        "version": 1,
        "operations": [{
            "original": str(original),
            "destination": str(destination),
            "status": "moved"
        }]
    }

    history_file.write_text(json.dumps(history))

    rollback_from_history(history_file)

    assert original.read_text() == "Original content"
    assert destination.exists()

    updated_history = json.loads(history_file.read_text())

    assert updated_history["operations"][0]["status"] == "moved"


def test_persistent_rollback_can_be_run_twice(tmp_path):
    original = tmp_path / "data" / "report.pdf"
    destination = tmp_path / "output" / "Documents" / "report.pdf"
    history_file = tmp_path / "history.json"

    original.parent.mkdir(parents=True)
    destination.parent.mkdir(parents=True)

    destination.write_text("Moved content")

    history = {
        "version": 1,
        "operations": [{
            "original": str(original),
            "destination": str(destination),
            "status": "moved"
        }]
    }

    history_file.write_text(json.dumps(history))

    rollback_from_history(history_file)
    rollback_from_history(history_file)

    assert original.exists()
    assert original.read_text() == "Moved content"
    assert not destination.exists()

    updated_history = json.loads(history_file.read_text())

    assert updated_history["operations"][0]["status"] == "rolled_back"
