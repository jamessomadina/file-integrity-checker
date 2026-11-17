
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone


BASELINE_DIR = Path.home() / ".file_integrity_checker"


def get_baseline_path(folder):
    """Create a unique baseline filename for each monitored folder."""
    folder_name = str(folder).encode("utf-8")
    folder_hash = hashlib.sha256(folder_name).hexdigest()[:16]

    return BASELINE_DIR / f"baseline_{folder_hash}.json"


def is_inside(path, parent):
    """Check whether a path is inside another directory."""
    return path == parent or parent in path.parents


def calculate_hash(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_folder(folder, baseline_path):
    """Scan a folder and return the hashes of its regular files."""
    file_hashes = {}
    errors = []

    baseline_dir = BASELINE_DIR.resolve()

    def handle_error(error):
        errors.append(str(error))

    for root, dirs, files in os.walk(
        folder, followlinks=False, onerror=handle_error
    ):
        current_dir = Path(root)

        # Skip symbolic-link directories and the baseline storage folder.
        dirs[:] = [
            name for name in dirs
            if not (current_dir / name).is_symlink()
            and not is_inside(
                (current_dir / name).resolve(), baseline_dir
            )
        ]

        for filename in files:
            file_path = current_dir / filename

            # Skip symbolic links and baseline files.
            if file_path.is_symlink():
                continue

            resolved_path = file_path.resolve()

            if is_inside(resolved_path, baseline_dir):
                continue

            try:
                relative_path = file_path.relative_to(folder).as_posix()
                file_hashes[relative_path] = calculate_hash(file_path)

            except OSError as error:
                errors.append(f"{file_path}: {error}")

    return file_hashes, errors


def create_baseline():
    """Save the original file hashes."""
    folder_input = input(
        "\nEnter the folder path you want to monitor: "
    ).strip().strip('"').strip("'")

    folder = Path(folder_input).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print("\nError: That folder does not exist.")
        return

    baseline_path = get_baseline_path(folder)

    print("\nScanning folder...")

    file_hashes, errors = scan_folder(folder, baseline_path)

    if errors:
        print("\nScan incomplete. Fix these access errors and try again:")
        for error in errors:
            print(f"- {error}")
        return

    baseline_data = {
        "version": 1,
        "folder": str(folder),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": file_hashes
    }

    try:
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)

        temporary_file = baseline_path.with_suffix(".tmp")
        temporary_file.write_text(
            json.dumps(baseline_data, indent=4),
            encoding="utf-8"
        )
        temporary_file.replace(baseline_path)

        print("\nBaseline created successfully!")
        print(f"Files recorded: {len(file_hashes)}")
        print(f"Monitored folder: {folder}")

    except OSError as error:
        print(f"\nCould not save baseline: {error}")


def check_integrity():
    """Compare current file hashes with the saved baseline."""
    folder_input = input(
        "\nEnter the folder path you previously monitored: "
    ).strip().strip('"').strip("'")

    folder = Path(folder_input).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print("\nError: That folder does not exist.")
        return

    baseline_path = get_baseline_path(folder)

    if not baseline_path.exists():
        print("\nNo baseline found for this folder.")
        print("Create a baseline first.")
        return

    try:
        baseline_data = json.loads(
            baseline_path.read_text(encoding="utf-8")
        )

        if (
            not isinstance(baseline_data, dict)
            or not isinstance(baseline_data.get("files"), dict)
            or not all(
                isinstance(name, str) and isinstance(value, str)
                for name, value in baseline_data["files"].items()
            )
        ):
            print("\nError: The baseline file has an invalid format.")
            return

        if baseline_data.get("folder") != str(folder):
            print("\nError: The baseline belongs to a different folder.")
            return

    except (OSError, json.JSONDecodeError):
        print("\nError: Could not read the baseline file.")
        return

    print("\nChecking file integrity...")

    current_files, errors = scan_folder(folder, baseline_path)

    if errors:
        print("\nScan incomplete. No comparison was performed.")
        for error in errors:
            print(f"- {error}")
        return

    original_files = baseline_data["files"]

    original_names = set(original_files)
    current_names = set(current_files)

    added = sorted(current_names - original_names)
    deleted = sorted(original_names - current_names)

    modified = sorted(
        name for name in original_names & current_names
        if original_files[name] != current_files[name]
    )

    print("\n========== INTEGRITY REPORT ==========")

    print(f"\nFiles originally recorded: {len(original_files)}")
    print(f"Files currently found: {len(current_files)}")

    print("\nADDED FILES:")
    if added:
        for name in added:
            print(f"  + {name}")
    else:
        print("  None")

    print("\nDELETED FILES:")
    if deleted:
        for name in deleted:
            print(f"  - {name}")
    else:
        print("  None")

    print("\nMODIFIED FILES:")
    if modified:
        for name in modified:
            print(f"  * {name}")
    else:
        print("  None")

    print("\n========== SUMMARY ==========")
    print(f"Added: {len(added)}")
    print(f"Deleted: {len(deleted)}")
    print(f"Modified: {len(modified)}")

    if not added and not deleted and not modified:
        print("\nRESULT: No changes detected.")
    else:
        print("\nRESULT: Changes detected. Review the report above.")

    print("\n======================================")


def main():
    while True:
        print("\n================================")
        print("       FILE INTEGRITY CHECKER")
        print("================================")
        print("1. Create a new baseline")
        print("2. Check file integrity")
        print("3. Exit")
        print("================================")

        choice = input("Select an option: ").strip()

        if choice == "1":
            create_baseline()

        elif choice == "2":
            check_integrity()

        elif choice == "3":
            print("\nExiting File Integrity Checker.")
            break

        else:
            print("\nInvalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
