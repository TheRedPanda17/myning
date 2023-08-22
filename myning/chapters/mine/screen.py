import random
import time
from typing import Type

from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, ProgressBar, Static

from myning.chapters.mine.actions import (
    Action,
    CombatAction,
    EquipmentAction,
    ItemAction,
    LoseAllyAction,
    MineralAction,
    RecruitAction,
    RoundAction,
    VictoryAction,
)
from myning.config import MINE_TICK_LENGTH, TICK_LENGTH, VICTORY_TICK_LENGTH
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.tui.header import Header
from myning.utilities.pick import throttle
from myning.utilities.tab_title import TabTitle
from myning.utilities.ui import Icons

player = Player()
trip = Trip()
ACTIONS: dict[str, Type[Action]] = {
    "combat": CombatAction,
    "mineral": MineralAction,
    "equipment": EquipmentAction,
    "recruit": RecruitAction,
    "lose_ally": LoseAllyAction,
}


def time_str(seconds: int):  # sourcery skip: assign-if-exp, reintroduce-else
    if seconds <= 0:
        return "0s"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


class MineScreen(Screen[bool]):
    BINDINGS = [
        ("ctrl+q", "abandon", "Abandon Mine"),
        ("enter", "skip", "Mine/Fight"),
    ]

    def __init__(self) -> None:
        self.content_container = ScrollableContainer()
        self.content = Static()
        self.summary = Static()
        self.progress = ProgressBar(total=trip.total_seconds, show_eta=False)
        self.time = Static()
        self.action = self.random_action
        self.abandoning = False
        self.last_skip_time = 0
        super().__init__()

    def compose(self):
        yield Header()
        with self.content_container:
            self.content_container.border_title = f"{trip.mine.icon} {trip.mine.name}"
            yield self.content
        with Container() as c:
            c.border_title = "Trip Summary"
            yield self.summary
        with Container() as c:
            c.border_title = "Trip Progress"
            yield self.time
            yield self.progress
        yield Footer()

    def on_mount(self):
        self.tick()
        self.set_interval(TICK_LENGTH, self.tick)

    @property
    def next_action(self):
        return self.action.next or self.random_action

    @property
    def random_action(self):
        odds = trip.mine.odds.copy()
        if not player.allies:
            odds = [o for o in odds if o["action"] != "lose_ally"]
        actions = [o["action"] for o in odds]
        chances = [o["chance"] for o in odds]
        selected_action = random.choices(actions, weights=chances)[0]
        return ACTIONS[selected_action]()

    def tick(self):
        if self.abandoning:
            return
        self.update_screen()
        self.action.tick()

        trip.seconds_passed(TICK_LENGTH)
        if (
            trip.seconds_left <= 0
            and not isinstance(self.action, (CombatAction, RoundAction))
            or player.army.defeated
        ):
            self.exit()

        if self.action.duration <= 0:
            self.action = self.next_action

    def update_screen(self):
        self.content.update(self.action.content)
        self.summary.update(trip.summary)
        self.progress.progress = trip.total_seconds - trip.seconds_left
        time_left = time_str(trip.seconds_left)
        self.time.update(f"{time_left} remaining")
        TabTitle.change_tab_status(f"{time_left} remaining in {trip.mine.icon} {trip.mine.name}")

    @throttle(min(MINE_TICK_LENGTH, TICK_LENGTH, VICTORY_TICK_LENGTH))
    def action_skip(self):
        if self.abandoning:
            self.abandoning = False
        elif player.army.defeated:
            self.exit()
        elif isinstance(self.action, ItemAction):
            if self.check_skip(TICK_LENGTH):
                self.action.tick()
                self.skip()
        elif isinstance(self.action, VictoryAction):
            if self.check_skip(VICTORY_TICK_LENGTH):
                self.action.tick()
                self.skip()
        elif self.check_skip(MINE_TICK_LENGTH):
            trip.seconds_passed(self.action.duration)
            self.skip()

    def check_skip(self, interval: float):
        current_time = time.time()
        skippable = current_time - self.last_skip_time >= interval
        if skippable:
            self.last_skip_time = current_time
        return skippable

    def skip(self):
        self.action = self.next_action
        self.flash_border()
        self.update_screen()

    def flash_border(self):
        self.content_container.styles.border = ("round", "lime")
        self.set_timer(TICK_LENGTH / 2, self.reset_border)

    def reset_border(self):
        self.content_container.styles.border = ("round", "dodgerblue")

    def action_abandon(self):
        if self.abandoning:
            self.exit()
        else:
            self.confirm_abandon()

    def confirm_abandon(self):
        self.content.update(
            "Are you sure you want to abandon your trip?\n\n"
            f"[bold red1]{Icons.WARNING}  WARNING {Icons.WARNING}[/]\n\n"
            "You will not receive any items you found or any allies you recruited.\n"
            "In addition, lost allies and damage sustained will not be recovered.\n\n"
            "Press [bold dodger_blue1]CTRL+Q[/] again to abandon, "
            "or [bold dodger_blue1]Enter ↩[/] to continue."
        )
        self.abandoning = True

    def exit(self):
        self.dismiss(self.abandoning)
