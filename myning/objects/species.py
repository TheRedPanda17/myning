from rich.table import Table

from myning.objects.object import Object
from myning.utilities.ui import Icons

SKILL_GAPS = {
    "strength": [0, 1, 2, 4, 6],
    "defense": [0, 1, 2, 3, 5],
    "critical_chance": [0, 1, 3, 5, 7],
    "dodge_chance": [0, 1, 3, 5, 7],
}
SKILL_COLORS = [
    "[red1]{msg}[/]",
    "[orange1]{msg}[/]",
    "[grey70]{msg}[/]",
    "[cyan1]{msg}[/]",
    "[dodger_blue1]{msg}[/]",
    "[purple]{msg}[/]",
]
ADJECTIVES = [
    "Very Low",
    "Low",
    "Average",
    "High",
    "Very High",
    "Unbeatable",
]
RARITIES = [
    "[grey70]Very Common[/]",
    "Common",
    "[cyan1]Uncommon[/]",
    "[dodger_blue1]Rare[/]",
    "[purple]Very Rare[/]",
    "[red1]Extraordinary[/]",
    "[gold1]Mythical[/]",
]


class Species(Object):
    def __init__(
        self,
        icon,
        name,
        strength,
        defense,
        critical_chance,
        dodge_chance,
        intro,
        description: str,
        size,
        health_mod: int,
        rarity_tier: int,
        alignment,
        is_enemy=False,
    ) -> None:
        self.name = name
        self.icon = icon
        self.strength = strength
        self.defense = defense
        self.critical_chance = critical_chance
        self.dodge_chance = dodge_chance
        self.intro = intro
        self.description = description
        self.size = size
        self.health_mod = health_mod
        self.rarity_tier = rarity_tier
        self.alignment = alignment
        self.is_enemy = is_enemy

    @classmethod
    def from_dict(cls, attrs: dict):
        return cls(**attrs)

    def get_skill_adj(self, skill: str, exact: bool):
        level = getattr(self, skill)
        gaps = SKILL_GAPS[skill]

        index = -1
        for i, gap_level in enumerate(gaps):
            if level <= gap_level:
                index = i
                break

        msg = ADJECTIVES[index]
        if exact:
            msg = f"{level} - {msg}"

        return SKILL_COLORS[index].format(msg=msg)

    def get_stats(self, exact: bool):
        table = Table.grid(padding=(0, 1))
        table.add_row("Base Health", Icons.HEART, f"[green1]{self.health_mod}[/]")
        table.add_row("Strength", Icons.WEAPON, self.get_skill_adj("strength", exact))
        table.add_row("Defense", Icons.ARMOR, self.get_skill_adj("defense", exact))
        table.add_row("Critical chance", Icons.CRIT, self.get_skill_adj("critical_chance", exact))
        table.add_row("Dodge chance", Icons.DODGE, self.get_skill_adj("dodge_chance", exact))
        return table

    @property
    def rarity(self):
        return RARITIES[self.rarity_tier - 1]
