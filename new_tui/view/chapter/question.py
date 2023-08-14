from rich.console import RenderableType
from rich.table import Table
from textual.reactive import Reactive
from textual.widgets import Static

from new_tui.formatter import Colors


class Question(Static):
    message = Reactive("", layout=True)
    subtitle: Reactive[RenderableType] = Reactive("", layout=True)  # type: ignore

    def render(self):
        table = Table.grid()
        table.add_column(overflow="fold")
        table.add_row(f"[bold]{self.message}[/]")
        if self.subtitle:
            if isinstance(self.subtitle, str):
                self.subtitle = f"[{Colors.LOCKED}]{self.subtitle}[/]"
            table.add_row(self.subtitle)
        return table
