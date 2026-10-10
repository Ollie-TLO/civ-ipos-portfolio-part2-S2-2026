import io
import main
import os
import unittest
import unittest.mock
from contextlib import redirect_stdout
import src.task_manager as task_manager
import src.file_handler as file_handler


TEST_FILE = "test.bin_prior_to_testing"


# class TestTaskApp(unittest.IsolatedAsyncioTestCase):
#     async def test_starts_empty(self):
#         app = TaskApp()
#         async with app.run_test() as pilot:
#             await pilot.pause()
#             self.assertEqual(len(app.query(".tasklist Button")), 0)

class TestTaskApp(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """
        Set up the test environment by initialising an empty task list
        and backing up the original task binary file.
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

    # async def test_main_tui_list_task(self):

    async def test_main_tui_list_task(self):
        """
        Test that after adding a new task (using unittest.mock), it is
        correctly displayed.
        Verify that the sole task has the due_date in correct column and
        the list size increased.
        """
        inputs = ["1", "Title", "description", "01-02-2026", "3", "4"]
        out = io.StringIO()
        with (unittest.mock.patch("builtins.input", side_effect=inputs),
              redirect_stdout(out)):
            main.main()

        app = main.TaskApp()
        async with app.run_test() as pilot:
            # await pilot.press("a", "enter")
            await pilot.pause()
            self.assertEqual(1, len(app._tasks))
            self.assertIn("01-02-2026", out.getvalue())

            row = app.query_one("VerticalScroll").query(".task-row").first()
            cell = row.query_one(".col-due-date")
            self.assertEqual("01-02-2026", str(cell.content))


    async def test_main_tui_delete_task(self):
        """
        Test that after adding a new task (using unittest.mock), it is
        correctly displayed.
        Verify that the sole task has the due_date in correct column and
        the list size increased.
        """
        self.tasks = []
        result = task_manager.add_task(self.tasks, "Test Task", "Description", "01-02-2026")
        self.assertTrue(result)
        self.assertEqual(1, len(self.tasks))
        # FIXME How can the task_manager.save_tasks work?
        file_handler.save_tasks(self.tasks)
        task_manager.save_tasks(self.tasks)

        app = main.TaskApp()
        async with app.run_test() as pilot:
            self.assertEqual(1, len(app._tasks))
            await pilot.press("tab", "d")
            await pilot.pause()
            self.assertEqual(0, len(app._tasks))
            self.assertEqual(0, len(app.query_one("VerticalScroll").query(".task-row")), "len(tasklist)")


if __name__ == '__main__':
    unittest.main()
