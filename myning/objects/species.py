from rich.table import Table

from myning.objects.object import Object
from myning.utilities.ui import Icons

SKILL_GAPS = {
    "strength": [0, 1, 2, 4, 6],
    "defense": [0, 1, 2, 3, 5],
    "critical_chance": [0, 1, 3, 5, 7],
    "dodge_chance": [0, 1, 3, 5, 7],
}
ADJECTIVES = [
    "[red1]Very Low[/]",
    "[orange1]Low[/]",
    "[grey70]Average[/]",
    "[cyan1]High[/]",
    "[dodger_blue1]Very High[/]",
    "[purple]Unbeatable[/]",
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

    def get_skill_adj(self, skill: str):
        level = getattr(self, skill)
        gaps = SKILL_GAPS[skill]
        return next(
            (ADJECTIVES[index] for index, gap_level in enumerate(gaps) if level <= gap_level),
            ADJECTIVES[-1],
        )

    @property
    def stats(self):
        table = Table.grid(padding=(0, 1))
        table.add_row("Base Health", Icons.HEART, f"[green1]{self.health_mod}[/]")
        table.add_row("Strength", Icons.WEAPON, self.get_skill_adj("strength"))
        table.add_row("Defense", Icons.ARMOR, self.get_skill_adj("defense"))
        table.add_row("Critical chance", Icons.CRIT, self.get_skill_adj("critical_chance"))
        table.add_row("Dodge chance", Icons.DODGE, self.get_skill_adj("dodge_chance"))
        return table

    @property
    def rarity(self):
        return RARITIES[self.rarity_tier - 1]
