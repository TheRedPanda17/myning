from rich.table import Table
from textual.widgets import Static

from myning.config import MINES
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.utils.ui_consts import Icons

player = Player()
research_facility = ResearchFacility()


class CurrencyWidget(Static):
    DEFAULT_CLASSES = "container"

    def render(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_row("[bold]Gold[/]", Icons.GOLD, f"[bold gold1]{player.gold}[/]")

        if MINES["Large pit"] in player.mines_completed:
            table.add_row(
                "[bold]Soul credits[/]",
                Icons.GRAVEYARD,
                f"[bold blue]{player.soul_credits} soul credits[/]",
            )

        if MINES["Cavern"] in player.mines_completed:
            table.add_row(
                "[bold]Research points[/]",
                Icons.RESEARCH_FACILITY,
                f"[bold deep_pink3]{research_facility.points} research points[/]",
            )

        if player.macguffin.exp_boost > 1 or player.macguffin.mineral_boost > 1:
            table.add_row(
                "[bold]Macguffin[/]",
                Icons.MINERAL,
                f"[bold gold1]{player.macguffin.store_percentage}[/] mineral value boost",
            )
            table.add_row(
                "",
                Icons.XP,
                f"[bold magenta]{player.macguffin.exp_percentage}[/] xp boost",
            )

        return table

    def on_mount(self):
        self.border_title = "Currency"
