"""
package_all_tasks.py
====================
Creates a consolidated submission ZIP 'Auspify_Python_Internship_All_Tasks.zip'
on your Desktop containing all 4 completed tasks, documentation, and tests.
"""

import os
import shutil
import zipfile
from pathlib import Path


def package_full_internship():
    root = Path(__file__).resolve().parent
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    zip_path = desktop / "Auspify_Python_Internship_All_Tasks.zip"

    print("Cleaning __pycache__ and temporary files...")
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
            if file_path.is_file():
                rel = file_path.relative_to(root)
                if any(part in exclude_names or part.endswith(".pyc") or part.endswith(".tmp") for part in rel.parts):
                    continue
                arcname = os.path.join("Auspify_Python_Internship", *rel.parts)
                zipf.write(file_path, arcname)

    print("\n[SUCCESS] Master submission ZIP created successfully!")
    print(f"Location: {zip_path}\n")


if __name__ == "__main__":
    package_full_internship()
