from src.task_manager import add_task, delete_task, list_tasks
from src.file_handler import load_tasks
import sys
import textual
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static
from textual.containers import HorizontalScroll

class TaskApp(App):
    tasks = load_tasks()

    BINDINGS = [("a", "add_task", "Add Task"),
                ("d", "delete_task", "Delete Task"),
                ("l", "list_tasks", "List Tasks")]

    def compose(self) -> ComposeResult:
        yield Header()
        for index, task in enumerate(self.tasks):
            with HorizontalScroll():
                yield Button("X", id="delete"+str(index), variant="error")
                yield Static(task.title, id="delete")
                
        yield Footer()


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


if __name__ == "__main__":
    #main()
    TaskApp().run()
