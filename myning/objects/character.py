import random
from datetime import datetime
from enum import Enum

from blessed import Terminal

from myning.config import RACES, XP_COST
from myning.objects.equipment import Equipment
from myning.objects.object import Object
from myning.objects.race import Race
from myning.utils import utils
from myning.utils.file_manager import FileManager
from myning.utils.output import print_level_up
from myning.utils.ui import columnate, get_health_bar
from myning.utils.ui_consts import Colors, Icons
from myning.utils.utils import get_random_array_item, get_random_int

term = Terminal()
STRENGTH_DIVISOR = 4
DEF_DIVISOR = 8
CRIT_DIVISOR = 5
DODGE_DIVISOR = 5


class CharacterRaces(str, Enum):
    AASIMAR = "Aasimar"
    ALIEN = "Alien"
    BUGBEAR = "Bugbear"
    DRAGONBORN = "Dragonborn"
    DWARF = "Dwarf"
    ELF = "Elf"
    FIRBOLG = "Firbolg"
    GNOME = "Gnome"
    GOBLIN = "Goblin"
    GOLIATH = "Goliath"
    HALF_ELF = "Half-Elf"
    HALF_ORC = "Half-Orc"
    HALFLING = "Halfling"
    HOBGOBLIN = "Hobgoblin"
    HUMAN = "Human"
    KENKU = "Kenku"
    KOBOLD = "Kobold"
    LIZARDFOLK = "Lizardfolk"
    ORC = "Orc"
    TABAXI = "Tabaxi"
    TIEFLING = "Tiefling"
    TRITON = "Triton"
    YUAN_TI_PUREBLOOD = "Yuan-Ti Pureblood"
    UNICORN = "Unicorn"


class Character(Object):
    base_stats = ["damage", "armor"]

    def __init__(
        self,
        name: str,
        description=None,
        level: int = 1,
        is_enemy=False,
        race: Race = RACES[CharacterRaces.HUMAN.value],
    ):
        self.name = name
        self.description = description or name
        self.level = level
        self.is_enemy = is_enemy
        self.is_ghost = False
        self.equipment = Equipment()
        self.experience = 0
        self.race: Race = race
        self.health = self.max_health
        self.id = f"{self.name} - {get_random_int(10 ** 13)}"

    @property
    def health_mod(self):
        return self.race.health_mod

    @property
    def intros(self):
        return [self.race.intro, "Hello", "Howdy"]

    @property
    def max_health(self):
        return self.level * self.health_mod

    @property
    def _level_stats(self):
        return {
            "damage": self.level * 2,
            "armor": self.level,
        }

    @property
    def _race_bonus(self):
        return {
            "damage": self.race.strength * self.level / STRENGTH_DIVISOR,
            "armor": self.race.defense * self.level / DEF_DIVISOR,
            "critical_chance": self.race.critical_chance * self.level / CRIT_DIVISOR,
            "dodge_chance": self.race.dodge_chance * self.level / DODGE_DIVISOR,
            "health_mod": self.race.health_mod,
        }

    @property
    def stats(self):
        return {
            "damage": int(
                self.equipment.stats["damage"]
                + self._level_stats["damage"]
                + self._race_bonus["damage"]
            ),
            "armor": int(
                self.equipment.stats["armor"]
                + self._level_stats["armor"]
                + self._race_bonus["armor"]
            ),
            "critical_chance": int(self._race_bonus["critical_chance"]),
            "dodge_chance": int(self._race_bonus["dodge_chance"]),
        }

    @property
    def value(self):
        equipment_value = sum(item.value for item in self.equipment.all_items)
        level_value = utils.fibonacci_sum(self.level) * XP_COST

        return equipment_value + level_value

    def get_introduction(self):
        random.seed(datetime.now().timestamp())
        if len(self.intros) == 0:
            intro = "Howdy"
        else:
            index = random.randint(0, (len(self.intros) - 1))
            intro = self.intros[index]

        return f"{intro}, my name is {self.name}. I'm {self.description}."

    def subtract_health(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    @property
    def file_name(self):
        return f"entities/{self.id}"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "is_enemy": self.is_enemy,
            "equipment": self.equipment.to_dict(),
            "experience": self.experience,
            "health": self.health,
            "race": self.race.name,
            "id": self.id,
            "is_ghost": self.is_ghost,
        }

    @classmethod
    def from_dict(cls, dict: dict):
        entity = cls(
            dict["name"],
            dict["description"],
            dict["level"],
            dict["is_enemy"],
        )
        entity.race = RACES[dict.get("race") or CharacterRaces.HUMAN.value]
        entity.equipment = Equipment.from_dict(dict["equipment"])
        entity.experience = dict["experience"]
        entity.health = dict["health"]

        if "id" in dict:
            entity.id = dict["id"]

        # add id (and save) for all allies without
        # TODO: remove after everyone is migrated
        elif "allies" not in dict:
            # clear old file?
            entity.id = entity.name
            FileManager.delete(entity)

            # create new file for allies
            entity.id = f"{entity.name} - {get_random_int(10 ** 13)}"
            FileManager.save(entity)

        entity.is_ghost = dict.get("is_ghost") or False
        return entity

    def add_experience(self, exp, display=True):
        if exp <= 0:
            return
        self.experience += exp
        needed = utils.fibonacci(self.level + 1)
        while self.experience >= needed:
            self.level += 1
            self.experience = self.experience - needed
            self.health += self.health_mod
            for stat in Character.base_stats:
                self.stats[stat] += 1

            needed = utils.fibonacci(self.level + 1)

            if display:
                print_level_up(self.level)

        FileManager.save(self)

    @classmethod
    @property
    def companion_races(cls) -> list:
        return [
            CharacterRaces.DWARF,
            CharacterRaces.HUMAN,
            CharacterRaces.ELF,
            CharacterRaces.ORC,
            CharacterRaces.AASIMAR,
            CharacterRaces.HALF_ELF,
            CharacterRaces.HALF_ORC,
            CharacterRaces.HALFLING,
            CharacterRaces.KENKU,
            CharacterRaces.LIZARDFOLK,
            CharacterRaces.KOBOLD,
            CharacterRaces.TABAXI,
            CharacterRaces.YUAN_TI_PUREBLOOD,
            CharacterRaces.HOBGOBLIN,
            CharacterRaces.TRITON,
            CharacterRaces.GOLIATH,
            CharacterRaces.GOBLIN,
            CharacterRaces.TIEFLING,
            CharacterRaces.BUGBEAR,
            CharacterRaces.FIRBOLG,
            CharacterRaces.GNOME,
        ]

    @property
    def stats_str(self):
        return "\n".join(
            columnate(
                [
                    [
                        "Damage",
                        f"{Colors.WEAPON}{Icons.DAMAGE} {self.stats['damage']}{term.normal}",
                    ],
                    [
                        "Armor",
                        f"{Colors.ARMOR}{Icons.ARMOR} {self.stats['armor']}{term.normal}",
                    ],
                ],
                sep="  ",
            )
        )

    @property
    def icon(self):
        return RaceEmoji(f"{self.race.icon}")

    @property
    def health_str(self):
        return get_health_bar(self.health, self.max_health)

    @property
    def damage_str(self):
        return f"{Icons.DAMAGE} {Colors.WEAPON}{self.stats['damage']}{term.normal}"

    @property
    def armor_str(self):
        return f"{Icons.ARMOR} {Colors.ARMOR}{self.stats['armor']}{term.normal}"

    @property
    def level_str(self):
        return f"{Icons.LEVEL} {Colors.LEVEL}{self.level}{term.normal}"

    @property
    def exp_str(self):
        return f"{Colors.EXP}{self.experience}/{utils.fibonacci(self.level + 1)}{term.normal} xp"

    @property
    def ghost_str(self):
        return " " if not self.is_ghost else "🪦"

    def __str__(self):
        exp = "" if self.is_enemy else f" | {self.exp_str}"
        return f"{self.icon} {self.name}: {self.health_str} {self.damage_str} {self.armor_str} | {self.level_str}{exp} {self.ghost_str}"

    @property
    def premium(self):
        composite = self.health_mod + self.stats["armor"] + self.stats["damage"]

        return int(composite * 0.2) if composite > 0 else 1


class RaceEmoji:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def __len__(self):
        return 1
