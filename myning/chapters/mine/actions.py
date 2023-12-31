import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache

from rich.console import RenderableType
from rich.table import Table
from textual.widget import Widget

from myning.chapters.mine.mining_minigame import MiningMinigame, MiningScore
from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.graveyard import Graveyard
from myning.objects.inventory import Inventory
from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.objects.stats import IntegerStatKeys, Stats
from myning.objects.trip import Trip
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.generators import (
    generate_character,
    generate_enemy_army,
    generate_equipment,
    generate_mineral,
    generate_reward,
)
from myning.utilities.species_rarity import get_recruit_species
from myning.utilities.string_generation import generate_death_action
from myning.utilities.tab_title import TabTitle
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


@dataclass
class RoundLog:
    attacker: Character
    defender: Character
    is_friendly: bool
    damage: int
    dodged: bool
    critted: bool


class CombatAction(Action):
    # pylint: disable=redefined-builtin
    def __init__(self, *, enemies: Army | None = None, round=1):
        if enemies:
            self.enemies = enemies
        else:
            assert trip.mine
            if trip.mine.enemies[1] < 0:
                trip.mine.enemies[1] = len(player.army) + trip.mine.enemies[1]
            self.enemies = generate_enemy_army(
                trip.mine.character_levels,
                trip.mine.enemies,
                trip.mine.max_enemy_items,
                trip.mine.max_enemy_item_level,
                trip.mine.enemy_item_scale,
            )
        self.round = round
        self.round_logs: list[RoundLog] = []
        self.damage_done = 0
        self.damage_taken = 0
        TabTitle.change_tab_subactivity(
            f"⚔️ Battling ({player.species.icon}{len(player.army.living_members)} "
            f"v 👽{len(self.enemies.living_members)})"
        )
        duration = random.randint(5, 9)
        super().__init__(duration)

    @property
    def content(self):
        player_army = Army(player.army.living_members)
        enemy_army = Army(self.enemies.living_members)
        content_table = Table.grid()
        content_table.add_row("[orange1]Oh no! You're under attack[/]\n")
        content_table.add_row(f"[bold]Round {self.round}[/]")
        content_table.add_row(f"Fighting... ({self.duration} seconds left)\n")
        content_table.add_row("⚔️   " * (5 - (self.duration - 1) % 5))
        content_table.add_row("\n[bold]Your Army[/]")
        content_table.add_row(
            player_army.compact_view if settings.compact_mode else player_army.battle_view
        )
        content_table.add_row("\n[bold]Enemy Army[/]")
        content_table.add_row(
            enemy_army.compact_view if settings.compact_mode else enemy_army.battle_view
        )
        return content_table

    def fight(self):
        battle_order = _get_battle_order(player.army.living_members, self.enemies.living_members)
        # bonus = _mini_game_bonus(static_menu)
        for attacker in battle_order:
            if player.army.defeated or self.enemies.defeated:
                break

            is_friendly = attacker in player.army
            defender = random.choice(
                self.enemies.living_members if is_friendly else player.army.living_members
            )
            damage, dodged, crit = _calculate_damage(attacker, defender)

            if damage > 0:
                if not dodged:
                    defender.subtract_health(damage)
                self.round_logs.append(
                    RoundLog(
                        attacker=attacker,
                        defender=defender,
                        is_friendly=is_friendly,
                        damage=damage,
                        dodged=dodged,
                        critted=crit,
                    )
                )
            if is_friendly:
                self.damage_done += damage
                FileManager.save(attacker)
            else:
                self.damage_taken += damage
                FileManager.save(defender)

            if defender.health <= 0:
                battle_order.remove(defender)
                if is_friendly:
                    stats.increment_int_stat(IntegerStatKeys.FALLEN_SOLDIERS)
                    FileManager.save(stats)

    @property
    @lru_cache(maxsize=1)
    def next(self):
        self.fight()
        if player.army.defeated:
            return None
        if self.enemies.defeated:
            trip.add_battle(len(self.enemies), True)
            FileManager.save(trip)
            return VictoryAction(len(self.enemies))
        next_combat_action = CombatAction(enemies=self.enemies, round=self.round + 1)
        return RoundAction(
            self.damage_done,
            self.damage_taken,
            self.round_logs,
            next_combat_action,
        )


class RoundAction(Action):
    def __init__(
        self, damage_done: int, health_lost: int, round_logs: list[RoundLog], next_action: Action
    ):
        self.damage_done = damage_done
        self.health_lost = health_lost
        self.next_action = next_action
        damage_width = max(len(str(self.damage_done)), len(str(self.health_lost)))
        self.summary = (
            "[bold]Round Summary[/]\n\n"
            f"[bold green1]{self.damage_done:{damage_width}}[/] damage inflicted.\n"
            f"[bold red1]{self.health_lost:{damage_width}}[/] damage sustained.\n"
        )
        self.log_table = Table.grid(padding=(0, 1, 0, 0))
        if round_logs:
            for log in round_logs:
                self.log_table.add_row(
                    str(log.attacker.icon),
                    f"[{'green1' if log.is_friendly else 'red1'}]{log.attacker.name}[/]",
                    Icons.CRIT if log.critted else "",
                    "[bold dark_cyan](0)[/]"
                    if log.dodged
                    else f"[{'bold orange1' if log.critted else 'normal'}]{log.damage}[/]",
                    Icons.DODGE if log.dodged else "",
                    str(log.defender.icon),
                    f"[{'red1' if log.is_friendly else 'green1'}]{log.defender.name}[/]",
                    Icons.DEATH if log.defender.health <= 0 else "",
                )
            self.log_table.columns[3].justify = "right"
        super().__init__(5)

    @property
    def content(self):
        table = Table.grid(expand=True)
        table.add_row(self.summary)
        table.add_row(f"Returning to battle in {self.duration}...\n")
        table.add_row(self.log_table)
        return table

    @property
    def next(self):
        return self.next_action


class VictoryAction(Action):
    def __init__(self, enemy_count: int):
        TabTitle.change_tab_subactivity("")
        assert trip.mine
        rewards = generate_reward(trip.mine.max_item_level, enemy_count)
        trip.add_items(*rewards)
        FileManager.multi_save(trip, *rewards)
        self.rewards = rewards
        super().__init__(len(rewards) + 1)

    @property
    def content(self):
        lines = ["[green1]You won the battle![/]\n"] + [
            item.battle_new_str for item in self.rewards[: len(self.rewards) - self.duration + 1]
        ]
        return "\n".join(lines)

    @property
    def next(self):
        return self if self.duration > 1 else None


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


def _get_battle_order(allies: list[Character], enemies: list[Character]):
    combined = allies + enemies
    random.shuffle(combined)
    return combined


def _calculate_damage(attacker: Character, defender: Character, bonus=1):
    dodge_chance = int(defender.stats["dodge_chance"])
    dodge = random.choices(
        [True, False],
        weights=[dodge_chance, 100 - dodge_chance],
    )[0]

    critical_chance = int(attacker.stats["critical_chance"])
    crit = random.choices(
        [True, False],
        weights=[critical_chance, 100 - critical_chance],
    )[0]

    damage = attacker.stats["damage"]
    damage = random.randint(0, damage)
    damage = int(bonus * damage)
    if crit:
        damage *= 2

    armor = defender.stats["armor"]
    blocked = random.randint(0, max(armor, 0))
    damage -= blocked
    damage = max(damage, 0)
    return damage, dodge, crit
