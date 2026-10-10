from src.task_manager import add_task, delete_task, list_tasks
from src.file_handler import load_tasks
import sys
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static
from textual.containers import Container, HorizontalGroup, VerticalScroll


class DeleteButton(Button):
    """
    Button subclass purely to add the key binding and task index. The binding
    is only active when a tasks delete button is pressed.
    """
    BINDINGS = [("d", "app.delete_task", "Delete Task")]

    def __init__(self, label, index, **kwargs):
        super().__init__(label, **kwargs)
        self.index = index


class TaskList(Container, can_focus=False):
    """
    Generate a list of task-row's, one per task, for the VerticalScroll.
    """
    def __init__(self, tasks, **kwargs):
        super().__init__(**kwargs)
        self._tasks = tasks

    def compose(self) -> ComposeResult:
        for index, task in enumerate(self._tasks):
            with HorizontalGroup(classes="task-row"):
                yield Static(task.title, id="title", classes="col-title")
                yield Static(task.description, id="description",
                             classes="col-description")
                yield Static(task.due_date, id="due_date", classes="col-due-date")
                yield Static(task.status, id="status", classes="col-status")
                with Container(classes="col-delete"):
                    yield DeleteButton("X", index, id="delete-" + str(index),
                                       variant="error")


class TaskApp(App):
    """
    Main Task Manager App class
    """
    CSS_PATH = "task-app.tcss"
    BINDINGS = [("a", "add_task", "Add Task")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tasks = load_tasks()

    def compose(self) -> ComposeResult:
        """
        Generate the entire screen. Most of the screen is the VerticalScroll
        """
        yield Header()
        with HorizontalGroup(classes="task-header"):
            yield Static("Title", id="title", classes="col-title")
            yield Static("Description", id="description", classes="col-description")
            yield Static("Due date", id="due_date", classes="col-due-date")
            yield Static("Status", id="status", classes="col-status")
            yield Static("Action", id="delete", classes="col-delete")
        with VerticalScroll():
            yield TaskList(self._tasks, classes="task-list")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle delete button press
        """
        if event.button.id and event.button.id.startswith("delete-"):
            try:
                task_index = int(event.button.id.removeprefix("delete-"))
                delete_task(self._tasks, self._tasks[task_index].title)
                self.query_one(".task-list").refresh(recompose=True)
            except ValueError:
                pass

    def action_delete_task(self) -> None:
        """
        Handle delete action, from key_d or k_enter with task focused
        Needs work.
        """
        if self.focused.id and self.focused.id.startswith("delete-"):
            try:
                task_index = int(self.focused.id.removeprefix("delete-"))
                delete_task(self._tasks, self._tasks[task_index].title)
                self.query_one(".task-list").refresh(recompose=True)
            except ValueError:
                pass


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
    if len(sys.argv) == 1:
        TaskApp().run()
    elif len(sys.argv) == 2 and sys.argv[1] == "--classic":
        main()
