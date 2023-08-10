from collections import UserList

from rich.table import Table
from rich.text import Text

from myning.objects.character import Character
from myning.utils import utils
from myning.utils.ui import columnate, get_health_bar
from myning.utils.ui_consts import Icons


class Army(UserList[Character]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort(key=lambda e: (e.level, e.experience), reverse=True)

    def append(self, __object: Character) -> None:
        super().append(__object)
        self.sort(key=lambda e: (e.level, e.experience), reverse=True)

    @property
    def abbreviated(self):
        return columnate(
            [
                [
                    member.icon,
                    member.name,
                    member.damage_str,
                    member.armor_str,
                    member.level_str,
                    member.exp_str,
                    member.ghost_str,
                ]
                for member in self
            ]
        )

    @property
    def current_health(self) -> int:
        return sum(member.health for member in self)

    @property
    def defeated(self):
        return all(member.health <= 0 for member in self)

    @property
    def living_members(self):
        return [m for m in self if m.health > 0]

    @property
    def total_health(self) -> int:
        return sum(member.max_health for member in self)

    @property
    def total_damage(self) -> int:
        return sum(member.stats["damage"] for member in self)

    @property
    def total_armor(self) -> int:
        return sum(member.stats["armor"] for member in self)

    @property
    def summary_str(self) -> str:
        return f"{self.icons_str}\n\n{self.stats_summary}"

    @property
    def stats_summary(self) -> str:
        return (
            f"{get_health_bar(self.current_health, self.total_health, 30)}"
            f" {Icons.DAMAGE} {self.total_damage} {Icons.ARMOR} {self.total_armor}"
        )

    @property
    def icons_str(self) -> str:
        s = ""
        for i, member in enumerate(self):
            if i != 0:
                s += "\n" if i % 15 == 0 else " "
            s += str(member.icon)
        return s

    def get_table(self, *, show_header=True, show_xp=True):
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

        for member in self:
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
                cells.append(
                    f"[magenta1]{member.experience}/{utils.fibonacci(member.level + 1)}[/]"
                )
            cells.append("🪦" if member.is_ghost else " ")
            table.add_row(*cells)
        return table

    @property
    def tui_table(self):
        return self.get_table()

    @property
    def tui_columns(self):
        chunk_size = 10
        chunks = [self[i : i + chunk_size] for i in range(0, len(self), chunk_size)]
        columns = []
        for chunk in chunks:
            table = Table(box=None, padding=(0, 1, 0, 0))
            table.add_column("", width=2, no_wrap=True, overflow="ignore")
            table.add_column(Text("Name", justify="left"))
            table.add_column(Text("Health", justify="center"))
            table.add_column(Text(Icons.DAMAGE, justify="center"), justify="right")
            table.add_column(Text(Icons.ARMOR, justify="center"), justify="right")
            table.add_column(Text(Icons.LEVEL, justify="center"), justify="right")
            # if show_xp:
            #     table.add_column(Text(Icons.XP, justify="center"), justify="right")
            table.add_column(Text(Icons.GRAVEYARD, justify="center"))

            for member in chunk:
                if not member.name:
                    continue
                cells = []
                cells.append(str(member.icon))
                cells.append(member.name.split()[0])
                cells.append(get_health_bar(member.health, member.max_health))
                cells.append(f"[red1]{member.stats['damage']}[/]")
                cells.append(f"[dodger_blue1]{member.stats['armor']}[/]")
                cells.append(f"[cyan1]{member.level}[/]")
                # if show_xp:
                #     cells.append(
                #         f"[magenta1]{member.experience}/{utils.fibonacci(member.level + 1)}[/]"
                #     )
                cells.append("🪦" if member.is_ghost else " ")
                table.add_row(*cells)
            columns.append(table)
        return columns
