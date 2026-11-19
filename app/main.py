
import logging

from app.scanner import scan_directory
from app.organizer import (
    organize_files,
    rollback_from_history,
    recover_pending_operations
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def organize_workflow():
    directory = "data"
    output_directory = "output"
    history_file = "output/operation_history.json"

    # Scan the source directory
    files = scan_directory(
        directory,
        exclude_directories=[output_directory]
    )

    logger.info("Found %d files.", len(files))

    if not files:
        logger.info("No files found. Nothing to organize.")
        return

    # Preview the planned operations first
    logger.info("Starting dry run...")

    organize_files(
        files,
        output_directory,
        source_directory=directory,
        dry_run=True,
        preserve_structure=True
    )

    logger.info("Preview completed.")

    # Ask for confirmation before moving files
    confirmation = input(
        "\nDo you want to execute these operations? (yes/no): "
    ).strip().lower()

    if confirmation not in ("yes", "y"):
        logger.info("Operation cancelled. No files were moved.")
        return

    # Execute the actual organization
    logger.info("Starting file organization...")

    history = organize_files(
        files,
        output_directory,
        source_directory=directory,
        dry_run=False,
        preserve_structure=True,
        history_file=history_file
    )

    logger.info(
        "Organization completed. Successfully moved %d files.",
        len(history)
    )


def main():
    history_file = "output/operation_history.json"

    while True:
        print("\n===== AUTOMATED FILE ORGANIZER =====")
        print("1. Organize files")
        print("2. Rollback previous operations")
        print("3. Recover interrupted operations")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            try:
                organize_workflow()
            except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
                logger.error("Could not access directory: %s", error)
            except Exception:
                logger.exception("An unexpected error occurred during organization.")

        elif choice == "2":
            rollback_from_history(history_file)

        elif choice == "3":
            recover_pending_operations(history_file)

        elif choice == "4":
            logger.info("Exiting application. Goodbye!")
            break

        else:
            print("Invalid selection. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
