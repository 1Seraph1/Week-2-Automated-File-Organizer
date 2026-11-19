
import logging
import stat
from pathlib import Path


logger = logging.getLogger(__name__)


def is_hidden(file_path):
    if file_path.name.startswith("."):
        return True

    try:
        hidden_attribute = getattr(stat, "FILE_ATTRIBUTE_HIDDEN", 0x02)
        attributes = file_path.stat().st_file_attributes

        return bool(attributes & hidden_attribute)

    except (AttributeError, OSError):
        return False


def has_hidden_component(path, root):
    current = path

    while current != root:
        if is_hidden(current):
            return True

        current = current.parent

    return False


def scan_directory(
    directory,
    recursive=True,
    include_hidden=False,
    exclude_directories=None
):
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    excluded_paths = [
        Path(path).resolve()
        for path in (exclude_directories or [])
    ]

    files = []

    logger.info("Scanning directory: %s", directory)

    if recursive:
        items = directory.rglob("*")
    else:
        items = directory.iterdir()

    for item in items:

        # Skip excluded directories and their contents
        resolved_item = item.resolve()

        if any(
            resolved_item.is_relative_to(excluded)
            for excluded in excluded_paths
        ):
            logger.debug("Skipping excluded path: %s", item)
            continue

        if item.is_file():

            if not include_hidden and has_hidden_component(item, directory):
                logger.debug("Skipping hidden path: %s", item)
                continue

            files.append(item)
            logger.debug("Discovered file: %s", item)

    logger.info("Scanning completed. Found %d files.", len(files))

    return files
