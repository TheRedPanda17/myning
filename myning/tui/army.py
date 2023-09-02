from textual.widgets import DataTable

from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.utilities.ui import Colors, Icons

player = Player()
settings = Settings()


class ArmyWidget(DataTable):
    BINDINGS = [("c", "compact", "Toggle Compact Mode")]
    hash = None

    def on_mount(self):
        self.border_title = "Army"
        self.show_cursor = False

    def on_click(self):
        self.focus()

    def action_compact(self):
        settings.toggle_compact_mode()
        self.update()

    def update(self):
        army_hash = hash((player.army, settings.compact_mode))
        if self.hash == army_hash:
            return
        self.hash = army_hash
        self.clear(columns=True)
        if settings.compact_mode:
            self.compact()
        else:
            self.full()

    def compact(self):
        self.show_header = False
        self.border_subtitle = f"{len(player.army)} members "
        self.add_column("")
        self.add_row(player.army.icons, height=len(player.army.icons.splitlines()))
        self.add_row("\n" + player.army.health_bar + "\n", height=3)
        self.add_row(player.army.stats_str)

    def full(self):
        self.show_header = True
        self.border_subtitle = (
            f"{len(player.army)} members "
            f"{Icons.HEART}  [green1]{player.army.current_health}[/]/"
            f"[green1]{player.army.total_health}[/] "
            f"{Icons.DAMAGE} [{Colors.WEAPON}]{player.army.total_damage}[/] "
            f"{Icons.ARMOR} [{Colors.ARMOR}]{player.army.total_armor}[/]"
        )
        self.add_columns(*player.column_titles)
        self.add_rows(member.arr for member in player.army)
