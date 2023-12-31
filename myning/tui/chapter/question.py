from rich.console import RenderableType
from rich.table import Table
from textual.reactive import Reactive
from textual.widgets import Static

from myning.utilities.ui import Colors


class Question(Static):
    message: Reactive[RenderableType] = Reactive("", layout=True)  # type:ignore
    subtitle: Reactive[RenderableType] = Reactive("", layout=True)  # type: ignore

    def render(self):
        table = Table.grid()
        table.add_column(overflow="fold")
        table.add_row(f"[bold]{self.message}[/]" if isinstance(self.message, str) else self.message)

        if self.subtitle:
            if isinstance(self.subtitle, str):
                self.subtitle = Colors.LOCKED(self.subtitle)
            table.add_row(self.subtitle)

        return table
