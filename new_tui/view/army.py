import math

from rich.table import Table
from rich.text import Text
from textual.containers import ScrollableContainer
from textual.widgets import Static
from myning.objects.army import Army

from myning.objects.player import Player
from myning.utils import utils
from myning.utils.ui_consts import Icons
from new_tui.formatter import Colors

player = Player()


def get_health_bar(health: int, max_health: int, bar_count: int = 11):
    health_fraction = health / max_health if max_health else 0
    green_count = math.ceil(health_fraction * bar_count)
    health_fraction_str = f"{health}/{max_health}".center(bar_count)
    return "".join(
        f"[grey0 on green]{char}[/]" if i < green_count else f"[on red]{char}[/]"
        for i, char in enumerate(health_fraction_str)
    )


def get_army_table(army: Army, *, show_header=True, show_xp=True):
    table = Table(box=None, padding=(0, 1, 0, 0))
    table.add_column("", width=2, no_wrap=True, overflow="ignore")
    table.add_column(Text("Name", justify="left"))
    table.add_column(Text("Health", justify="center"))
    table.add_column(Text(Icons.DAMAGE, justify="center"), justify="right")
    table.add_column(Text(Icons.ARMOR, justify="center"), justify="right")
    table.add_column(Text(Icons.LEVEL, justify="center"), justify="right")
    if show_xp:
        table.add_column(Text(Icons.XP, justify="center"), justify="right")
    table.add_column(Text(Icons.GRAVEYARD, justify="center"))

    if not show_header:
        table.show_header = False
        for column in table.columns:
            column.header = ""

    for member in army:
        if not member.name:
            continue
        cells = []
        cells.append(str(member.icon))
        cells.append(member.name.split()[0])
        cells.append(get_health_bar(member.health, member.max_health))
        cells.append(f"[red1]{member.stats['damage']}[/]")
        cells.append(f"[dodger_blue1]{member.stats['armor']}[/]")
        cells.append(f"[cyan1]{member.level}[/]")
        if show_xp:
            cells.append(f"[magenta1]{member.experience}/{utils.fibonacci(member.level + 1)}[/]")
        cells.append("🪦" if member.is_ghost else " ")
        table.add_row(*cells)
    return table


def get_army_columns(army: Army):
    chunk_size = 10
    chunks = [army[i : i + chunk_size] for i in range(0, len(army), chunk_size)]
    return [get_army_table(column, show_header=False, show_xp=False) for column in chunks]


class ArmyContents(Static):
    def update_army(self):
        self.update(get_army_table(player.army))


class ArmyWidget(ScrollableContainer):
    can_focus = True

    def compose(self):
        yield ArmyContents()

    def on_mount(self):
        self.border_title = "Army"
        self.border_subtitle = (
            f"{len(player.army):2} members "
            f"❤️  [green1]{player.army.current_health}[/]/"
            f"[green1]{player.army.total_health}[/] "
            f"{Icons.DAMAGE} [{Colors.WEAPON}]{player.army.total_damage}[/] "
            f"{Icons.ARMOR} [{Colors.ARMOR}]{player.army.total_armor}[/]"
        )

    def on_click(self):
        self.focus()
