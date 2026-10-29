import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from services.task_service import TaskService


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TaskTrackerTests(unittest.TestCase):
    def setUp(self):
        self.original_directory = Path.cwd()
        self.temporary_directory = tempfile.TemporaryDirectory()
        os.chdir(self.temporary_directory.name)
        self.service = TaskService()

    def tearDown(self):
        os.chdir(self.original_directory)
        self.temporary_directory.cleanup()

    def test_creates_json_and_adds_serializable_task(self):
        task = self.service.add_task({"description": "First task"})

        self.assertEqual(task["id"], 1)
        self.assertEqual(task["status"], "todo")
        self.assertTrue(Path("tasks.json").exists())
        stored_tasks = json.loads(Path("tasks.json").read_text(encoding="utf-8"))
        self.assertEqual(stored_tasks, [task])

    def test_update_and_status_change_preserve_other_fields(self):
        task = self.service.add_task({"description": "First task"})
        in_progress = self.service.mark_task_in_progress(task["id"])
        updated = self.service.update_task(
            task["id"], {"description": "Updated task"}
        )

        self.assertEqual(in_progress["status"], "in-progress")
        self.assertEqual(updated["status"], "in-progress")
        self.assertEqual(updated["createdAt"], task["createdAt"])
        self.assertEqual(updated["description"], "Updated task")

    def test_filters_and_ids_after_deletion(self):
        first = self.service.add_task({"description": "First"})
        self.service.mark_task_in_progress(first["id"])
        self.service.add_task({"description": "Second"})
        self.service.mark_task_done(2)
        self.service.delete_task(1)
        third = self.service.add_task({"description": "Third"})

        self.assertEqual(third["id"], 3)
        self.assertEqual(
            [task["status"] for task in self.service.get_tasks_by_status("done")],
            ["done"],
        )
        self.assertEqual(
            [
                task["status"]
                for task in self.service.get_tasks_by_status("in-progress")
            ],
            [],
        )

    def test_rejects_empty_description_and_reports_missing_task(self):
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            self.service.add_task({"description": "  "})
        self.assertIsNone(self.service.update_task(99, {"description": "Missing"}))
        self.assertFalse(self.service.delete_task(99))

    def test_cli_uses_current_directory_for_persistence(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"), "add", "CLI task"],
            cwd=self.temporary_directory.name,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Added task 1", result.stdout)
        stored_tasks = json.loads(Path("tasks.json").read_text(encoding="utf-8"))
        self.assertEqual(stored_tasks[0]["description"], "CLI task")

    def test_cli_commands_and_status_filters(self):
        def run_cli(*arguments):
            return subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "main.py"), *arguments],
                cwd=self.temporary_directory.name,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(run_cli("add", "First task").returncode, 0)
        self.assertEqual(run_cli("mark-in-progress", "1").returncode, 0)
        self.assertEqual(run_cli("add", "Second task").returncode, 0)
        self.assertEqual(run_cli("mark-done", "2").returncode, 0)
        self.assertEqual(run_cli("add", "Todo task").returncode, 0)

        not_done = run_cli("list", "not-done")
        self.assertEqual(not_done.returncode, 0, not_done.stderr)
        self.assertIn("First task", not_done.stdout)
        self.assertIn("Todo task", not_done.stdout)
        self.assertNotIn("Second task", not_done.stdout)

        in_progress = run_cli("list-in-progress")
        self.assertEqual(in_progress.returncode, 0, in_progress.stderr)
        self.assertIn("First task", in_progress.stdout)
        self.assertNotIn("Todo task", in_progress.stdout)

        done = run_cli("list-done")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("Second task", done.stdout)
        self.assertNotIn("First task", done.stdout)

        updated = run_cli("update", "1", "Updated task")
        self.assertEqual(updated.returncode, 0, updated.stderr)
        deleted = run_cli("delete", "2")
        self.assertEqual(deleted.returncode, 0, deleted.stderr)
        all_tasks = run_cli("list")
        self.assertIn("Updated task", all_tasks.stdout)
        self.assertIn("Todo task", all_tasks.stdout)
        self.assertNotIn("Second task", all_tasks.stdout)

    def test_invalid_json_is_reported_without_traceback(self):
        Path("tasks.json").write_text("{invalid", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"), "list"],
            cwd=self.temporary_directory.name,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("contains invalid JSON", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
