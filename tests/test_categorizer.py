
from app.categorizer import categorize_file


def test_categorizes_images():
    assert categorize_file("photo.jpg") == "Images"
    assert categorize_file("picture.png") == "Images"


def test_categorizes_videos():
    assert categorize_file("movie.mp4") == "Videos"
    assert categorize_file("clip.mkv") == "Videos"


def test_categorizes_audio():
    assert categorize_file("song.mp3") == "Audio"
    assert categorize_file("track.wav") == "Audio"


def test_categorizes_documents():
    assert categorize_file("report.pdf") == "Documents"
    assert categorize_file("notes.txt") == "Documents"


def test_unknown_extension_returns_other():
    assert categorize_file("archive.xyz") == "Other"


def test_file_without_extension_returns_other():
    assert categorize_file("README") == "Other"


def test_extension_matching_is_case_insensitive():
    assert categorize_file("PHOTO.JPG") == "Images"
    assert categorize_file("SONG.MP3") == "Audio"
