from textual.widgets import DataTable
from rich.text import Text

from myning.objects.player import Player
from myning.utils.ui_consts import Icons
from new_tui.formatter import Colors

player = Player()


class ArmyWidget(DataTable):
    can_focus = True

    def on_mount(self):
        # self.show_header = False
        self.show_cursor = False
        self.add_column("")
        self.add_column("Name")
        self.add_column(Text("Health", justify="center"))
        self.add_column(Text(Icons.DAMAGE, justify="center"))
        self.add_column(Text(Icons.ARMOR, justify="center"))
        self.add_column(Text(Icons.LEVEL, justify="center"))
        self.add_column(Text(Icons.XP, justify="center"))
        self.add_column(Text(Icons.GRAVEYARD, justify="center"))

    def on_click(self):
        self.focus()

    def update(self):
        self.border_title = "Army"
        self.border_subtitle = (
            f"{len(player.army)} members "
            f"❤️  [green1]{player.army.current_health}[/]/"
            f"[green1]{player.army.total_health}[/] "
            f"{Icons.DAMAGE} [{Colors.WEAPON}]{player.army.total_damage}[/] "
            f"{Icons.ARMOR} [{Colors.ARMOR}]{player.army.total_armor}[/]"
        )
        self.clear()
        for member in player.army:
            self.add_row(*member.tui_arr)
