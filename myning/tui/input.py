from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.validation import Number, Length
from textual.widgets import Input, Static

from myning.utilities.formatter import Formatter


class IntInput(Input):
    def validate_value(self, value: str):
        value = value.strip()
        if (
            value
            and value[-1] == "q"
            and (screen := self.app.query("IntInputScreen")[0])
            and isinstance(screen, IntInputScreen)
        ):
            screen.action_cancel()
        elif value:
            try:
                int(value)
            except ValueError:
                return self.value
        return value


class IntInputScreen(ModalScreen[int | None]):
    BINDINGS = [("escape", "cancel", "cancel")]

    def __init__(
        self,
        question: str,
        *,
        placeholder: str | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        self.question = question
        self.input = IntInput(
            placeholder=placeholder or "",
            validators=[Number(minimum=minimum, maximum=maximum)],
        )
        if minimum is not None and maximum is not None:
            error = f"Please enter a number between {minimum} and {maximum}"
        elif minimum is not None:
            error = f"Please enter a number greater than or equal to {minimum}"
        elif maximum is not None:
            error = f"Please enter a number less than or equal to {maximum}"
        else:
            error = ""
        self.error = Static(error, id="error")
        super().__init__()

    def compose(self):
        with Vertical():
            yield Static(self.question)
            yield self.input
            yield Static(Formatter.locked("Press escape or q to cancel"))

    def on_input_changed(self):
        self.error.remove()

    def on_input_submitted(self, event: Input.Submitted):
        if event.validation_result and event.validation_result.is_valid:
            self.dismiss(int(event.value))
        else:
            self.query_one("Vertical").mount(self.error, before=-1)

    def action_cancel(self):
        self.dismiss(None)


class LoginFormScreen(ModalScreen[str | None]):
    BINDINGS = [("escape", "cancel", "cancel")]

    def __init__(self, question: str) -> None:
        self.question = question
        self.username_input = Input(placeholder="Username" or "", validators=[Length(1)])
        self.password_input = Input(placeholder="Password" or "", validators=[Length(1)])
        super().__init__()

    def compose(self):
        with Vertical():
            yield Static(self.question)
            yield self.username_input
            yield self.password_input
            yield Static(Formatter.locked("Press escape or q to cancel"))

    def on_input_submitted(self, event: Input.Submitted):
        username = self.username_input.value
        password = self.password_input.value
        if not password:
            self.focus_next()
            return
        if event.validation_result and event.validation_result.is_valid:
            self.dismiss((username, password))
        else:
            self.query_one("Vertical").mount(self.error, before=-1)

    def action_cancel(self):
        self.dismiss(None)
