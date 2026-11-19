
from pathlib import Path


FILE_CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".webm"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"}
}


def categorize_file(file_path):
    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Other"

