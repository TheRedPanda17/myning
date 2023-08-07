import math

from rich.table import Table
from rich.text import Text
from textual.containers import ScrollableContainer
from textual.widgets import Static

from myning.objects.player import Player
from myning.utils import utils
from myning.utils.ui_consts import Icons

player = Player()


def get_health_bar(health: int, max_health: int, bar_count: int = 11):
    health_fraction = health / max_health if max_health else 0
    green_count = math.ceil(health_fraction * bar_count)
    health_fraction_str = f"{health}/{max_health}".center(bar_count)
    return "".join(
        f"[grey0 on green]{char}[/]" if i < green_count else f"[on red]{char}[/]"
        for i, char in enumerate(health_fraction_str)
    )


class ArmyContents(Static):
    def update_army(self):
        table = Table(box=None, padding=(0, 1, 0, 0))
        table.add_column("", width=2, no_wrap=True, overflow="ignore")
        table.add_column(Text("Name", justify="left"))
        table.add_column(Text("Health", justify="center"))
        table.add_column(Text(Icons.DAMAGE, justify="center"), justify="right")
        table.add_column(Text(Icons.ARMOR, justify="center"), justify="right")
        table.add_column(Text(Icons.LEVEL, justify="center"), justify="right")
        table.add_column(Text(Icons.XP, justify="center"), justify="right")
        table.add_column(Text(Icons.GRAVEYARD, justify="center"))
        for member in player.army:
            if not member.name:
                continue
            table.add_row(
                str(member.icon),
                member.name.split()[0],
                get_health_bar(member.health, member.max_health),
                f"[red1]{member.stats['damage']}[/]",
                f"[dodger_blue1]{member.stats['armor']}[/]",
                f"[cyan1]{member.level}[/]",
                f"[magenta1]{member.experience}/{utils.fibonacci(member.level + 1)}[/]",
                "🪦" if member.is_ghost else " ",
            )
        self.update(table)


class ArmyWidget(ScrollableContainer):
    can_focus = True

    def compose(self):
        yield ArmyContents()

    def on_mount(self):
        self.border_title = "Army"
        self.border_subtitle = (
            f"{len(player.army):2} members "
            f"❤️  [green]{player.army.current_health}[/]/"
            f"[green]{player.army.total_health}[/] "
            f"{Icons.DAMAGE} [red1]{player.army.total_damage}[/] "
            f"{Icons.ARMOR} [bold dodger_blue1]{player.army.total_armor}[/]"
        )

    def on_click(self):
        self.focus()
