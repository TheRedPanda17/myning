from rich.table import Table
from textual.widgets import Static

from myning.config import MINES
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.utils.file_manager import FileManager
from myning.utils.ui_consts import Icons
from new_tui.formatter import Colors, Formatter

player = Player()
macguffin = Macguffin()
facility = ResearchFacility()


class CurrencyWidget(Static):
    DEFAULT_CLASSES = "container"

    def render(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column()
        table.add_row("Gold", Icons.GOLD, Formatter.gold(player.gold))

        if MINES["Large pit"] in player.mines_completed:
            table.add_row(
                "Soul credits",
                Icons.SOUL_CREDITS,
                Formatter.soul_credits(player.soul_credits),
            )

        if MINES["Cavern"] in player.mines_completed:
            table.add_row(
                "Research points",
                Icons.RESEARCH_POINTS,
                Formatter.research_points(facility.points),
            )

        if macguffin.mineral_boost > 1:
            table.add_row(
                "Macguffin",
                Icons.MINERAL,
                f"[{Colors.GOLD}]{Formatter.percentage(macguffin.mineral_boost)}[/] mineral value",
            )
            table.add_row(
                "",
                Icons.XP,
                f"[{Colors.XP}]{Formatter.percentage(macguffin.xp_boost)}[/] xp gain",
            )

        # pylint: disable=line-too-long
        if macguffin.soul_credit_boost > 1:
            table.add_row(
                "",
                Icons.GRAVEYARD,
                f"[{Colors.SOUL_CREDITS}]{Formatter.percentage(macguffin.soul_credit_boost)}[/] soul credits",
            )
            table.add_row(
                "",
                Icons.RESEARCH_FACILITY,
                f"[{Colors.RESEARCH_POINTS}]{Formatter.percentage(macguffin.research_boost)}[/] research speed",
            )
            table.add_row(
                "",
                Icons.PLANT,
                f"[{Colors.PLANT}]{Formatter.percentage(macguffin.plant_boost)}[/] plant value",
            )

        return table

    def on_mount(self):
        self.border_title = "Currency"
        self.set_interval(1, self.check_in)

    def check_in(self):
        facility.check_in(macguffin.research_boost)
        FileManager.save(facility)
        self.refresh()
