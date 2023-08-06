from rich.table import Table
from textual.containers import ScrollableContainer
from textual.widgets import Static

from myning.objects.player import Player

player = Player()


class InventoryContents(Static):
    def update_inventory(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column()
        table.add_column(max_width=36, no_wrap=True)
        table.add_column(justify="right")
        for item in player.inventory.items:
            table.add_row(*item.tui_arr)
        self.update(table if player.inventory.items else "")


class InventoryWidget(ScrollableContainer):
    can_focus = True

    def compose(self):
        yield InventoryContents()

    def on_click(self):
        self.focus()

    def update_border(self):
        self.border_title = "Inventory"
        self.border_subtitle = (
            f"{len(player.inventory.items)} items "
            f"([gold1]{sum(item.value for item in player.inventory.items)}g[/])"
        )
