from rich.table import Table
from textual.widgets import Static

from myning.config import MINES
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.utils.ui_consts import Icons
from new_tui.formatter import Colors, Formatter

player = Player()
research_facility = ResearchFacility()


class CurrencyWidget(Static):
    DEFAULT_CLASSES = "container"

    def render(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column(style="bold")
        table.add_row("Gold", Icons.GOLD, Formatter.gold(player.gold))

        if MINES["Large pit"] in player.mines_completed:
            table.add_row(
                "Soul credits",
                Icons.GRAVEYARD,
                Formatter.soul_credits(player.soul_credits),
            )

        if MINES["Cavern"] in player.mines_completed:
            table.add_row(
                "Research points",
                Icons.RESEARCH_FACILITY,
                Formatter.research_points(research_facility.points),
            )

        if player.macguffin.exp_boost > 1 or player.macguffin.mineral_boost > 1:
            table.add_row(
                "Macguffin",
                Icons.MINERAL,
                f"[{Colors.GOLD}]{player.macguffin.store_percentage}[/] mineral value boost",
            )
            table.add_row(
                "",
                Icons.XP,
                f"[{Colors.XP}]{player.macguffin.exp_percentage}[/] xp boost",
            )

        return table

    def on_mount(self):
        self.border_title = "Currency"
        self.set_interval(1, research_facility.check_in)
        self.set_interval(1, self.refresh)
