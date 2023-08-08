import random
from abc import ABC, abstractmethod

from rich.console import RenderableType
from rich.table import Table

from myning.config import CONFIG
from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_mineral, generate_reward
from myning.utils.output import damage_string
from myning.utils.string_generation import generate_death_action
from new_tui.formatter import Formatter
from new_tui.view.army import get_army_columns

player = Player()
trip = Trip()


class Action(ABC):
    def __init__(self, duration: int):
        self.duration = duration

    def tick(self):
        self.duration -= 1

    @property
    @abstractmethod
    def content(self) -> RenderableType:
        pass

    @property
    def next(self) -> "Action | None":
        return None


class MineAction(Action):
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


class CombatAction(Action):
    def __init__(self, enemies: Army, _round=1):
        self.allies = player.army
        self.enemies = enemies
        self.round = _round
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
        content_table.add_row(*get_army_columns(Army([c for c in player.army if c.health > 0])))
        content_table.add_row("\n[bold]Enemy Army[/]")
        content_table.add_row(*get_army_columns(Army([c for c in self.enemies if c.health > 0])))
        return content_table

    def fight(self):
        battle_order = _get_battle_order(self.allies, self.enemies)
        # bonus = _mini_game_bonus(static_menu)
        battle_log = []
        for attacker in battle_order:
            if not self.enemies or not self.allies:
                break

            is_friendly = attacker in self.allies
            defender = random.choice(self.enemies if is_friendly else self.allies)
            damage, dodged, crit = _calculate_damage(attacker, defender)

            if damage > 0:
                if not dodged:
                    defender.subtract_health(damage)
                battle_log.append(
                    damage_string(attacker, defender, damage, is_friendly, dodged, crit)
                )
            if is_friendly:
                self.damage_done += damage
                FileManager.save(attacker)
            else:
                self.damage_taken += damage
                FileManager.save(defender)

            if defender.health == 0:
                battle_order.remove(defender)
                if is_friendly:
                    self.enemies.remove(defender)
                else:
                    self.allies.remove(defender)

    @property
    def next(self):
        self.fight()
        if not self.allies:
            # enemy_survivors = [e for e in self.enemies if e.health > 0]
            # trip.add_battle(len(self.enemies) - len(enemy_survivors), False)
            return LossAction()
        if not self.enemies:
            # trip.add_battle(len(self.enemies), False)
            return VictoryAction(bool(self.allies), len(self.enemies))
        next_combat_action = CombatAction(self.enemies, self.round + 1)
        return RoundAction(self.damage_done, self.damage_taken, next_combat_action)


class RoundAction(Action):
    def __init__(self, damage_done: int, health_lost: int, action: Action):
        self.damage_done = damage_done
        self.health_lost = health_lost
        self.action = action
        super().__init__(2)

    @property
    def content(self):
        return (
            f"Summary: [green1]{self.damage_done}[/] damage done. "
            f"[red1]{self.health_lost}[/] damage received.\n"
        )

    @property
    def next(self):
        return self.action


class LossAction(Action):
    def __init__(
        self,
    ):
        super().__init__(5)

    @property
    def content(self):
        return "[red1]You lost the battle![/]"


class VictoryAction(Action):
    def __init__(self, victory: bool, enemy_count: int):
        self.victory = victory
        rewards = generate_reward(trip.mine.max_item_level, enemy_count)
        print([item.name for item in rewards])
        for reward in rewards:
            trip.add_item(reward)
        FileManager.multi_save(*rewards)
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


def _get_battle_order(allies: Army, enemies: Army):
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


class ItemAction(Action):
    def __init__(self, item: Item):
        self.item = item
        trip.add_item(item)
        FileManager.multi_save(item, trip)
        super().__init__(2)

    @property
    def content(self):
        return self.item.tui_new_text


class RecruitAction(Action):
    def __init__(self, ally: Character):
        self.message = "\n\n".join(
            [
                "[green1]You have recruited an ally![/]",
                f"{ally.icon} [bold]{ally.name}[/] ({Formatter.level(ally.level)})",
                f"{ally.get_introduction()} I'd like to join your army.",
            ]
        )
        super().__init__(5)

    @property
    def content(self):
        return self.message


class LoseAllyAction(Action):
    def __init__(self, ally: Character):
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
