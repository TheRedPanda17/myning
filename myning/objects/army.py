import math
from collections import UserList

from myning.objects.character import Character
from myning.objects.settings import Settings
from myning.utils.ui import columnate, get_health_bar
from myning.utils.ui_consts import Icons


class Army(UserList[Character]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort(key=lambda e: (e.level, e.experience))
        self.reverse()

    def append(self, __object) -> None:
        super().append(__object)
        self.sort(key=lambda e: (e.level, e.experience))
        self.reverse()

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
    def character_icon(self) -> str:
        if len(self) == 0:
            return "💀"

        race_counts = {}
        for member in self:
            race_counts[member.race] = race_counts.get(member.race, 0) + 1

        icon, max = "", 0
        for race, count in race_counts.items():
            if count > max:
                icon = race.icon
                max = count

        return icon

    @property
    def current_health(self) -> int:
        return sum(member.health for member in self)

    @property
    def total_health(self) -> int:
        return sum(member.max_health for member in self)

    @property
    def defeated(self) -> int:
        return not any(member.health > 0 for member in self)

    @property
    def total_damage(self) -> int:
        return sum(member.stats["damage"] for member in self)

    @property
    def total_armor(self) -> int:
        return sum(member.stats["armor"] for member in self)

    @property
    def summary_str(self) -> str:
        return (
            f"{self.character_icon} {len(self)} "
            f"{get_health_bar(self.current_health, self.total_health, 30)}"
            f" {Icons.DAMAGE} {self.total_damage} {Icons.ARMOR} {self.total_armor}"
        )

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

            s += f"\n\n{self.summary_str}"
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
