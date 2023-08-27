from textual.widgets import DataTable

from myning.objects.inventory import Inventory
from myning.objects.player import Player
from myning.utilities.formatter import Formatter

player = Player()
inventory = Inventory()


class InventoryWidget(DataTable):
    hash = None

    def on_mount(self):
        self.show_cursor = False
        self.show_header = False
        self.add_column("i")
        self.add_column("n", width=32)
        self.add_column("v")

    def on_click(self):
        self.focus()

    def update(self):
        inventory_hash = hash(tuple(player.inventory.items))
        if self.hash == inventory_hash:
            return
        self.hash = inventory_hash
        self.border_title = "Inventory"
        self.border_subtitle = (
            f"{len(inventory.items)} items ({Formatter.gold(inventory.total_value)})"
        )
        self.clear()
        self.add_rows(item.arr for item in inventory.items)
