import math
import random
from abc import ABC, abstractmethod
from functools import lru_cache

from rich.console import RenderableType
from textual.widget import Widget

from myning.chapters.mine.mining_minigame import MiningMinigame, MiningScore
from myning.objects.graveyard import Graveyard
from myning.objects.inventory import Inventory
from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.objects.stats import Stats
from myning.objects.trip import Trip
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.generators import generate_character, generate_equipment, generate_mineral
from myning.utilities.species_rarity import get_recruit_species
from myning.utilities.string_generation import generate_death_action
from myning.utilities.ui import Icons

player = Player()
settings = Settings()
stats = Stats()
trip = Trip()
graveyard = Graveyard()
inventory = Inventory()


class Action(ABC):
    def __init__(self, duration=5):
        self.duration = duration

    def tick(self):
        self.duration -= 1

    @property
    @abstractmethod
    def content(self) -> RenderableType | Widget:
        pass

    @property
    def next(self) -> "Action | None":
        return None


class MineralAction(Action):
    def __init__(self):
        duration = random.randint(5, trip.seconds_left // 60 + 30)
        self.game = MiningMinigame(duration)
        super().__init__(duration)

    @property
    def content(self):
        if settings.mini_games_disabled:
            return "\n".join(
                [
                    f"Mining... ({self.duration} seconds left)\n",
                    "💎  " * (5 - (self.duration - 1) % 5),
                ]
            )
        return self.game

    @property
    @lru_cache(maxsize=1)
    def next(self):
        if not trip.mine:
            return None
        if settings.mini_games_disabled or self.duration == 0:
            return ItemsAction(
                [generate_mineral(trip.mine.max_item_level, trip.mine.resource)],
                "You found a mineral!",
            )
        minerals = []
        match self.game.score:
            case MiningScore.GREEN:
                minerals.extend(
                    generate_mineral(trip.mine.max_item_level, trip.mine.resource) for _ in range(2)
                )
                return ItemsAction(
                    minerals,
                    "[bold green1]Fantastic![/]\n\n"
                    "You've struck a rich mineral layer while mining and find twice the amount of "
                    "minerals!\n"
                    f"Your progress has been advanced by [bold]{self.duration}[/] seconds.\n\n"
                    "Keep up the good work, miner!",
                )
            case MiningScore.YELLOW:
                minerals.append(generate_mineral(trip.mine.max_item_level, trip.mine.resource))
                return ItemsAction(
                    minerals,
                    "[bold yellow1]Alright![/]\n\n"
                    "You succesfully mine a mineral, and your progress has been advanced by "
                    f"[bold]{self.duration}[/] seconds.",
                )
            case MiningScore.ORANGE:
                return ItemsAction(
                    [],
                    "[bold orange1]Drat![/]\n\n"
                    "You've encountered an unexpected pocket of mineral-free rock while mining.\n\n"
                    "Try a little harder for better prospects!",
                )
            case MiningScore.RED:
                return ItemsAction(
                    [],
                    "[bold red1]Ouch![/]\n\n"
                    "You've struck a rocky vein while mining, and take some damage as a result.\n"
                    "Your progress has been delayed by [bold]10[/] seconds.\n\n"
                    "Be more careful with your swings!",
                )


class ItemsAction(Action):
    def __init__(self, items: list[Item], message: str):
        self.items = items
        trip.add_items(*items)
        FileManager.multi_save(*items, trip)
        self.message = message + "\n\n" + "\n".join(item.battle_new_str for item in self.items)
        super().__init__(5)

    @property
    def content(self):
        return self.message


class EquipmentAction(ItemsAction):
    def __init__(self):
        assert trip.mine
        equipment = generate_equipment(trip.mine.max_item_level)
        super().__init__([equipment], "You've found a piece of equipment!")


class RecruitAction(Action):
    def __init__(self):
        assert trip.mine
        levels = trip.mine.character_levels
        levels = [max(1, math.ceil(level * 0.75)) for level in levels]
        species = get_recruit_species(trip.mine.companion_rarity)
        ally = generate_character(levels, species=species)
        trip.add_ally(ally)
        FileManager.multi_save(trip, ally)
        self.message = "\n\n".join(
            [
                "[green1]You have recruited an ally![/]",
                f"{ally.icon} [bold]{ally.name}[/] ({Icons.LEVEL} {Formatter.level(ally.level)})",
                f"{ally.introduction} I'd like to join your army.",
            ]
        )
        super().__init__(5)

    @property
    def content(self):
        return self.message


class LoseAllyAction(Action):
    def __init__(self):
        ally = random.choice(player.allies)
        reason = generate_death_action()
        if ally.is_ghost:
            self.message = (
                f"[dodger_blue1]{ally.icon} {ally.name} was almost {reason}.[/]\n\n"
                "Luckily, they're a ghost."
            )
        else:
            self.message = (
                f"[red1]Oh no! {ally.icon} {ally.name} has died![/]\n\nCause of death: {reason}."
            )
            player.remove_ally(ally)
            for item in ally.equipment.all_items:
                inventory.add_item(item)
                ally.equipment.clear()

            trip.remove_ally(ally)
            graveyard.add_fallen_ally(ally)
            FileManager.multi_save(trip, player, graveyard, inventory)
        super().__init__(5)

    @property
    def content(self):
        return self.message


# pylint: disable=wrong-import-position
from .combat import *
