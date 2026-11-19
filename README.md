# Automated File Intelligence & Organization System

## Overview

The Automated File Intelligence & Organization System is a Python-based application designed to scan, classify, and organize files automatically.

The system identifies files based on their extensions and sorts them into appropriate categories. It also provides safety mechanisms such as dry-run previews, operation history, rollback functionality, and interrupted-operation recovery.

The project aims to make file organization more efficient while reducing the risk of accidental file loss.

## Features

- **Automated File Scanning:** Scans directories and discovers files, including files in nested folders.
- **File Categorization:** Classifies files into Images, Videos, Audio, Documents, and Other.
- **Hidden File Handling:** Supports excluding hidden files and directories.
- **Directory Exclusion:** Allows specified directories to be excluded from scanning.
- **Duplicate Filename Handling:** Prevents existing files from being overwritten by generating alternative filenames.
- **Directory Structure Preservation:** Supports preserving the original folder structure or organizing files into flattened category folders.
- **Dry-Run Preview:** Displays planned file movements before executing them.
- **Operation History:** Records file movements in a JSON history file.
- **Rollback:** Restores previously organized files to their original locations.
- **Interrupted Operation Recovery:** Checks incomplete operations and identifies their likely state.
- **Error Handling:** Handles common file access and movement errors.

## Technologies Used

- Python 3.14
- JSON
- pathlib
- shutil
- logging
- pytest

## Project Structure

```text
automated-file-organizer/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── scanner.py
│   ├── categorizer.py
│   ├── organizer.py
│   └── history.py
│
├── tests/
│   ├── test_scanner.py
│   ├── test_categorizer.py
│   ├── test_organizer.py
│   └── test_history.py
│
├── data/
├── output/
├── .venv/
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

## Installation and Setup

### 1. Clone or download the project

Open the project directory in Visual Studio Code.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### 1. Add files

Place the files you want to organize inside the `data` directory.

### 2. Run the application

```bash
python -m app.main
```

### 3. Select an operation

The application provides the following menu options:

1. Organize files
2. Rollback previous operations
3. Recover interrupted operations
4. Exit

### 4. Preview and execute

When organizing files, the application first performs a dry run to preview the planned movements.

The user is then asked to confirm whether the operations should be executed.

Files are moved only after confirmation.

## File Categories

| Category | Example Extensions |
|---|---|
| Images | JPG, JPEG, PNG, GIF, WEBP, SVG |
| Videos | MP4, MKV, MOV, AVI, WEBM |
| Audio | MP3, WAV, AAC, FLAC, OGG |
| Documents | PDF, DOC, DOCX, TXT, XLSX, PPTX |
| Other | Unsupported or unrecognized extensions |

## Operation History and Recovery

The application stores operation records in:

```text
output/operation_history.json
```

The history records the original file location, destination location, and operation status.

The rollback functionality uses this information to restore previously moved files.

The recovery functionality checks pending operations and classifies them based on whether the original and destination files exist.

Operations requiring manual review are not automatically restored.

## Testing

The project uses pytest for automated testing.

Run the complete test suite using:

```bash
python -m pytest -v
```

The current test suite has successfully passed **37 automated tests**.

## Safety Considerations

- Always review the dry-run preview before confirming file movements.
- Keep backups of important files before performing large organization operations.
- Avoid manually modifying the operation history JSON file.
- Review operations marked as requiring manual attention before taking further action.

## Conclusion

The Automated File Intelligence & Organization System demonstrates the use of Python modules, file handling, directory traversal, exception handling, logging, JSON persistence, and automated testing.

It provides a structured approach to automating file organization while incorporating mechanisms to reduce the risk of accidental data loss.