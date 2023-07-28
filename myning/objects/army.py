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
    def defeated(self):
        return not any(member.health > 0 for member in self)

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

            health, total_health = 0, 0
            for member in self:
                total_health += member.max_health
                health += member.health

            total_armour = sum(member.stats["armor"] for member in self)
            total_damage = sum(member.stats["damage"] for member in self)

            s += f"\n\n {get_health_bar(health, total_health, 30)} {Icons.DAMAGE} {total_damage} {Icons.ARMOR} {total_armour}"
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
