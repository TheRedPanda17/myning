from collections import UserList

from rich.table import Table
from rich.text import Text

from myning.objects.character import Character
from myning.utilities.fib import fibonacci
from myning.utilities.ui import Icons, get_health_bar


class Army(UserList[Character]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort(key=lambda c: (c.__class__.__name__ != "Player", -c.level))

    def append(self, __object: Character) -> None:
        super().append(__object)
        self.sort(key=lambda c: (c.__class__.__name__ != "Player", -c.level))

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

    @property
    def tui_table(self):
        table = Table(box=None, padding=(0, 1, 0, 0))
        table.add_column("", width=2, no_wrap=True, overflow="ignore")
        table.add_column(Text("Name", justify="left"))
        table.add_column(Text("Health", justify="center"))
        table.add_column(Text(Icons.DAMAGE, justify="center"), justify="right")
        table.add_column(Text(Icons.ARMOR, justify="center"), justify="right")
        table.add_column(Text(Icons.LEVEL, justify="center"), justify="right")
        table.add_column(Text(Icons.XP, justify="center"), justify="right")
        table.add_column(Text(Icons.GRAVEYARD, justify="center"))
        for member in self:
            table.add_row(
                str(member.icon),
                member.name.split()[0],
                get_health_bar(member.health, member.max_health),
                f"[red1]{member.stats['damage']}[/]",
                f"[dodger_blue1]{member.stats['armor']}[/]",
                f"[cyan1]{member.level}[/]",
                f"[magenta1]{member.experience}/{fibonacci(member.level + 1)}[/]",
                "🪦" if member.is_ghost else " ",
            )
        return table

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
            table.add_column(Text(Icons.GRAVEYARD, justify="center"))
            for member in chunk:
                table.add_row(
                    str(member.icon),
                    member.name.split()[0],
                    get_health_bar(member.health, member.max_health),
                    f"[red1]{member.stats['damage']}[/]",
                    f"[dodger_blue1]{member.stats['armor']}[/]",
                    f"[cyan1]{member.level}[/]",
                    "🪦" if member.is_ghost else " ",
                )
            columns.append(table)
        return columns
