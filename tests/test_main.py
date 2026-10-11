import main
import os
import textwrap
import unittest
from click.testing import CliRunner
from pathlib import Path

TEST_FILE = "test.bin_prior_to_testing"


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

    def test_main_cli_no_args(self):
        """
        Test providing no args at all.
        Verify that 'old-style' interactive task manager activates.
        """
        result = self.runner.invoke(main.command_line_handler)
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
        result = self.runner.invoke(main.command_line_handler, input="1\nTitle\nDescription\n20-05-2025\nP\n4\n")
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
