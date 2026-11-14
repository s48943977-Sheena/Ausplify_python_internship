# Test Cases — Enhanced To-Do List Application

## Testing Environment

- **Operating System:** Windows 10 / 11
- **Programming Language:** Python 3.10+ (Tested on Python 3.14)
- **IDE / Environment:** Visual Studio Code / Windows PowerShell
- **Architecture:** Pure Standard Library (`json`, `os`, `pathlib`, `datetime`, `unittest`)
- **Data Store:** `tasks.json` (Atomic JSON serialization via `.tmp` swap)

---

## Test Results Summary

| ID | Test Case | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | Application Initialization | Loads existing tasks from `tasks.json` and presents 9-option interactive menu | Menu rendered with options `1` to `9`; active tasks loaded into memory | **Pass** |
| **TC02** | Add New Task (Valid Input) | Prompts for title, priority (1-3), and due date (YYYY-MM-DD); appends and persists task | Task added with status `Pending`, priority `High`, and formatted due date; saved to `tasks.json` | **Pass** |
| **TC03** | Add Task (Empty Title Validation) | Rejects empty or whitespace-only task name with warning | Displays "Task name cannot be empty." and returns safely to menu | **Pass** |
| **TC04** | Explicit Status Update | Prompts for task index, then options `1. Pending` or `2. Completed`; updates status directly | Task completion toggled accurately without confusing index toggle | **Pass** |
| **TC05** | Inline Task Editing | Allows updating title, priority, or date; pressing Enter keeps current value | Modified attributes updated in memory and disk; unmodified fields preserved | **Pass** |
| **TC06** | Task Deletion & Confirmation | Prompts for confirmation (`y/n`); removes task if `y`, cancels if `n` | Task removed from list upon confirmation; cancellation leaves list unchanged | **Pass** |
| **TC07** | Keyword Search | Case-insensitive substring search matching task titles | Returns matching tasks; displays message if no match found | **Pass** |
| **TC08** | Status Filtering | Filters display by `All`, `Pending`, or `Completed` tasks | Accurately renders only tasks meeting the filter condition | **Pass** |
| **TC09** | Multi-Criterion Sorting | Correctly sorts by: (1) Priority (High->Low), (2) Due Date, (3) A-Z Name | Order adheres strictly to priority rank, chronological order, and lexical A-Z | **Pass** |
| **TC10** | Legacy Schema & Corruption Recovery | Upgrades older schema without priority/date; halts safely on corrupted JSON | Older records upgraded with default `Medium` priority; corrupted JSON does not overwrite file | **Pass** |

---

## Detailed Test Logs

### TC01: Application Initialization
- **Input:** Execute `python todo_list.py`
- **Output:** Welcome banner and full 9-item menu rendered.
- **Verification:** Correctly verifies file presence and loads existing tasks into memory without throwing exceptions.

### TC02: Add New Task (Valid Input)
- **Input:**
  - Option: `1`
  - Task name: `Submit Python Internship Report`
  - Priority: `1` (High)
  - Due date: `2026-11-15`
- **Output:** `"Task added and saved successfully!"`
- **Verification:** Inspection of `tasks.json` reveals the newly serialized record matching all attributes.

### TC03: Empty Title Input Handling
- **Input:**
  - Option: `1`
  - Task name: `   ` (whitespace string)
- **Output:** `"Task name cannot be empty."`
- **Verification:** No empty task is added to memory or written to disk; returns cleanly to main loop.

### TC04: Explicit Status Update
- **Input:**
  - Option: `3`
  - Task Number: `1`
  - Status choice: `2` (Completed)
- **Output:** `"Status updated to Completed."`
- **Verification:** Target task `completed` property toggled to `true`. Option `1` switches it back to `Pending` (`false`). Invalid option `0` is gracefully rejected.

### TC05: Inline Task Editing
- **Input:**
  - Option: `4`
  - Task Number: `1`
  - Task name: `[Enter]` (Keep existing)
  - Priority: `2` (Change to Medium)
  - Due date: `[Enter]` (Keep existing)
- **Output:** `"Task updated successfully!"`
- **Verification:** Only priority field was mutated; title and date remained unchanged.

### TC06: Task Deletion & Confirmation
- **Input:**
  - Option: `5`
  - Task Number: `1`
  - Confirmation: `n` -> Output: `"Deletion cancelled."`
  - Confirmation: `y` -> Output: `"Deleted 'Submit Python Internship Report'."`
- **Verification:** Task remains intact on `n` and is permanently purged from memory and `tasks.json` on `y`.

### TC07: Keyword Search
- **Input:**
  - Option: `6`
  - Search keyword: `report`
- **Output:** Displays all tasks containing `"report"` (e.g., `"Submit Python Internship Report"`) regardless of casing.
- **Verification:** Accurate substring filter applied; unrelated tasks excluded from output view.

### TC08: Status Filtering
- **Input:**
  - Option: `7` -> Choice `2` (Pending tasks)
- **Output:** Only tasks with `completed == false` are displayed.
- **Verification:** Completed tasks omitted from view while remaining saved in memory.

### TC09: Multi-Criterion Sorting
- **Input:**
  - Option: `8` -> Choice `1` (Priority: High to Low)
  - Option: `8` -> Choice `2` (Due date: earliest first)
  - Option: `8` -> Choice `3` (Alphabetical: A-Z)
- **Output:** Displayed order reorganizes accurately for each chosen criteria.
- **Verification:** Evaluated against custom priority comparator (`High: 1, Medium: 2, Low: 3`) and ISO date ordering. Tasks without due dates appear at the end.

### TC10: Legacy Schema & Corruption Recovery
- **Input:** Load test file containing `{ "title": "Old Task" }` without `priority` or `due_date`.
- **Output:** Task is automatically upgraded to have `priority: "Medium"` and `due_date: ""` without crashing.
- **Input 2:** Load test file containing malformed JSON syntax.
- **Output:** Warning message displayed; halts execution safely to prevent destroying the user's unreadable file.
- **Verification:** Confirmed 100% pass via automated unit tests in `test_todo_list.py`.
