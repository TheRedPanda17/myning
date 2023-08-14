from textual.widgets import DataTable

from myning.objects.player import Player

player = Player()


class InventoryWidget(DataTable):
    can_focus = True

    def on_mount(self):
        self.show_header = False
        self.show_cursor = False
        self.add_column("i")
        self.add_column("n", width=32)
        self.add_column("v")
        self.update()

    def on_click(self):
        self.focus()

    def update(self):
        self.border_title = "Inventory"
        self.border_subtitle = (
            f"{len(player.inventory.items)} items "
            f"([gold1]{sum(item.value for item in player.inventory.items)}g[/])"
        )
        self.clear()
        self.add_rows(item.tui_arr for item in player.inventory.items)
