import random
from enum import Enum

from rich.text import Text

from myning.config import SPECIES, XP_COST
from myning.objects.equipment import Equipment
from myning.objects.object import Object
from myning.objects.species import Species
from myning.utilities.fib import fibonacci, fibonacci_sum
from myning.utilities.file_manager import FileManager
from myning.utilities.rand import get_random_int
from myning.utilities.ui import Colors, Icons, get_health_bar

STRENGTH_DIVISOR = 4
DEF_DIVISOR = 8
CRIT_DIVISOR = 5
DODGE_DIVISOR = 5


class CharacterSpecies(str, Enum):
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
        species: Species = SPECIES[CharacterSpecies.HUMAN.value],
    ):
        self.name = name
        self.description = description or name
        self.level = level
        self.is_enemy = is_enemy
        self.is_ghost = False
        self.equipment = Equipment()
        self.experience = 0
        self.species: Species = species
        self.health = self.max_health
        self.id = f"{self.name} - {get_random_int(10 ** 13)}"

    @property
    def health_mod(self):
        return self.species.health_mod

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
    def _species_bonus(self):
        return {
            "damage": self.species.strength * self.level / STRENGTH_DIVISOR,
            "armor": self.species.defense * self.level / DEF_DIVISOR,
            "critical_chance": self.species.critical_chance * self.level / CRIT_DIVISOR,
            "dodge_chance": self.species.dodge_chance * self.level / DODGE_DIVISOR,
            "health_mod": self.species.health_mod,
        }

    @property
    def stats(self):
        return {
            "damage": int(
                self.equipment.stats["damage"]
                + self._level_stats["damage"]
                + self._species_bonus["damage"]
            ),
            "armor": int(
                self.equipment.stats["armor"]
                + self._level_stats["armor"]
                + self._species_bonus["armor"]
            ),
            "critical_chance": int(self._species_bonus["critical_chance"]),
            "dodge_chance": int(self._species_bonus["dodge_chance"]),
        }

    @property
    def value(self):
        equipment_value = sum(item.value for item in self.equipment.all_items)
        level_value = fibonacci_sum(self.level) * XP_COST

        return equipment_value + level_value

    @property
    def introduction(self):
        greeting = random.choice([self.species.intro, "Hello,", "Howdy,"])
        return f"{greeting} my name is {self.name}. I'm {self.description}."

    def subtract_health(self, damage):
        self.health = max(self.health - damage, 0)

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
            "race": self.species.name,
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
        entity.species = SPECIES[dict.get("race") or CharacterSpecies.HUMAN.value]
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

    def add_experience(self, xp: int):
        if xp <= 0:
            return
        self.experience += xp
        needed = fibonacci(self.level + 1)
        while self.experience >= needed:
            self.level += 1
            self.experience -= needed
            self.health += self.health_mod
            for stat in Character.base_stats:
                self.stats[stat] += 1

            needed = fibonacci(self.level + 1)

        FileManager.save(self)

    @classmethod
    @property
    def companion_species(cls) -> list:
        return [
            CharacterSpecies.DWARF,
            CharacterSpecies.HUMAN,
            CharacterSpecies.ELF,
            CharacterSpecies.ORC,
            CharacterSpecies.AASIMAR,
            CharacterSpecies.HALF_ELF,
            CharacterSpecies.HALF_ORC,
            CharacterSpecies.HALFLING,
            CharacterSpecies.KENKU,
            CharacterSpecies.LIZARDFOLK,
            CharacterSpecies.KOBOLD,
            CharacterSpecies.TABAXI,
            CharacterSpecies.YUAN_TI_PUREBLOOD,
            CharacterSpecies.HOBGOBLIN,
            CharacterSpecies.TRITON,
            CharacterSpecies.GOLIATH,
            CharacterSpecies.GOBLIN,
            CharacterSpecies.TIEFLING,
            CharacterSpecies.BUGBEAR,
            CharacterSpecies.FIRBOLG,
            CharacterSpecies.GNOME,
        ]

    @property
    def icon(self):
        return self.species.icon

    @property
    def health_str(self):
        return get_health_bar(self.health, self.max_health)

    @property
    def damage_str(self):
        return f"{Icons.DAMAGE} [{Colors.WEAPON}]{self.stats['damage']}[/]"

    @property
    def armor_str(self):
        return f"{Icons.ARMOR} [{Colors.ARMOR}]{self.stats['armor']}[/]"

    @property
    def level_str(self):
        return f"{Icons.LEVEL} [{Colors.LEVEL}]{self.level}[/]"

    @property
    def exp_str(self):
        return f"[{Colors.XP}]{self.experience}/{fibonacci(self.level + 1)}[/] xp"

    @property
    def ghost_str(self):
        return "🪦" if self.is_ghost else ""

    def __str__(self):
        exp = "" if self.is_enemy else f" {self.exp_str}"
        ghost_str = f" {self.ghost_str}" if self.is_ghost else ""
        return f"{self.icon} {self.name}: {self.health_str} {self.damage_str} {self.armor_str} {self.level_str}{exp}{ghost_str}"

    @property
    def premium(self):
        composite = self.health_mod + self.stats["armor"] + self.stats["damage"]
        return int(composite * 0.2) if composite > 0 else 1

    @classmethod
    @property
    def tui_column_titles(cls):
        return [
            "",
            "Name",
            Text("Health", justify="center"),
            Text(Icons.DAMAGE, justify="center"),
            Text(Icons.ARMOR, justify="center"),
            Text(Icons.LEVEL, justify="center"),
            Text(Icons.XP, justify="center"),
            Text(Icons.GRAVEYARD, justify="center"),
        ]

    @property
    def tui_arr(self):
        return [
            str(self.icon),
            self.name.split()[0],
            get_health_bar(self.health, self.max_health),
            Text.from_markup(f"[red1]{self.stats['damage']}[/]", justify="right"),
            Text.from_markup(f"[dodger_blue1]{self.stats['armor']}[/]", justify="right"),
            Text.from_markup(f"[cyan1]{self.level}[/]", justify="right"),
            Text.from_markup(
                f"[magenta1]{self.experience}/{fibonacci(self.level + 1)}[/]",
                justify="right",
            ),
            "🪦" if self.is_ghost else " ",
        ]

    @classmethod
    @property
    def abbreviated_tui_column_titles(cls):
        return [x for i, x in enumerate(cls.tui_column_titles) if i != 2]

    @property
    def abbreviated_tui_arr(self):
        return [x for i, x in enumerate(self.tui_arr) if i != 2]

