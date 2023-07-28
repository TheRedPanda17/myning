from blessed import Terminal

from myning.objects.object import Object

term = Terminal()


class Race(Object):
    SKILL_GAPS = {
        "strength": [0, 1, 2, 4, 6],
        "defense": [0, 1, 2, 3, 5],
        "critical_chance": [0, 1, 3, 5, 7],
        "dodge_chance": [0, 1, 3, 5, 7],
    }
    ADJECTIVES = [
        f"{term.red}Very low{term.normal}",
        f"{term.orange}Low{term.normal}",
        f"{term.gray}Average{term.normal}",
        f"{term.cyan}High{term.normal}",
        f"{term.blue}Very High{term.normal}",
        f"{term.purple}Unbeatable{term.normal}",
    ]

    def __init__(
        self,
        icon,
        name,
        strength,
        defense,
        critical_chance,
        dodge_chance,
        intro,
        description,
        size,
        health_mod,
        rarity_tier,
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

    def get_skill_adj(self, skill: str) -> str:
        level = self.__getattribute__(skill)
        gaps = Race.SKILL_GAPS[skill]
        for index, gap_level in enumerate(gaps):
            if level <= gap_level:
                return Race.ADJECTIVES[index]

        return Race.ADJECTIVES[-1]

    def get_skill_str(self, skill: str):
        title = skill.capitalize().replace("_", " ")
        return f"{title}: {self.get_skill_adj(skill)}\n"

    @property
    def skills_str(self):
        s = f"Base Health: {self.health_mod}\n"
        return s + "".join(
            [
                self.get_skill_str(stat)
                for stat in ["strength", "defense", "critical_chance", "dodge_chance"]
            ]
        )

    @property
    def rarity_str(self):
        return [
            f"{term.gray}Very Common{term.normal}",
            f"{term.cyan}Common{term.normal}",
            f"{term.blue}Uncommon{term.normal}",
            f"{term.purple}Rare{term.normal}",
            f"{term.red}Very Rare{term.normal}",
            f"{term.orange}Extraordinary{term.normal}",
            f"{term.yellow}Mythical{term.normal}",
        ][self.rarity_tier - 1]
