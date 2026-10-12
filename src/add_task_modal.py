from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Horizontal, VerticalGroup
from textual.validation import Function
from datetime import datetime


class AddTaskModal(ModalScreen):
    CSS_PATH = "add-task-modal.tcss"
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, tasks, **kwargs):
        super().__init__(**kwargs)
        self._tasks = tasks

    def title_is_unique(self, value: str) -> bool:
        return not any(value.strip().casefold() == t.title.casefold() for t in self._tasks)

    def date_is_valid(self, value: str) -> bool:
        try:
            datetime.strptime(value.strip(), "%d-%m-%Y")
        except ValueError:
            return False
        return True

    def compose(self) -> ComposeResult:
        with VerticalGroup(classes="task-row"):
            yield Label("Add task")
            yield Input(placeholder="Title", id="title", classes="col-field",
                        validators=[Function(self.title_is_unique, "Error: A task with this title already exists.")])
            yield Input(placeholder="Due date (DD-MM-YYYY)", id="due-date",
                        classes="col-field", restrict=r"[0-9-]*",
                        validators=[Function(self.date_is_valid, "Error: Invalid date format. Use DD-MM-YYYY.")])
            yield Input(placeholder="Status", id="status", classes="col-field")
            yield Input(placeholder="Task Description", id="description",
                        classes="col-field")
            with Horizontal(classes="buttons"):
                cancel = Button("Cancel", id="cancel", classes="Button")
                cancel.can_focus = False
                yield cancel
                yield Button("Add", id="add", classes="Button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            self.action_add()
        else:
            self.action_cancel()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_add(self) -> None:
        for field in self.query(Input):
            result = field.validate(field.value)
            if result is not None and not result.is_valid:
                field.focus()
                return
        results = {"title": self.query_one("#title").value,
                   "due_date": self.query_one("#due-date").value,
                   "status": self.query_one("#status").value,
                   "description": self.query_one("#description").value}
        self.dismiss(results)
