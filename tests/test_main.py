import io
import main
import os
import unittest
import unittest.mock
from contextlib import redirect_stdout
import src.task_manager as task_manager
import src.file_handler as file_handler


TEST_FILE = "test.bin_prior_to_testing"


class TestTaskApp(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for the Task Manager Textual User Interface (TUI).
    Tested functionality includes adding tasks, listing tasks, and deleting
    through the 3 methods TUI allows.
    Due to how textual's Pilot controls the app in test_run() mode
    this test class must derive from IsolatedAsyncioTestCase and
    the test methods are asynchronous.
    """

    def setUp(self):
        """
        Set up the test environment by backing up the original task binary file.
        """
        self.maxDiff = 5  # make unittest show all diff text
        self.original_file = "tasks.bin"
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        if os.path.exists("tasks.bin"):
            os.rename("tasks.bin", TEST_FILE)

    def tearDown(self):
        """
        Clean up the test environment by removing any test-created binary files
        and restoring the original task binary file.
        """
        if os.path.exists("tasks.bin"):
            os.remove("tasks.bin")
        if os.path.exists(TEST_FILE):
            os.rename(TEST_FILE, "tasks.bin")

    # async def test_main_tui_add_task(self):

    async def test_main_tui_list_task(self):
        """
        Test that after adding a new task (using unittest.mock), it is correctly
        displayed.
        Verify that the sole task has the due_date in correct column and the list size
        increased.
        """
        inputs = ["1", "Title", "description", "01-02-2026", "3", "4"]
        out = io.StringIO()
        with (unittest.mock.patch("builtins.input",
                                  side_effect=inputs), redirect_stdout(out)):
            main.main()

        app = main.TaskApp()
        async with app.run_test() as pilot:
            # There is nothing to do here, as tasks are always listed.
            await pilot.pause()
            self.assertEqual(1, len(app._tasks))
            self.assertIn("01-02-2026", out.getvalue())
            row = app.query_one("VerticalScroll").query(".task-row").first()
            cell = row.query_one(".col-due-date")
            self.assertEqual("01-02-2026", str(cell.content))

    async def test_main_tui_delete_task_by_key_d(self):
        """
        Test that after adding a new task (working directly through
        task_manager.add_task()), it is correctly deleted.
        Activate the deletion by focusing the row and simulating key_d.
        """
        self.tasks = []
        result = task_manager.add_task(self.tasks, "Test Task",
                                       "Description", "01-02-2026")
        self.assertTrue(result)
        self.assertEqual(1, len(self.tasks))
        file_handler.save_tasks(self.tasks)

        app = main.TaskApp()
        async with app.run_test() as pilot:
            self.assertEqual(1, len(app._tasks))
            await pilot.press("tab", "d")
            await pilot.pause()
            self.assertEqual(0, len(app._tasks))
            self.assertEqual(0, len(app.query_one("VerticalScroll").
                                    query(".task-row")), "len(tasklist)")

    async def test_main_tui_delete_task_by_key_enter(self):
        """
        Test that after adding a new task (working directly through
        task_manager.add_task()), it is correctly deleted.
        Activate the deletion by focusing the row and simulating key_enter.
        """
        self.tasks = []
        result = task_manager.add_task(self.tasks, "Test Task",
                                       "Description", "01-02-2026")
        self.assertTrue(result)
        self.assertEqual(1, len(self.tasks))
        file_handler.save_tasks(self.tasks)

        app = main.TaskApp()
        async with app.run_test() as pilot:
            self.assertEqual(1, len(app._tasks))
            await pilot.press("tab", "enter")
            await pilot.pause()
            self.assertEqual(0, len(app._tasks))
            self.assertEqual(0, len(app.query_one("VerticalScroll").
                                    query(".task-row")), "len(tasklist)")

    async def test_main_tui_delete_task_by_click(self):
        """
        Test that after adding a new task (working directly through
        task_manager.add_task()), it is correctly deleted.
        Activate the deletion by clicking the delete button.
        """
        self.tasks = []
        result = task_manager.add_task(self.tasks, "Test Task",
                                       "Description", "01-02-2026")
        self.assertTrue(result)
        self.assertEqual(1, len(self.tasks))
        file_handler.save_tasks(self.tasks)

        app = main.TaskApp()
        async with app.run_test() as pilot:
            self.assertEqual(1, len(app._tasks))
            await pilot.click("#delete-0")
            await pilot.pause()
            self.assertEqual(0, len(app._tasks))
            self.assertEqual(0, len(app.query_one("VerticalScroll").
                                    query(".task-row")), "len(tasklist)")


if __name__ == '__main__':
    unittest.main()
