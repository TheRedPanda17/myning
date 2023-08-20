import random
from typing import Type

from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, ProgressBar, Static

from myning.chapters.mine.actions import (
    Action,
    CombatAction,
    EquipmentAction,
    LoseAllyAction,
    MineralAction,
    RecruitAction,
    VictoryAction,
)
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.utilities.pick import throttle
from myning.utilities.tab_title import TabTitle
from myning.utilities.ui import Icons
from myning.view.header import Header

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
        self.set_interval(1, self.tick)

    def update_screen(self):
        if self.abandoning:
            return
        self.content.update(self.action.content)
        self.summary.update(trip.tui_summary)
        self.progress.progress = trip.total_seconds - trip.seconds_left
        time_left = time_str(trip.seconds_left)
        self.time.update(f"{time_left} remaining")
        TabTitle.change_tab_status(f"{time_left} remaining in {trip.mine.icon} {trip.mine.name}")

    def flash_border(self):
        og_border = self.content_container.styles.border

        def reset_border():
            self.content_container.styles.border = og_border

        self.content_container.styles.border = ("round", "lime")
        self.set_timer(0.5, reset_border)

    def action_abandon(self):
        if self.abandoning:
            self.exit()
        else:
            self.confirm_abandon()

    @throttle(1)
    def action_skip(self):
        if self.abandoning:
            self.abandoning = False
        elif player.army.defeated:
            self.exit()
        elif not isinstance(self.action, VictoryAction):
            trip.tick_passed(self.action.duration)
        self.action = self.next_action
        self.flash_border()
        self.update_screen()

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

    def tick(self):
        if self.abandoning:
            return
        self.update_screen()
        self.action.tick()

        trip.tick_passed(1)
        if trip.seconds_left <= 0 or player.army.defeated:
            self.exit()

        if self.action.duration <= 0:
            self.action = self.next_action

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
