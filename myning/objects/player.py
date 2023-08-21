import math
import random
from typing import Optional

from myning.config import MINES, SPECIES, UPGRADES, XP_COST
from myning.objects.army import Army
from myning.objects.character import Character, CharacterSpecies
from myning.objects.inventory import Inventory
from myning.objects.item import ItemType
from myning.objects.mine import Mine
from myning.objects.mine_stats import MineStats
from myning.objects.singleton import Singleton
from myning.objects.upgrade import Upgrade
from myning.utilities.file_manager import FileManager


class Player(Character, metaclass=Singleton):
    # Remove the required argument from the constructor
    def __init__(self, name=None, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    @classmethod
    def initialize(cls, name=None):
        player = FileManager.load(Player, "player")
        if not player:
            while not name:
                name = input("\nEnter your player name: ")
            player = cls(name)
            player._allies = []
            player._fallen_allies = []
            player._fired_allies = []
            player.inventory = Inventory()
            player.gold = 1
            player.exp_available = 0
            player.mines_available = [MINES["Hole in the ground"]]
            player.upgrades = []
            player.mine_progressions = {}
            player.mines_completed = []
            player.blacksmith_level = 1
            player.soul_credits = 0
            player.discovered_species = [SPECIES[CharacterSpecies.HUMAN.value]]
            player.completed_migrations = [1]
        cls._instance = player

    @property
    def army(self):
        return Army([self, *self._allies])

    @property
    def allies(self) -> list[Character]:
        return self._allies

    @property
    def fired_allies(self) -> list[Character]:
        return self._fired_allies

    @property
    def alive(self):
        return any(member.health > 0 for member in self.army)

    @property
    def total_value(self) -> int:
        item_value = sum(item.value for item in self.inventory.items)
        army_value = sum(member.value for member in self.army)
        exp_value = self.exp_available * XP_COST
        upgrades_value = sum(sum(u.costs[: u.level]) for u in self.upgrades)

        unlocked_mines = sum(mine.cost for mine in self.mines_available)
        beaten_mines = int(
            sum(mine.win_value * math.pow(mine.cost, 1 / 3) for mine in self.mines_completed)
        )

        return (
            item_value
            + army_value
            + exp_value
            + upgrades_value
            + unlocked_mines
            + self.gold
            + upgrades_value
            + beaten_mines
        )

    def has_upgrade(self, upgrade_id):
        return upgrade_id in [upgrade.id for upgrade in self.upgrades]

    def reset(self):
        self._allies = []
        self._fallen_allies = []
        self._fired_allies = []
        self.inventory = Inventory()
        self.gold = 1
        self.exp_available = 0
        self.mines_available: list[Mine] = [MINES["Hole in the ground"]]
        self.upgrades: list[Upgrade] = []
        self.mine_progressions = {}
        self.mines_completed: list[Mine] = []
        self.blacksmith_level = 1
        self.level = 1
        self.experience = 0
        self.health = self.max_health
        self.equipment.clear()
        self.soul_credits = 0
        self.discovered_species = [SPECIES[CharacterSpecies.HUMAN.value]]
        self.completed_migrations = [1]

    def add_ally(self, ally: Character):
        self._allies.append(ally)

    def kill_ally(self, ally: Character):
        self._fallen_allies.append(ally)
        self.remove_ally(ally)

    def fire_ally(self, ally: Character):
        self._fired_allies.append(ally)
        self.remove_ally(ally)

    def move_ally_out(self, ally: Character):
        self._allies.remove(ally)

    def remove_ally(self, ally: Character):
        for item in ally.equipment.all_items:
            self.inventory.add_item(item)
        ally.equipment.clear()
        self._allies.remove(ally)

    def remove_fallen_ally(self, ally: Character):
        self._fallen_allies.remove(ally)

    def revive_ally(self, ally: Character):
        self.remove_fallen_ally(ally)
        self._allies.append(ally)

    def add_available_xp(self, xp: int):
        self.exp_available += xp

    def remove_available_xp(self, xp: int):
        if xp > 0:
            self.exp_available -= xp

    def add_soul_credits(self, credits):
        if credits > 0:
            self.soul_credits += credits

    def remove_soul_credits(self, credits: int):
        if credits > 0:
            self.soul_credits -= credits

    def get_mine_progress(self, progress_name):
        progress = self.mine_progressions.get(progress_name)
        if progress:
            return progress
        else:
            self.mine_progressions[progress_name] = MineStats(0, 0, 0)
            return self.mine_progressions[progress_name]

    def roll_for_species(self):
        species_list = self.discovered_species
        if self.species in species_list:
            species_list.remove(self.species)
        return random.choice(species_list)

    @property
    def fallen_allies(self) -> list[Character]:
        return self._fallen_allies

    @property
    def ghost_count(self):
        return len([ally for ally in self.allies if ally.is_ghost])

    @property
    def seeds(self):
        plants = self.inventory.get_slot(ItemType.PLANT)
        return [p for p in plants if p.is_seed]  # pylint: disable=not-an-iterable

    @classmethod
    @property
    def file_name(cls):
        return "player"

    def to_dict(self):
        character = super().to_dict()
        return {
            **character,
            "allies": [ally.to_dict() for ally in self._allies],
            "fallen_allies": [ally.to_dict() for ally in self._fallen_allies],
            "fired_allies": [ally.to_dict() for ally in self._fired_allies],
            "inventory": self.inventory.to_dict(),
            "gold": self.gold,
            "exp_available": self.exp_available,
            "mines_available": [mine.name for mine in self.mines_available],
            "mines_completed": [mine.name for mine in self.mines_completed],
            "upgrades": [{"id": upgrade.id, "level": upgrade.level} for upgrade in self.upgrades],
            "mine_progressions": {
                name: progress.to_dict() for name, progress in self.mine_progressions.items()
            },
            "blacksmith_level": self.blacksmith_level,
            "soul_credits": self.soul_credits,
            "discovered_races": [species.name for species in self.discovered_species],
            "completed_migrations": self.completed_migrations,
        }

    @classmethod
    def from_dict(cls, attrs: dict):
        player = super().from_dict(attrs)
        player._allies = [Character.from_dict(ally) for ally in attrs["allies"]]
        player._fallen_allies = [
            Character.from_dict(ally) for ally in attrs.get("fallen_allies", [])
        ]
        player._fired_allies = [Character.from_dict(ally) for ally in attrs.get("fired_allies", [])]
        player.inventory = Inventory.from_dict(attrs["inventory"])
        player.gold = int(attrs["gold"])
        player.exp_available = int(attrs["exp_available"])
        player.mines_available = [MINES[mine_name] for mine_name in attrs["mines_available"]]
        player.mines_available = sorted(
            player.mines_available, key=lambda mine: mine.min_player_level
        )
        player.mines_completed = [MINES[mine_name] for mine_name in attrs["mines_completed"]]
        player.upgrades = []
        for upgrade in attrs["upgrades"]:
            id = upgrade["id"] if isinstance(upgrade, dict) else upgrade
            level = upgrade["level"] if isinstance(upgrade, dict) else 1
            player.upgrades.append(UPGRADES[id])
            player.upgrades[-1].level = level
        player.mine_progressions = {
            name: MineStats.from_dict(progress)
            for name, progress in attrs["mine_progressions"].items()
        }
        player.blacksmith_level = attrs.get("blacksmith_level") or 1
        player.soul_credits = attrs.get("soul_credits") or 0
        player.discovered_species = [
            SPECIES[species_name]
            for species_name in attrs.get("discovered_races", [CharacterSpecies.HUMAN.value])
        ]
        player.completed_migrations = attrs.get("completed_migrations") or [1]
        return player
