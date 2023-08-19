import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

from rich.console import RenderableType
from rich.table import Table

from myning.config import CONFIG
from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.generators import (
    generate_character,
    generate_enemy_army,
    generate_equipment,
    generate_mineral,
    generate_reward,
)
from myning.utils.race_rarity import get_recruit_species
from myning.utils.string_generation import generate_death_action
from myning.utils.ui_consts import Icons
from new_tui.formatter import Formatter

player = Player()
trip = Trip()


class Action(ABC):
    def __init__(self, duration=5):
        self.duration = min(duration, trip.seconds_left)

    def tick(self):
        self.duration -= 1

    @property
    @abstractmethod
    def content(self) -> RenderableType:
        pass

    @property
    def next(self) -> "Action | None":
        return None


class MineralAction(Action):
    def __init__(self):
        duration = random.randint(0, int(CONFIG["tick_length"] + trip.seconds_left / 60)) + 5
        super().__init__(duration)

    @property
    def content(self):
        return "\n".join(
            [
                f"Mining... ({self.duration} seconds left)\n",
                "💎  " * (5 - (self.duration - 1) % 5),
            ]
        )

    @property
    def next(self):
        mineral = generate_mineral(trip.mine.max_item_level, trip.mine.resource)
        return ItemAction(mineral)


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
        duration = int(CONFIG["tick_length"] / 5) + 3
        super().__init__(duration)

    @property
    def content(self):
        content_table = Table.grid()
        content_table.add_row("[orange1]Oh no! You're under attack[/]\n")
        content_table.add_row(f"[bold]Round {self.round}[/]")
        content_table.add_row(f"Fighting... ({self.duration} seconds left)\n")
        content_table.add_row("⚔️   " * (5 - (self.duration - 1) % 5))
        content_table.add_row("\n[bold]Your Army[/]")
        content_table.add_row(*Army(player.army.living_members).tui_columns)
        content_table.add_row("\n[bold]Enemy Army[/]")
        content_table.add_row(*Army(self.enemies.living_members).tui_columns)
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

    @property
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
        rewards = generate_reward(trip.mine.max_item_level, enemy_count)
        for reward in rewards:
            trip.add_item(reward)
        FileManager.multi_save(trip, *rewards)
        self.rewards = rewards
        super().__init__(len(rewards) + 1)

    @property
    def content(self):
        lines = ["[green1]You won the battle![/]\n"] + [
            item.tui_new_text for item in self.rewards[: len(self.rewards) - self.duration + 1]
        ]
        return "\n".join(lines)

    @property
    def next(self):
        return self if self.duration else None


class ItemAction(Action):
    def __init__(self, item: Item):
        self.item = item
        trip.add_item(item)
        FileManager.multi_save(item, trip)
        super().__init__(2)

    @property
    def content(self):
        return self.item.tui_new_text


class EquipmentAction(ItemAction):
    def __init__(self):
        equipment = generate_equipment(trip.mine.max_item_level)
        super().__init__(equipment)


class RecruitAction(Action):
    def __init__(self):
        levels = trip.mine.character_levels
        levels = [max(1, math.ceil(level * 0.75)) for level in levels]
        species = get_recruit_species(trip.mine.companion_rarity)
        ally = generate_character(levels, race=species)
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
        player.kill_ally(ally)
        trip.remove_ally(ally)
        FileManager.multi_save(trip, player)
        reason = generate_death_action()
        self.message = (
            f"[dodger_blue1]{ally.icon} {ally.name} was almost {reason}.[/]\n\n"
            "Luckily, they're a ghost"
            if ally.is_ghost
            else f"[red1]Oh no! ally.icon {ally.name} has died![/]\n\nCause of death: {reason}"
        )
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
