import textwrap
from collections import UserList

from rich.table import Table
from rich.text import Text

from myning.objects.character import Character
from myning.utilities.fib import fibonacci
from myning.utilities.ui import Colors, Icons, get_health_bar


class Army(UserList[Character]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort(key=lambda c: (c.__class__.__name__ != "Player", -c.level))

    def __hash__(self):
        return hash(
            tuple(
                (
                    c.id,
                    c.icon,
                    c.name,
                    c.health,
                    c.equipment,
                    c.level,
                    c.experience,
                    c.is_ghost,
                )
                for c in self
            )
        )

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
    def healer_view(self):
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
    def battle_view(self):
        table = Table.grid(padding=(0, 1))
        chunk_size = 10
        chunks = [self[i : i + chunk_size] for i in range(0, len(self), chunk_size)]
        columns = []
        for chunk in chunks:
            chunk_table = Table(box=None, padding=(0, 1, 0, 0))
            chunk_table.add_column("", width=2, no_wrap=True, overflow="ignore")
            chunk_table.add_column(Text("Name", justify="left"))
            chunk_table.add_column(Text("Health", justify="center"))
            chunk_table.add_column(Text(Icons.DAMAGE, justify="center"), justify="right")
            chunk_table.add_column(Text(Icons.ARMOR, justify="center"), justify="right")
            chunk_table.add_column(Text(Icons.LEVEL, justify="center"), justify="right")
            chunk_table.add_column(Text(Icons.GRAVEYARD, justify="center"))
            for member in chunk:
                chunk_table.add_row(
                    str(member.icon),
                    member.name.split()[0],
                    get_health_bar(member.health, member.max_health),
                    f"[red1]{member.stats['damage']}[/]",
                    f"[dodger_blue1]{member.stats['armor']}[/]",
                    f"[cyan1]{member.level}[/]",
                    "🪦" if member.is_ghost else " ",
                )
            columns.append(chunk_table)
        table.add_row(*columns)
        return table

    @property
    def icons(self):
        return textwrap.fill(" ".join(member.icon for member in self), width=2 * 15)

    @property
    def health_bar(self):
        return get_health_bar(self.current_health, self.total_health, 30)

    @property
    def stats_str(self):
        damage_str = f"{Icons.DAMAGE} {Colors.WEAPON(self.total_damage)}"
        armor_str = f"{Icons.ARMOR} {Colors.ARMOR(self.total_armor)}"
        return f"{damage_str} {armor_str}"

    @property
    def compact_view(self):
        return f"{self.icons}\n\n{self.health_bar} {self.stats_str}"
