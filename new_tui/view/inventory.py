from rich.table import Table
from textual.containers import ScrollableContainer
from textual.widgets import Static

from myning.objects.player import Player

player = Player()


class InventoryWidget(ScrollableContainer):
    can_focus = True

    def compose(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column()
        table.add_column(no_wrap=True)
        table.add_column(justify="right")
        for item in player.inventory.items:
            table.add_row(*item.tui_arr)
        yield Static(table)

    def on_mount(self):
        self.border_title = "Inventory"
        self.border_subtitle = (
            f"{len(player.inventory.items)} items "
            f"([gold1]{sum(item.value for item in player.inventory.items)}g[/])"
        )

    def on_click(self):
        self.focus()
