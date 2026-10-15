import io
import main
import os
import textwrap
import unittest
import unittest.mock
from contextlib import redirect_stdout
import src.task_manager as task_manager
import src.file_handler as file_handler
from click.testing import CliRunner
from pathlib import Path

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

    async def test_main_tui_add_task(self):
        """
        Test adding a new task to the task list via the TUI, keyboard driven
        Verify that the task is successfully added and the list size increases.
        """
        inputs = ("a", *"This title",
                  "tab", *"13-12-2028",
                  "tab", *"urgent",
                  "tab", *"Long, wordy prose here.",
                  "tab", "enter")
        app = main.TaskApp()
        async with app.run_test() as pilot:
            self.assertEqual(0, len(app._tasks))
            self.assertEqual(0, len(app.query_one("VerticalScroll").
                                    query(".task-row")), "len(tasklist)")
            await pilot.press(*inputs)
            await pilot.pause()
            self.assertEqual(1, len(app._tasks))
            self.assertEqual(1, len(app.query_one("VerticalScroll").
                                    query(".task-row")), "len(tasklist)")
            self.assertEqual(1, len(app._tasks))
            row = app.query_one("VerticalScroll").query(".task-row").first()
            cell = row.query_one(".col-due-date")
            self.assertEqual("13-12-2028", str(cell.content))

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
            main.classic_ui()

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


class TestMainCli(unittest.TestCase):
    """
    Unit tests for Task Manager command line arguments functionality including adding, deleting, listing, filtering,
    and persisting tasks to and from a binary file.
    click provides CliRunner for this.
    Note that EOF on unix is 0x04 (ctrl-d) on windows it is 0x1a (ctrl-z),
    although that is not necessary in these tests.
    it must follow and precede '\n'
    """

    def setUp(self):
        """
        Set up the test environment by initialising an empty task list
        and backing up the original task binary file.
        """
        self.runner = CliRunner()
        self.maxDiff = None  # make unittest show all diff text
        self.original_file = "tasks.bin"
        Path(TEST_FILE).unlink(missing_ok=True)
        if os.path.exists("tasks.bin"):
            os.rename("tasks.bin", TEST_FILE)

    def tearDown(self):
        """
        Clean up the test environment by removing any test-created binary files
        and restoring the original task binary file.
        """
        Path("tasks.bin").unlink(missing_ok=True)
        if os.path.exists(TEST_FILE):
            os.rename(TEST_FILE, "tasks.bin")

    def test_main_cli_create_task(self):
        """
        Test adding a new task to the task list via command line
        Verify that the task is successfully added and the list size increases.
        """
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-11-2026', "Task description"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output)

        result = self.runner.invoke(main.command_line_handler, ['-l'])
        self.assertEqual(0, result.exit_code)
        expected_outcome = ("Title | Task description | Due: 15-11-2026 | Status: pending" + "\n")
        self.assertEqual(expected_outcome, result.output)

    def test_main_cli_list_task(self):
        """
        Test the list via command line
        Verify that the task is displayed.
        """
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-11-2026', "Task description"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output)

        result = self.runner.invoke(main.command_line_handler, ['-l'])
        self.assertEqual(0, result.exit_code)
        expected_outcome = "Title | Task description | Due: 15-11-2026 | Status: pending\n"
        self.assertEqual(expected_outcome, result.output)

    def test_main_cli_delete_task(self):
        """
        Test the delete task via command line.
        Verify it is actually gone.
        """
        self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-11-2026', "Task description"])

        result = self.runner.invoke(main.command_line_handler, ['-d', 'Title'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("Task deleted successfully.\n", result.output)
        # Verify that it is really gone.
        result = self.runner.invoke(main.command_line_handler, ['-l'])
        self.assertEqual(0, result.exit_code)
        expected_outcome = "No tasks found.\n"
        self.assertEqual(expected_outcome, result.output)

    def test_main_cli_add_duplicate_task(self):
        """
        Test adding a duplicate task with the same title.
        Verify that duplicates are not allowed.
        """
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-11-2026', "Task description"])
        self.assertEqual(0, result.exit_code)

        # Add the task a second time
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-11-2026', "Task description"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("Error: A task with this title already exists.\n", result.output)

        # Check that it _was_ added only once
        result = self.runner.invoke(main.command_line_handler, ['-l'])
        expected_outcome = "Title | Task description | Due: 15-11-2026 | Status: pending\n"
        self.assertEqual(expected_outcome, result.output)

    def test_main_cli_add_invalid_due_date(self):
        """
        Test adding a task with an invalid due date format.
        Verify that the task is rejected.
        """
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-15-2026', "Task description"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("Error: Invalid date format. Use DD-MM-YYYY.\n", result.output)

    def test_main_cli_add_invalid_args(self):
        """
        Test running with invalid args.
        """
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-11-2026', 'Task description', '-l'])
        self.assertEqual(2, result.exit_code)
        self.assertEqual("Usage: taskman [OPTIONS]\n"
                         "Try 'taskman --help' for help.\n\n"
                         "Error: Choose only one of <-a|-l|-d|--classic>\n", result.output)

    def test_main_cli_classic(self):
        """
        Test triggering old-style CLI.
        Verify that 'old-style' interactive task manager activates.
        """
        result = self.runner.invoke(main.command_line_handler, ['--classic'])
        self.assertEqual(1, result.exit_code)
        self.assertEqual("\nTask Manager CLI\n"
                         "1. Add Task\n"
                         "2. Delete Task\n"
                         "3. List Tasks\n"
                         "4. Exit\n"
                         "Enter your choice: \n"
                         "Aborted!\n", result.output)


class TestClassic(unittest.TestCase):
    """
    Unit tests for classic Task Manager interactive mode
    """

    def setUp(self):
        """
        Set up the test environment by initialising an empty task list
        and backing up the original task binary file.
        """
        self.runner = CliRunner()
        self.maxDiff = None  # make unittest show all diff text
        self.original_file = "tasks.bin"
        Path(TEST_FILE).unlink(missing_ok=True)
        if os.path.exists("tasks.bin"):
            os.rename("tasks.bin", TEST_FILE)

    def tearDown(self):
        """
        Clean up the test environment by removing any test-created binary files
        and restoring the original task binary file.
        """
        Path("tasks.bin").unlink(missing_ok=True)
        if os.path.exists(TEST_FILE):
            os.rename(TEST_FILE, "tasks.bin")

    def test_classic_add_task(self):
        """
        Test adding a new task to the task list via classic mode.
        Verify zero return code and that output matches expectations.
        """

        result = self.runner.invoke(main.command_line_handler, ['--classic'], input="1\nTitle\nDescription\n20-05-2025\nP\n4\n")
        self.assertEqual(0, result.exit_code)
        expected_outcome = textwrap.dedent("""
            Task Manager CLI
            1. Add Task
            2. Delete Task
            3. List Tasks
            4. Exit
            Enter your choice: Title: Description: Due Date (DD-MM-YYYY): """ """
            Task Manager CLI
            1. Add Task
            2. Delete Task
            3. List Tasks
            4. Exit
            Enter your choice: Invalid choice. Try again.

            Task Manager CLI
            1. Add Task
            2. Delete Task
            3. List Tasks
            4. Exit
            Enter your choice: Exiting Task Manager.
            """)
        self.assertEqual(expected_outcome, result.output)


if __name__ == '__main__':
    unittest.main()
