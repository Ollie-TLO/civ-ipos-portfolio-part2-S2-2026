import main
import os
import textwrap
import unittest
from click.testing import CliRunner


TEST_FILE = "test_preserved while testing.bin"


class TestMain(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment by initialising an empty task list
        and backing up the original task binary file.
        """
        self.runner = CliRunner()
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


    def testMainCliCreateTask(self):
        """
        Test adding a new task to the task list via command line
        Verify that the task is successfully added and the list size increases.
        """
        result = self.runner.invoke(main.command_line_handler, ['-a', 'Title', '15-05-2025', "Task description"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output)

        result = self.runner.invoke(main.command_line_handler, ['-l'])
        self.assertEqual(0, result.exit_code)
        expected_outcome = "Title | Task description | Due: 15-05-2025 | Status: pending" + "\n"
        self.assertEqual(expected_outcome, result.output)


if __name__ == '__main__':
    unittest.main()
