File Integrity Checker

A Python-based file integrity monitoring tool that uses SHA-256 hashing to identify changes in files within a selected directory.

Overview

The File Integrity Checker creates a baseline of file hashes and compares it with later scans to identify files that have been added, modified, or deleted.

It is a beginner-friendly cybersecurity project demonstrating file hashing, integrity monitoring, and basic Python automation.

Features

- SHA-256 Hashing: Generates unique hashes for files.
- Baseline Creation: Records the original state of files in a directory.
- Modified File Detection: Identifies files whose contents have changed.
- Added File Detection: Detects newly added files.
- Deleted File Detection: Identifies files that are no longer present.
- Integrity Reports: Displays a summary of detected changes.

Technologies Used

- Python
- hashlib
- os
- json
- pathlib
- datetime

Requirements

- Python 3.6 or newer.
- No external Python packages required.

Installation

Clone the repository:

git clone https://github.com/jamessomadina/file-integrity-checker.git

Navigate into the project directory:

cd file-integrity-checker

Usage

Run the program:

python file_integrity_checker.py

Choose from the menu:

1. Create a new baseline.
2. Check file integrity.
3. Exit.

Enter the directory path you want to monitor.

After creating a baseline, run the integrity check again to identify changes.

How It Works

1. The user selects a directory.
2. The program calculates SHA-256 hashes for its files.
3. The hashes are saved as a baseline.
4. During a later scan, new hashes are calculated.
5. The program compares the current hashes with the saved baseline.
6. Added, deleted, and modified files are reported.

Project Purpose

This project was developed to improve practical knowledge of Python programming and fundamental cybersecurity concepts, particularly file integrity monitoring and cryptographic hashing.

Limitations

This tool detects changes in file contents and directory contents. It does not identify the person responsible for a change or determine whether a changed file is malicious.

The baseline is stored locally and should be protected against unauthorized modification.

Author

James Somadina Eberechukwu

GitHub: https://github.com/jamessomadina