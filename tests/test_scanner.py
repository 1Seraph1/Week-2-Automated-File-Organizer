
import pytest

from app.scanner import scan_directory


def test_scan_directory_finds_files(tmp_path):
    # Create sample files
    (tmp_path / "image.jpg").touch()
    (tmp_path / "song.mp3").touch()

    files = scan_directory(tmp_path)

    assert len(files) == 2


def test_scan_directory_finds_nested_files(tmp_path):
    # Create a nested folder
    nested_folder = tmp_path / "Projects"
    nested_folder.mkdir()

    (nested_folder / "report.pdf").touch()

    files = scan_directory(tmp_path)

    assert len(files) == 1
    assert files[0].name == "report.pdf"


def test_scan_directory_excludes_hidden_files(tmp_path):
    # Create normal and hidden files
    (tmp_path / "notes.txt").touch()
    (tmp_path / ".hidden.txt").touch()

    files = scan_directory(tmp_path)

    assert len(files) == 1
    assert files[0].name == "notes.txt"


def test_scan_directory_includes_hidden_files(tmp_path):
    (tmp_path / ".hidden.txt").touch()

    files = scan_directory(
        tmp_path,
        include_hidden=True
    )

    assert len(files) == 1


def test_scan_directory_invalid_path():
    with pytest.raises(FileNotFoundError):
        scan_directory("nonexistent_folder")


def test_scan_directory_rejects_file_as_directory(tmp_path):
    file = tmp_path / "example.txt"
    file.touch()

    with pytest.raises(NotADirectoryError):
        scan_directory(file)


def test_scan_directory_excludes_hidden_directory_contents(tmp_path):
    hidden_folder = tmp_path / ".Private"
    hidden_folder.mkdir()

    hidden_file = hidden_folder / "secret.txt"
    hidden_file.touch()

    normal_file = tmp_path / "notes.txt"
    normal_file.touch()

    files = scan_directory(tmp_path)

    assert len(files) == 1
    assert files[0].name == "notes.txt"


def test_scan_directory_excludes_output_directory(tmp_path):
    source = tmp_path / "data"
    output = source / "output"

    output.mkdir(parents=True)

    normal_file = source / "report.pdf"
    normal_file.touch()

    output_file = output / "old_report.pdf"
    output_file.touch()

    files = scan_directory(
        source,
        exclude_directories=[output]
    )

    assert len(files) == 1
    assert files[0].name == "report.pdf"
