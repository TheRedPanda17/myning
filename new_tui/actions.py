from abc import ABC, abstractmethod
from myning.objects.army import Army

from myning.objects.character import Character
from myning.objects.item import Item
from myning.objects.trip import Trip
from myning.utils.string_generation import generate_death_action
from new_tui.formatter import Formatter

trip = Trip()


class Action(ABC):
    def __init__(self, duration: int):
        self.duration = duration

    def tick(self):
        self.duration -= 1

    @property
    @abstractmethod
    def content(self) -> str:
        pass


class MineAction(Action):
    @property
    def content(self):
        return "\n".join(
            [
                f"Mining... ({self.duration} seconds left)\n",
                "💎  " * (5 - (self.duration - 1) % 5),
            ]
        )


class CombatAction(Action):
    def __init__(self, duration: int, enemy_army: Army):
        self.enemy_army = enemy_army
        super().__init__(duration)

    def tick(self):
        if self.enemy_army:
            self.enemy_army.pop()
        else:
            self.duration = 0

    @property
    def content(self):
        return "\n".join(
            [
                "[orange1]Oh no! You're under attack[/]\n",
                *[f"{c.icon} {c.name}" for c in self.enemy_army],
            ]
        )

    def fight(self):
        self.duration = 5

    def win(self):
        self.enemy_army = Army()


class ItemAction(Action):
    def __init__(self, item: Item):
        self.item = item
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
