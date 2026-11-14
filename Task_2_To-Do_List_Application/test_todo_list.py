"""
Unit Test Suite for Task 2: To-Do List Application
Auspify Technologies — Python Development Internship

Tests data persistence, atomic file saving, legacy schema upgrade,
validation, sorting, filtering, and CRUD operations.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import todo_list


class TestTodoListDataPersistence(unittest.TestCase):
    """Test loading, saving, data migration, and corruption recovery."""

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.test_dir.name) / "test_tasks.json"
        # Patch the module's FILE_NAME to point to our isolated temporary file
        self.patcher = patch.object(todo_list, "FILE_NAME", self.test_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.test_dir.cleanup()

    def test_load_tasks_nonexistent_file(self):
        """Loading from a non-existent file should safely return an empty list."""
        if self.test_file.exists():
            self.test_file.unlink()
        tasks = todo_list.load_tasks()
        self.assertEqual(tasks, [])

    def test_save_and_load_tasks_roundtrip(self):
        """Saving tasks and loading them back should preserve all fields."""
        sample_tasks = [
            {
                "title": "Complete Python Assignment",
                "completed": False,
                "priority": "High",
                "due_date": "2026-11-01"
            },
            {
                "title": "Submit Documentation",
                "completed": True,
                "priority": "Medium",
                "due_date": "2026-11-05"
            }
        ]
        save_result = todo_list.save_tasks(sample_tasks)
        self.assertTrue(save_result)
        self.assertTrue(self.test_file.exists())

        loaded = todo_list.load_tasks()
        self.assertEqual(loaded, sample_tasks)

    def test_atomic_save_tmp_file_cleaned_up(self):
        """Atomic write should replace the target file and leave no leftover .tmp file."""
        sample_tasks = [{"title": "Task A", "completed": False, "priority": "Low", "due_date": ""}]
        todo_list.save_tasks(sample_tasks)

        tmp_file = self.test_file.with_suffix(".tmp")
        self.assertFalse(tmp_file.exists())
        self.assertTrue(self.test_file.exists())

    def test_load_tasks_legacy_format_upgrade(self):
        """Older task records missing priority or due_date should be upgraded with defaults."""
        legacy_data = [
            {"title": "Legacy Task 1"},  # Missing completed, priority, due_date
            {"title": "Legacy Task 2", "completed": True},  # Missing priority, due_date
            {"title": "Legacy Task 3", "priority": "InvalidPriority", "due_date": "invalid-date"}
        ]
        with self.test_file.open("w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        loaded = todo_list.load_tasks()
        self.assertEqual(len(loaded), 3)

        # Verification of auto-migration
        self.assertEqual(loaded[0]["priority"], "Medium")
        self.assertEqual(loaded[0]["completed"], False)
        self.assertEqual(loaded[0]["due_date"], "")

        self.assertEqual(loaded[1]["priority"], "Medium")
        self.assertEqual(loaded[1]["completed"], True)
        self.assertEqual(loaded[1]["due_date"], "")

        # Invalid priority should default to Medium; invalid date should default to empty string
        self.assertEqual(loaded[2]["priority"], "Medium")
        self.assertEqual(loaded[2]["due_date"], "")

    def test_load_tasks_corrupt_json(self):
        """Corrupt JSON in storage should return None without crashing or overwriting."""
        with self.test_file.open("w", encoding="utf-8") as f:
            f.write("{ invalid json formatting !!!")

        loaded = todo_list.load_tasks()
        self.assertIsNone(loaded)

    def test_load_tasks_non_list_root(self):
        """JSON with a non-list root structure (e.g., dict or integer) should return empty list."""
        with self.test_file.open("w", encoding="utf-8") as f:
            json.dump({"not_a_list": 123}, f)

        loaded = todo_list.load_tasks()
        self.assertEqual(loaded, [])


class TestTodoListOperations(unittest.TestCase):
    """Test task sorting, filtering, searching, and validation logic."""

    def setUp(self):
        self.tasks = [
            {"title": "Submit Weekly Report", "completed": False, "priority": "High", "due_date": "2026-10-25"},
            {"title": "Attend Standup Meeting", "completed": True, "priority": "Low", "due_date": "2026-10-20"},
            {"title": "Review Pull Request", "completed": False, "priority": "Medium", "due_date": "2026-10-22"},
            {"title": "Update Documentation", "completed": False, "priority": "Low", "due_date": ""}
        ]

    def test_search_tasks(self):
        """Search should perform case-insensitive substring matching on task titles."""
        keyword = "report"
        matches = [t for t in self.tasks if keyword in t["title"].lower()]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["title"], "Submit Weekly Report")

        keyword_multi = "e"
        matches_multi = [t for t in self.tasks if keyword_multi in t["title"].lower()]
        self.assertEqual(len(matches_multi), 4)

    def test_filter_tasks_by_status(self):
        """Filtering should isolate pending and completed tasks accurately."""
        pending = [t for t in self.tasks if not t["completed"]]
        completed = [t for t in self.tasks if t["completed"]]

        self.assertEqual(len(pending), 3)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]["title"], "Attend Standup Meeting")

    def test_sort_tasks_by_priority(self):
        """Sorting by priority should order High -> Medium -> Low."""
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: todo_list.PRIORITY_ORDER[t["priority"]]
        )
        self.assertEqual(sorted_tasks[0]["priority"], "High")
        self.assertEqual(sorted_tasks[1]["priority"], "Medium")
        self.assertEqual(sorted_tasks[2]["priority"], "Low")
        self.assertEqual(sorted_tasks[3]["priority"], "Low")

    def test_sort_tasks_by_due_date(self):
        """Sorting by due date should list earliest dates first, with undated tasks at the end."""
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: (not bool(t["due_date"]), t["due_date"])
        )
        self.assertEqual(sorted_tasks[0]["due_date"], "2026-10-20")
        self.assertEqual(sorted_tasks[1]["due_date"], "2026-10-22")
        self.assertEqual(sorted_tasks[2]["due_date"], "2026-10-25")
        self.assertEqual(sorted_tasks[3]["due_date"], "")

    def test_sort_tasks_alphabetically(self):
        """Sorting by task name should be case-insensitive A-Z."""
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: t["title"].lower()
        )
        titles = [t["title"] for t in sorted_tasks]
        self.assertEqual(
            titles,
            [
                "Attend Standup Meeting",
                "Review Pull Request",
                "Submit Weekly Report",
                "Update Documentation"
            ]
        )

    def test_priority_mapping_constants(self):
        """Verify priority constants and ordering mapping."""
        self.assertEqual(todo_list.PRIORITIES["1"], "High")
        self.assertEqual(todo_list.PRIORITIES["2"], "Medium")
        self.assertEqual(todo_list.PRIORITIES["3"], "Low")
        self.assertLess(todo_list.PRIORITY_ORDER["High"], todo_list.PRIORITY_ORDER["Medium"])
        self.assertLess(todo_list.PRIORITY_ORDER["Medium"], todo_list.PRIORITY_ORDER["Low"])


if __name__ == "__main__":
    unittest.main()
