import random
from functools import partial
from typing import TYPE_CHECKING

from rich.table import Table
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, ProgressBar, Static

from myning.chapters import DynamicArgs, Option, PickArgs, main_menu, tutorial
from myning.config import HEAL_TICK_LENGTH, UPGRADES
from myning.objects.army import Army
from myning.objects.player import Player
from myning.tui.header import Header
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import throttle

if TYPE_CHECKING:
    from myning.chapters import ChapterWidget

player = Player()


def members_to_heal(members: Army):
    return [m for m in members if m.health < m.max_health]


def healthy():
    return PickArgs(
        message="Everyone is healthy.",
        options=[
            Option("Okay", main_menu.enter if tutorial.is_complete() else tutorial.learn_bindings)
        ],
    )


def enter():
    if not members_to_heal(player.army):
        return healthy()

    options: list[Option] = []
    if player.has_upgrade("insta_heal"):
        cost = UPGRADES["insta_heal"].player_value * len(player.army)
        options.append(
            Option(
                f"Instant ({Formatter.gold(cost) if cost else 'free'})", partial(insta_heal, cost)
            )
        )
        # hide slow option if instant is free
        if cost:
            options.append(Option("Slowly (free)", slow_heal))
    else:
        options = [Option("Yes (free)", slow_heal)]
    options.append(
        Option("No", main_menu.enter if tutorial.is_complete() else tutorial.learn_bindings)
    )

    return PickArgs(message="Start Recovery?", options=options)


def insta_heal(cost: int):
    if player.gold < cost:
        return PickArgs(message="You can't afford it.", options=[Option("Darn!", enter)])
    for member in player.army:
        member.health = member.max_health
        FileManager.save(member)
    player.gold -= cost
    FileManager.save(player)
    return healthy()


def slow_heal():
    return DynamicArgs(callback=healer_callback)


def healer_callback(chapter: "ChapterWidget"):
    def screen_callback(_):
        return chapter.pick(healthy())

    chapter.clear()
    chapter.app.push_screen(HealScreen(), screen_callback)


class HealScreen(Screen[None]):
    BINDINGS = [("enter", "skip", "Heal")]

    def __init__(self) -> None:
        self.content_container = ScrollableContainer()
        self.content = Static()
        self.progress = ProgressBar(total=player.army.total_health)
        super().__init__()

    def compose(self):
        yield Header()
        with self.content_container:
            self.content_container.border_title = "Healer"
            yield self.content
        with Container() as c:
            c.border_title = "Estimated Time Remaining"
            yield self.progress
        yield Footer()

    def on_mount(self):
        self.tick()
        self.set_interval(1, self.tick)

    def update_screen(self):
        table = Table.grid()
        table.add_row(f"Recovering... (press {Formatter.keybind('Enter ↩')} to speed up)\n")
        table.add_row(player.army.healer_view)
        self.content.update(table)
        self.progress.progress = player.army.current_health

    def flash_border(self):
        self.content_container.styles.border = ("round", "lime")
        self.set_timer(0.5, self.reset_border)

    def reset_border(self):
        self.content_container.styles.border = ("round", "dodgerblue")

    @throttle(HEAL_TICK_LENGTH)
    def action_skip(self):
        if not self.heal():
            self.exit()
        self.flash_border()
        self.update_screen()

    def tick(self):
        self.update_screen()
        if not self.heal():
            self.exit()

    def exit(self):
        if self.app.screen is self:  # Prevent crash from holding enter
            self.dismiss(None)  # Needs a result to call the callback

    def heal(self):
        if need_healing := members_to_heal(player.army):
            heal_amount = random.randint(1, len(player.army))
            member = random.choice(need_healing)
            member.health = min(member.health + heal_amount, member.max_health)
            FileManager.save(member)
        still_need_healing = members_to_heal(player.army)
        return bool(still_need_healing)
