import random
import time
from typing import Type

from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, ProgressBar, Static

from myning.chapters.mine.actions import (
    Action,
    CombatAction,
    EquipmentAction,
    ItemsAction,
    LoseAllyAction,
    MineralAction,
    RecruitAction,
    VictoryAction,
)
from myning.chapters.mine.mining_minigame import MiningScore
from myning.config import MINE_TICK_LENGTH, TICK_LENGTH, VICTORY_TICK_LENGTH
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.objects.trip import Trip
from myning.tui.header import Header
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import throttle
from myning.utilities.tab_title import TabTitle
from myning.utilities.ui import Icons, get_time_str

player = Player()
settings = Settings()
trip = Trip()

ACTIONS: dict[str, Type[Action]] = {
    "combat": CombatAction,
    "mineral": MineralAction,
    "equipment": EquipmentAction,
    "recruit": RecruitAction,
    "lose_ally": LoseAllyAction,
}


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
            assert trip.mine
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
        self.update_screen()
        self.set_interval(TICK_LENGTH, self.tick)

    @throttle(min(MINE_TICK_LENGTH, TICK_LENGTH, VICTORY_TICK_LENGTH))
    def action_skip(self):
        if self.abandoning:
            self.abandoning = False
            if isinstance(self.action, MineralAction):
                self.action.game.toggle_paused()
                self.update_screen()
        elif self.should_exit:
            self.exit()
        elif isinstance(self.action, MineralAction):
            if settings.mini_games_disabled:
                content = str(self.content._renderable)  # pylint: disable=protected-access
                if "disabled" not in content:
                    self.content.update(
                        content
                        + "\n\nMinigames have been disabled; you can enable them in the settings."
                    )
                return
            match self.action.game.score:
                case MiningScore.GREEN:
                    color = "lime"
                    trip.seconds_passed(self.action.duration)
                case MiningScore.YELLOW:
                    color = "yellow"
                    trip.seconds_passed(self.action.duration)
                case MiningScore.ORANGE:
                    color = "orange"
                case MiningScore.RED:
                    color = "red"
                    trip.seconds_passed(-10)
                    for member in player.army.living_members:
                        member.health -= 1
                    FileManager.multi_save(*player.army)
            self.skip(color)
        elif isinstance(self.action, ItemsAction):
            if self.check_skip(TICK_LENGTH):
                trip.seconds_passed(TICK_LENGTH)
                self.skip()
        elif isinstance(self.action, VictoryAction):
            if self.check_skip(VICTORY_TICK_LENGTH):
                trip.seconds_passed(TICK_LENGTH)
                self.action.tick()  # Need to tick here because VictoryAction.next returns itself
                self.skip()
        elif self.check_skip(MINE_TICK_LENGTH):
            trip.seconds_passed(self.action.duration)
            self.skip()

    def action_abandon(self):
        if self.abandoning:
            self.exit()
        else:
            self.confirm_abandon()

    def tick(self):
        if self.abandoning:
            return

        trip.seconds_passed(TICK_LENGTH)
        if self.should_exit:
            self.exit()
            return

        self.update_screen()
        self.action.tick()
        if self.action.duration <= 0:
            self.action = self.next_action

    def update_screen(self):
        if not trip.mine:
            return
        if isinstance(self.action.content, Widget):
            self.content_container.mount(self.action.content, before=0)
            self.content.update("")
        else:
            self.content.update(self.action.content)
        trip_summary = trip.summary
        trip_summary.add_row(
            Icons.HEART, "Army health:", f"{player.army.current_health}/{player.army.total_health}"
        )
        self.summary.update(trip_summary)
        self.progress.progress = trip.total_seconds - trip.seconds_left
        time_left = get_time_str(trip.seconds_left)
        self.time.update(f"{time_left} remaining")
        TabTitle.change_tab_status(f"{time_left} remaining in {trip.mine.icon} {trip.mine.name}")

    def check_skip(self, interval: float):
        current_time = time.time()
        skippable = current_time - self.last_skip_time >= interval
        if skippable:
            self.last_skip_time = current_time
        return skippable

    def skip(self, color: str | None = None):
        self.action = self.next_action
        self.flash_border(color)
        self.update_screen()

    def flash_border(self, color: str | None = None):
        self.content_container.styles.border = ("round", color or "lime")
        self.set_timer(TICK_LENGTH / 2, self.reset_border)

    def reset_border(self):
        self.content_container.styles.border = ("round", "dodgerblue")

    def confirm_abandon(self):
        if isinstance(self.action, MineralAction):
            self.action.game.toggle_paused()
        self.content.update(
            "Are you sure you want to abandon your trip?\n\n"
            f"[bold red1]{Icons.WARNING}  WARNING {Icons.WARNING}[/]\n\n"
            "You will not receive any items you found or any allies you recruited.\n"
            "In addition, lost allies and damage sustained will not be recovered.\n\n"
            f"Press {Formatter.keybind('CTRL+Q')} again to abandon, "
            f"or {Formatter.keybind('Enter ↩')} to continue."
        )
        self.abandoning = True

    def exit(self):
        if self.app.screen is self:  # Prevent crash from holding enter
            self.dismiss(self.abandoning)

    @property
    def should_exit(self):
        return trip.seconds_left <= 0 and not self.action.next or player.army.defeated

    @property
    def next_action(self):
        return self.action.next or self.random_action

    @property
    def random_action(self):
        assert trip.mine
        odds = trip.mine.odds.copy()
        if not player.allies:
            odds = [o for o in odds if o["action"] != "lose_ally"]
        actions = [o["action"] for o in odds]
        chances = [o["chance"] for o in odds]
        selected_action = random.choices(actions, weights=chances)[0]
        return ACTIONS[selected_action]()
