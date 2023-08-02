from rich.table import Table
from textual.containers import ScrollableContainer
from textual.widgets import Static

from myning.objects.item import ItemType
from myning.objects.player import Player

player = Player()


class InventoryWidget(ScrollableContainer):
    can_focus = True

    def on_mount(self):
        self.border_title = "Inventory"
        self.border_subtitle = (
            f"{len(player.inventory.items)} items "
            f"([gold1]{sum(item.value for item in player.inventory.items)}g[/])"
        )

    def compose(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column(no_wrap=True)
        for item in player.inventory.items:
            match item.type:
                case ItemType.MINERAL:
                    color = "gold1"
                case ItemType.WEAPON:
                    color = "red1"
                case ItemType.HELMET | ItemType.SHIRT | ItemType.PANTS | ItemType.SHOES:
                    color = "dodger_blue1"
                case ItemType.PLANT:
                    color = "green1"
                case _:
                    color = ""
            table.add_row(f"{item.icon} {item.name} [bold {color}]{item.value}[/]")
        yield Static(table)

    def on_click(self):
        self.focus()
