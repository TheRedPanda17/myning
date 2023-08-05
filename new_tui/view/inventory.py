from rich.table import Table
from textual.containers import ScrollableContainer
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Static

from myning.objects.player import Player

player = Player()


class InventoryContents(Static):
    def update_inventory(self):
        if not self.parent:
            return

        self.parent.border_title = "Inventory"
        self.parent.border_subtitle = (
            f"{len(player.inventory.items)} items "
            f"([gold1]{sum(item.value for item in player.inventory.items)}g[/])"
        )

        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column()
        table.add_column(no_wrap=True)
        table.add_column(justify="right")
        for item in player.inventory.items:
            table.add_row(*item.tui_arr)
        self.update(table)


class InventoryWidget(ScrollableContainer):
    can_focus = True

    def compose(self):
        yield InventoryContents()

    def on_click(self):
        self.focus()
        self._scroll_update(self.virtual_size)
