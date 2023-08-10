import random
from typing import Type

from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, ProgressBar, Static

from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.utils.ui_consts import Icons
from new_tui.actions import (
    Action,
    CombatAction,
    EquipmentAction,
    LoseAllyAction,
    LossAction,
    MineAction,
    RecruitAction,
    VictoryAction,
)
from new_tui.utilities import throttle
from new_tui.view.header import Header

player = Player()
trip = Trip()
ACTIONS: dict[str, Type[Action]] = {
    "combat": CombatAction,
    "mineral": MineAction,
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


class Content(Static):
    def print(self, content):
        self.update(content)


class Summary(Static):
    def on_mount(self):
        self.update_summary()
        self.set_interval(1, self.update_summary)

    def update_summary(self):
        self.update(trip.tui_summary)


class TimeRemaining(Static):
    def on_mount(self) -> None:
        self.set_interval(0.1, self.update_time)

    def update_time(self):
        self.update(f"{time_str(trip.seconds_left)} remaining")


class MineScreen(Screen):
    BINDINGS = [
        ("ctrl+q", "abandon", "Abandon Mine"),
        ("enter", "skip", "Mine/Fight"),
    ]

    def __init__(self) -> None:
        self.content_container = ScrollableContainer()
        self.content = Content()
        self.progress = ProgressBar(total=trip.total_seconds, show_eta=False)
        self.action: Action = ACTIONS["mineral"]()
        self.abandoning = False
        super().__init__()

    def compose(self):
        yield Header()
        with self.content_container:
            self.content_container.border_title = f"{trip.mine.icon} {trip.mine.name}"
            yield self.content
        with Container() as c:
            c.border_title = "Trip Summary"
            yield Summary()
        with Container() as c:
            c.border_title = "Trip Progress"
            yield TimeRemaining()
            yield self.progress
        yield Footer()

    def on_mount(self):
        self.tick()
        self.set_interval(1, self.tick)

    def update_screen(self):
        if self.abandoning:
            return
        self.progress.progress = trip.total_seconds - trip.seconds_left
        self.content.print(self.action.content)

    def action_abandon(self):
        if self.abandoning:
            self.exit()
        else:
            self.confirm_abandon()

    @throttle(1)
    def action_skip(self):
        if self.abandoning:
            self.abandoning = False
        elif isinstance(self.action, LossAction):
            self.exit()
        elif not isinstance(self.action, VictoryAction):
            trip.tick_passed(self.action.duration)

        og_border = self.content_container.styles.border

        def reset_border():
            self.content_container.styles.border = og_border

        self.content_container.styles.border = ("round", "lime")
        self.set_timer(0.5, reset_border)
        self.action = self.next_action
        self.update_screen()

    def confirm_abandon(self):
        self.content.print(
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
        if (
            trip.seconds_left <= 0
            # When defeated, automatically exit only after LossAction is finished
            or player.army.defeated
            and isinstance(self.action, LossAction)
            and self.action.duration <= 0
        ):
            self.exit()

        if self.action.duration <= 0:
            self.action = self.next_action

    @property
    def next_action(self):
        if self.action.next:
            return self.action.next

        odds = trip.mine.odds.copy()
        if not player.allies:
            odds = [o for o in odds if o["action"] != "lose_ally"]
        actions = [o["action"] for o in odds]
        chances = [o["chance"] for o in odds]
        selected_action = random.choices(actions, weights=chances)[0]
        return ACTIONS[selected_action]()
