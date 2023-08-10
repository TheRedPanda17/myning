import math
from collections import UserList

from myning.objects.character import Character
from myning.objects.settings import Settings
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

    def __str__(self):
        if not self:
            return "This army is defeated"

        if len(self) > Settings().army_columns:
            s = ""
            column_count = math.ceil(len(self) / Settings().army_columns)
            row_count = math.ceil(len(self) / column_count)
            rows = [[] for _ in range(row_count)]
            members = columnate(
                [
                    [
                        member.icon,
                        member.name.partition(" ")[0],
                        member.damage_str,
                        member.armor_str,
                        member.level_str,
                        member.ghost_str,
                    ]
                    for member in self
                ]
            )
            for i, member in enumerate(members):
                row = i % row_count
                end = "\n" if len(rows[row]) == column_count - 1 else " ║ "
                rows[row].append(f"{member}{end}")

            for column in rows:
                for member in column:
                    s += member

            s += f"\n\n{self.stats_summary}"
            return s

        return "\n".join(
            columnate(
                [
                    [
                        member.icon,
                        member.name.partition(" ")[0],
                        member.health_str,
                        member.damage_str,
                        member.armor_str,
                        member.level_str,
                        member.exp_str,
                        member.ghost_str,
                    ]
                    for member in self
                ]
            )
        )
