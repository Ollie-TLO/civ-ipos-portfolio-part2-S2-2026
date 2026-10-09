from src.task_manager import add_task, delete_task, list_tasks
from src.file_handler import load_tasks
import click


def main():
    tasks = load_tasks()
    while True:
        print("\nTask Manager CLI")
        print("1. Add Task")
        print("2. Delete Task")
        print("3. List Tasks")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            title = input("Title: ")
            description = input("Description: ")
            due_date = input("Due Date (DD-MM-YYYY): ")
            add_task(tasks, title, description, due_date)
        elif choice == "2":
            title = input("Title of the task to delete: ")
            if delete_task(tasks, title):
                print("Task deleted successfully.")
            else:
                print("Task not found.")
        elif choice == "3":
            list_tasks(tasks)
        elif choice == "4":
            print("Exiting Task Manager.")
            break
        else:
            print("Invalid choice. Try again.")


@click.command()
@click.option("-a", "--add",       "add_option", nargs=3,               metavar="<title> <DD-MM-YYYY> <description>", help="Add a new task")  # noqa: E241 E501 B950
@click.option("-l", "--list",     "list_option",          is_flag=True,                                               help="List all tasks")  # noqa: E241 E501 B950
@click.option("-d", "--delete", "delete_option", nargs=1,               metavar="<task title>",                       help="Delete named task")  # noqa: E241 E501 B950
def command_line_handler(add_option, list_option, delete_option):

    options = (add_option, list_option, delete_option)
    count_options = sum(1 for opt in options if opt)

    if 1 < count_options:
        raise click.UsageError("Choose only one of <-a|-l|-f|-d>")
    elif 1 == count_options:
        tasks = load_tasks()
        if add_option:
            title, date, description = add_option
            add_task(tasks, title, description, date)
        elif list_option:
            list_tasks(tasks)
        elif delete_option:
            if delete_task(tasks, delete_option):
                print("Task deleted successfully.")
            else:
                print("Task not found.")
    else:
        # No command line arguments so fall through to original behaviour.
        main()


if __name__ == "__main__":
    command_line_handler()
