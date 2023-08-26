from textual.widgets import DataTable

from myning.objects.player import Player
from myning.utilities.ui import Colors, Icons

player = Player()


class ArmyWidget(DataTable):
    def on_mount(self):
        self.show_cursor = False
        self.add_columns(*player.column_titles)
        self.update()

    def on_click(self):
        self.focus()

    def update(self):
        self.border_title = "Army"
        self.border_subtitle = (
            f"{len(player.army)} members "
            f"{Icons.HEART}  [green1]{player.army.current_health}[/]/"
            f"[green1]{player.army.total_health}[/] "
            f"{Icons.DAMAGE} [{Colors.WEAPON}]{player.army.total_damage}[/] "
            f"{Icons.ARMOR} [{Colors.ARMOR}]{player.army.total_armor}[/]"
        )
        self.clear()
        self.add_rows(member.arr for member in player.army)