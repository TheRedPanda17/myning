import random
from functools import partial
from typing import TYPE_CHECKING

from rich.table import Table
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, ProgressBar, Static

from myning.config import UPGRADES
from myning.objects.army import Army
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from new_tui.chapters import DynamicArgs, Option, PickArgs, main_menu, tutorial
from new_tui.formatter import Formatter
from new_tui.utilities import throttle
from new_tui.view.header import Header

if TYPE_CHECKING:
    from new_tui.chapters import ChapterWidget

player = Player()


def members_to_heal(members: Army):
    return [m for m in members if m.health < m.max_health]


def healthy():
    return PickArgs(
        message="Everyone is healthy.",
        options=[("Okay", main_menu.enter if tutorial.is_complete() else tutorial.learn_bindings)],
    )


def enter():
    if not members_to_heal(player.army):
        return healthy()

    options: list[Option] = []
    if player.has_upgrade("insta_heal"):
        cost = UPGRADES["insta_heal"].player_value * len(player.army)
        options.append(
            (
                f"Instant ({Formatter.gold(cost) if cost else 'free'})",
                partial(insta_heal, cost),
            )
        )
        # hide slow option if instant is free
        if cost:
            options.append(("Slowly (free)", slow_heal))
    else:
        options = [("Yes (free)", slow_heal)]
    options.append(("No", main_menu.enter if tutorial.is_complete() else tutorial.learn_bindings))

    return PickArgs(message="Start Recovery?", options=options)


def insta_heal(cost: int):
    if player.gold < cost:
        return PickArgs(message="You can't afford it.", options=[("Darn!", enter)])
    for member in player.army:
        member.health = member.max_health
        FileManager.save(member)
    return healthy()


def slow_heal():
    return DynamicArgs(callback=healer_callback)


def healer_callback(chapter: "ChapterWidget"):
    def screen_callback(_):
        return chapter.pick(healthy())

    chapter.app.push_screen(HealerScreen(), screen_callback)


class HealerScreen(Screen[None]):
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
        table.add_row("Recovering... (press enter to speed up)\n")
        table.add_row(player.army.tui_table)
        self.content.update(table)
        self.progress.progress = player.army.current_health

    def flash_border(self):
        og_border = self.content_container.styles.border

        def reset_border():
            self.content_container.styles.border = og_border

        self.content_container.styles.border = ("round", "lime")
        self.set_timer(0.5, reset_border)

    @throttle(0.1)
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
        self.dismiss(None)  # Needs a result to call the callback

    def heal(self):
        if need_healing := members_to_heal(player.army):
            heal_amount = random.randint(1, len(player.army))
            member = random.choice(need_healing)
            member.health = min(member.health + heal_amount, member.max_health)
            FileManager.save(member)
        still_need_healing = members_to_heal(player.army)
        return bool(still_need_healing)
