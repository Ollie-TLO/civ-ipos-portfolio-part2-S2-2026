from src.task_manager import add_task, delete_task, list_tasks
from src.file_handler import load_tasks
import sys
import textual
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static
from textual.containers import Container, HorizontalGroup, VerticalScroll

class TaskApp(App):
    #tasks = load_tasks()
    
    CSS_PATH = "task-app.tcss"
    
    BINDINGS = [("a", "add_task", "Add Task"),
                ("d", "delete_task", "Delete Task"),
                ("l", "list_tasks", "List Tasks")]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tasks = load_tasks()
        
    def compose(self) -> ComposeResult:
        yield Header()
        with HorizontalGroup(classes="task-header"):
            yield Static("Title", id="title", classes="col-title")
            yield Static("Description", id="description", classes="col-description")
            yield Static("Due date", id="due_date", classes="col-due-date")
            yield Static("Status", id="status", classes="col-status")
            yield Static("Delete", id="delete", classes="col-delete")
        for index, task in enumerate(self._tasks):
            with HorizontalGroup(classes="task-row"):
                yield Static(task.title, id="title", classes="col-title")
                yield Static(task.description, id="description", classes="col-description")
                yield Static(task.due_date, id="due_date", classes="col-due-date")
                yield Static(task.status, id="status", classes="col-status")
                with Container(classes="col-delete"):
                    yield Button("X", id="delete"+str(index), variant="error")
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
