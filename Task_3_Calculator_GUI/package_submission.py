"""
package_submission.py
=====================
Helper script to package Task 3 into 'Task_3_Calculator_GUI.zip'
on your Desktop for Auspify Technologies submission.

Automatically cleans __pycache__ and temporary files before compressing.
"""

import os
import shutil
import zipfile
from pathlib import Path


def create_submission_zip():
    root = Path(__file__).resolve().parent
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    zip_path = desktop / "Task_3_Calculator_GUI.zip"

    # Remove cache files
    print("Cleaning cache files...")
    for p in root.rglob("__pycache__"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)

    for p in root.rglob("*.pyc"):
        try:
            p.unlink()
        except OSError:
            pass

    exclude_names = {".git", "__pycache__", ".pytest_cache", ".vscode"}

    print(f"Compressing into: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in root.rglob("*"):
            parts = file_path.relative_to(root).parts
            if any(p in exclude_names or p.endswith(".pyc") or p.endswith(".tmp") for p in parts):
                continue
            # Store under Task_3_Calculator_GUI directory inside the zip
            arcname = os.path.join("Task_3_Calculator_GUI", *parts)
            zipf.write(file_path, arcname)

    print("\n[SUCCESS] Task_3_Calculator_GUI.zip created successfully!")
    print(f"Location: {zip_path}\n")
    print("Files included:")
    with zipfile.ZipFile(zip_path, "r") as zipf:
        for info in zipf.infolist():
            print(f" - {info.filename} ({info.file_size:,} bytes)")


if __name__ == "__main__":
    create_submission_zip()
