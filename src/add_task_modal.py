from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Container, Horizontal, HorizontalGroup, VerticalGroup


class AddTaskModal(ModalScreen):
    CSS_PATH = "add-task-modal.tcss"
    BINDINGS = [("escape", "cancel", "Cancel")]
    
    def compose(self) -> ComposeResult:
        with VerticalGroup(classes="task-row"):
            yield Label("Add task")
            yield Input(placeholder="Title", id="title", classes="col-field")
            yield Input(placeholder="Due date (DD-MM-YYYY)", id="due-date", classes="col-field", restrict=r"[0-9-]*")
            yield Input(placeholder="Status", id="status", classes="col-field")
            yield Input(placeholder="Task Description", id="description", classes="col-field")
            with Horizontal(classes="buttons"):
                yield Button("Cancel", id="cancel", classes="Button")
                yield Button("Add", id="add", classes="Button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            results = {"title": self.query_one("#title").value,
                       "due-date": self.query_one("#due-date").value,
                       "status": self.query_one("#status").value,
                       "description": self.query_one("#description").value
                    }
            self.action_add(results)
        else:
            self.action_cancel(None)

    def action_cancel(self) -> None:
        print("Cancele)
        self.dismiss(None)
    
    def action_add(self, results) -> None:
        print("ADD")
        self.dismiss(results)
