# Enhanced To-Do List Application

**Auspify Technologies — Python Development Internship**  
*Task 2: Console Task Management & Data Persistence System*

---

## 📌 Project Overview

The **Enhanced To-Do List Application** is a robust, production-ready task management system developed in Python. Designed to deliver an intuitive and resilient terminal experience, this application enables users to track deliverables, assign granular priority levels, schedule due dates, and perform multi-criterion sorting and keyword filtering.

Unlike basic scripting projects that suffer from runtime crashes or silent data loss upon unexpected shutdowns, this application implements an **atomic write architecture** with temporary swap files, **backward-compatible schema migration** for legacy JSON records, and strict **input validation** across all operations.

---

## ✨ Key Features

1. **Full CRUD Operations (Create, Read, Update, Delete):**
   - **Add Task:** Create tasks with mandatory non-empty titles, customizable priority levels, and optional deadlines.
   - **View Tasks:** Clean tabular display of all active items showing completion state, priority badges, and formatted due dates.
   - **Explicit Status Control:** Set tasks directly to `Pending` or `Completed` without ambiguous toggle confusion.
   - **Inline Task Editing:** Modify task names, priorities, or due dates independently while preserving unchanged fields on Enter.
   - **Safe Deletion:** Interactive confirmation prompt (`y/n`) with rollback protection if file persistence fails.

2. **Priority Hierarchy:**
   - Three standardized urgency levels: `High`, `Medium`, and `Low`.
   - Numeric shortcut selection (`1`, `2`, `3`) with fallback defaults.

3. **Date Validation & Deadlines:**
   - Strict `YYYY-MM-DD` ISO-8601 parsing via Python's `datetime.strptime`.
   - Graceful fallback and user alerts for malformed dates without crashing.

4. **Search & Multi-Criterion Sorting:**
   - **Keyword Search:** Case-insensitive substring matching across task descriptions.
   - **Status Filtering:** View `All`, `Pending`, or `Completed` subsets.
   - **Priority Sorting:** Arranges items from High to Low using custom mapping.
   - **Due Date Sorting:** Chronological order (earliest deadline first), gracefully placing undated tasks at the bottom.
   - **Alphabetical Sorting:** Case-insensitive lexical ordering (A–Z).

5. **Atomic Data Persistence & Crash Recovery:**
   - Data stored in human-readable, portable `tasks.json`.
   - Atomic disk writes via `.tmp` swap (`os.replace`) to prevent file corruption during sudden terminations.
   - Graceful corrupt file handling: halts safely without overwriting unreadable data.
   - Automatic migration of legacy task records missing newer schema fields (`priority`, `due_date`).

---

## 📂 Project Directory Structure

```text
Task_2_To-Do_List_Application/
├── todo_list.py             # Main CLI application script (9-option interactive menu)
├── todo_list_gui.py         # Modern Desktop GUI application (Tkinter / ttk)
├── test_todo_list.py        # Automated test suite (unittest framework, 12 test cases)
├── tasks.json               # Persistent JSON task database (atomic file writes)
├── test_cases.md            # Comprehensive verification report (TC01 - TC10)
├── package_submission.py    # Auto-packager creating submission ZIP on Desktop
└── README.md                # Project documentation and specifications
```

---

## 💾 Data Schema (`tasks.json`)

Tasks are serialized as a JSON array of objects conforming to the following schema:

```json
[
    {
        "title": "Submit Python Internship Project",
        "completed": false,
        "priority": "High",
        "due_date": "2026-10-25"
    },
    {
        "title": "Review Documentation",
        "completed": true,
        "priority": "Medium",
        "due_date": ""
    }
]
```

### Field Definitions:
| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `title` | `string` | Yes | — | The description or title of the task. |
| `completed` | `boolean` | Yes | `false` | Completion status (`true` for Completed, `false` for Pending). |
| `priority` | `string` | Yes | `"Medium"` | Urgency level: `"High"`, `"Medium"`, or `"Low"`. |
| `due_date` | `string` | No | `""` | Target deadline formatted as `YYYY-MM-DD` (or empty string if unset). |

---

## 🚀 Getting Started

### Prerequisites

- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python Version:** Python 3.8 or higher.
- **Dependencies:** None! Pure standard library implementation (`json`, `os`, `pathlib`, `datetime`, `unittest`).

### How to Run

#### Option A: Interactive CLI Terminal Application
1. Open your terminal / Command Prompt:
   ```powershell
   cd C:\Users\HP\Desktop\Auspify_Python_Internship\Task_2_To-Do_List_Application
   ```
2. Launch the CLI program:
   ```powershell
   python todo_list.py
   ```
3. Interact with the 9-option menu:
   ```text
   ========== TO-DO LIST ==========
   1. Add Task
   2. View Tasks
   3. Set Task Status
   4. Edit Task
   5. Delete Task
   6. Search Tasks
   7. Filter Tasks
   8. Sort Tasks
   9. Save and Exit
   Enter your choice (1-9):
   ```

#### Option B: Modern Desktop GUI Application
1. Run the graphical interface:
   ```powershell
   python todo_list_gui.py
   ```
2. The GUI displays tasks from `tasks.json` in a sortable, searchable table with inline task addition, double-click status toggling, and visual priority badges.

#### Option C: Package for Internship Submission
To generate a clean ZIP package (`Task_2_To_Do_List_Application.zip`) directly on your Desktop:
```powershell
python package_submission.py
```

---

## 🧪 Testing and Quality Assurance

A comprehensive unit test suite has been implemented using Python's standard `unittest` framework to verify persistence integrity, legacy migration, input resilience, and sorting algorithms.

### Running Automated Tests

Run the test suite directly from your terminal:

```powershell
python -m unittest test_todo_list.py -v
```

### Test Coverage Summary:
- **`test_load_tasks_nonexistent_file`**: Handles missing database by initializing clean state.
- **`test_save_and_load_tasks_roundtrip`**: Full data integrity roundtrip serialization.
- **`test_atomic_save_tmp_file_cleaned_up`**: Ensures temporary swap file is cleaned up after safe atomic swap.
- **`test_load_tasks_legacy_format_upgrade`**: Upgrades older schema without errors.
- **`test_load_tasks_corrupt_json`**: Fails safely on damaged files without overwriting.
- **`test_load_tasks_non_list_root`**: Validates root collection type constraints.
- **`test_filter_tasks_by_status`**: Validates separate isolation of Pending vs Completed items.
- **`test_search_tasks`**: Verifies case-insensitive substring search matching.
- **`test_sort_tasks_by_priority`**: Validates custom High -> Medium -> Low ranking.
- **`test_sort_tasks_by_due_date`**: Chronological validation with undated items anchored last.
- **`test_sort_tasks_alphabetically`**: Validates A-Z lexical ordering.
- **`test_priority_mapping_constants`**: Validates mapping constants and comparator contracts.

---

## 🛡️ Error Handling & Design Patterns

1. **Atomic File Writes:** Prevents incomplete file truncation if power or execution is interrupted during a write cycle.
2. **Defensive Lookups:** Employs `.get()` with safe defaults so old or externally modified records never trigger `KeyError` crashes.
3. **Safe Deletion with Rollback:** If writing changes to disk fails during a deletion, the in-memory array restores the removed item.
4. **Boundary Validation:** Prevents index errors when selecting tasks by converting 1-based user input into checked zero-based indices.

---

## 👨‍💻 Author & Internship Details

- **Intern Name:** Python Development Intern
- **Company:** Auspify Technologies
- **Internship Track:** Python Development Internship
- **Task Number:** Task 2 — To-Do List Application
