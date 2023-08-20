from rich.console import RenderableType
from rich.table import Table
from textual.reactive import Reactive
from textual.widgets import Static

from myning.formatter import Colors


class Question(Static):
    message: Reactive[RenderableType] = Reactive("", layout=True)  # type:ignore
    subtitle: Reactive[RenderableType] = Reactive("", layout=True)  # type: ignore

    def render(self):
        table = Table.grid()
        table.add_column(overflow="fold")

        if isinstance(self.message, str):
            self.message = f"[bold]{self.message}[/]"
        table.add_row(self.message)

        if self.subtitle:
            if isinstance(self.subtitle, str):
                self.subtitle = f"[{Colors.LOCKED}]{self.subtitle}[/]"
            table.add_row(self.subtitle)

        return table
