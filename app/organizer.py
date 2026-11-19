
import logging
import shutil
from pathlib import Path

from app.categorizer import categorize_file
from app.history import load_history, save_history


logger = logging.getLogger(__name__)


def organize_files(
    files,
    output_directory,
    source_directory,
    dry_run=True,
    preserve_structure=True,
    history_file=None
):
    output_directory = Path(output_directory)
    source_directory = Path(source_directory)

    operation_history = []
    planned_destinations = set()

    # Load previous history when persistence is enabled
    history_data = None

    if history_file is not None:
        history_data = load_history(history_file)

    for file in files:
        file = Path(file)
        record = None

        try:
            category = categorize_file(file)

            category_folder = output_directory / category

            if preserve_structure:
                relative_path = file.relative_to(source_directory)
                destination = category_folder / relative_path
            else:
                destination = category_folder / file.name

            # Prevent filename collisions
            counter = 1
            original_destination = destination

            while (
                destination.exists()
                or destination in planned_destinations
            ):
                new_name = (
                    f"{original_destination.stem}_{counter}"
                    f"{original_destination.suffix}"
                )

                destination = original_destination.parent / new_name
                counter += 1

            planned_destinations.add(destination)

            if dry_run:
                logger.info(
                    "[PREVIEW] %s -> %s",
                    file,
                    destination
                )

            else:
                # Record the intended movement before executing it
                if history_data is not None:
                    record = {
                        "original": str(file.resolve()),
                        "destination": str(destination.resolve()),
                        "status": "pending"
                    }

                    history_data["operations"].append(record)
                    save_history(history_data, history_file)

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                shutil.move(str(file), str(destination))

                operation_history.append({
                    "original": file,
                    "destination": destination
                })

                # Mark the movement as successful
                if record is not None:
                    record["status"] = "moved"
                    save_history(history_data, history_file)

                logger.info(
                    "[MOVED] %s -> %s",
                    file,
                    destination
                )

        except (PermissionError, OSError, ValueError) as error:
            logger.error(
                "Could not process %s: %s",
                file,
                error
            )

            # Record failed operations when possible
            if record is not None:
                record["status"] = "failed"

                try:
                    save_history(history_data, history_file)
                except OSError:
                    logger.exception(
                        "Could not update operation history."
                    )

    return operation_history


def rollback_operations(operation_history):
    logger.info("Starting rollback...")

    for operation in reversed(operation_history):
        original = operation["original"]
        destination = operation["destination"]

        try:
            if not destination.exists():
                logger.warning(
                    "Cannot find moved file: %s",
                    destination
                )
                continue

            if original.exists():
                logger.error(
                    "Cannot restore %s: original location already exists.",
                    original.name
                )
                continue

            original.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.move(
                str(destination),
                str(original)
            )

            logger.info("Restored: %s", original.name)

        except (PermissionError, OSError) as error:
            logger.error(
                "Rollback failed for %s: %s",
                original.name,
                error
            )

    logger.info("Rollback process completed.")


def rollback_from_history(history_file):
    logger.info("Starting persistent rollback...")

    try:
        history_data = load_history(history_file)

    except (OSError, ValueError) as error:
        logger.error("Could not load operation history: %s", error)
        return

    for operation in reversed(history_data["operations"]):

        if operation["status"] != "moved":
            continue

        original = Path(operation["original"])
        destination = Path(operation["destination"])

        try:
            if not destination.exists():
                logger.warning(
                    "Cannot restore missing file: %s",
                    destination
                )
                continue

            if original.exists():
                logger.error(
                    "Cannot restore %s: original file already exists.",
                    original
                )
                continue

            original.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.move(
                str(destination),
                str(original)
            )

            operation["status"] = "rolled_back"

            save_history(history_data, history_file)

            logger.info("Restored: %s", original)

        except (PermissionError, OSError) as error:
            logger.error(
                "Rollback failed for %s: %s",
                original,
                error
            )

    logger.info("Persistent rollback completed.")


def recover_pending_operations(history_file):
    logger.info("Checking for interrupted operations...")

    try:
        history_data = load_history(history_file)

    except (OSError, ValueError) as error:
        logger.error("Could not load operation history: %s", error)
        return

    recovery_counts = {
        "moved": 0,
        "not_moved": 0,
        "needs_review": 0,
        "missing": 0
    }

    for operation in history_data["operations"]:

        if operation.get("status") != "pending":
            continue

        try:
            original = Path(operation["original"])
            destination = Path(operation["destination"])

        except (KeyError, TypeError) as error:
            logger.error("Invalid operation record: %s", error)
            continue

        original_exists = original.is_file()
        destination_exists = destination.is_file()

        if not original_exists and destination_exists:
            operation["status"] = "moved"
            recovery_counts["moved"] += 1

            logger.info(
                "Movement completed before interruption: %s",
                destination
            )

        elif original_exists and not destination_exists:
            operation["status"] = "not_moved"
            recovery_counts["not_moved"] += 1

            logger.info(
                "Movement did not complete: %s",
                original
            )

        elif original_exists and destination_exists:
            operation["status"] = "needs_review"
            recovery_counts["needs_review"] += 1

            logger.warning(
                "Both original and destination exist. Manual review required: %s",
                original
            )

        else:
            operation["status"] = "missing"
            recovery_counts["missing"] += 1

            logger.error(
                "File missing from both locations: %s",
                original
            )

        try:
            save_history(history_data, history_file)

        except OSError:
            logger.exception(
                "Could not save recovery status for %s",
                original
            )
            return

    logger.info("Recovery check completed.")

    for status, count in recovery_counts.items():
        logger.info("%s: %d", status, count)

    return recovery_counts
