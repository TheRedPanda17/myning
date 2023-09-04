import random
from typing import TYPE_CHECKING

from rich.table import Table
from textual import events
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import ProgressBar, Static

from myning.objects.army import Army
from myning.objects.player import Player
from myning.objects.settings import Settings

if TYPE_CHECKING:
    from myning.chapters.mine.actions.combat import CombatAction

TICKS_PER_SECOND = 12
BONUS_THRESHOLD = 2 / 3
KEYS = ["a", "s", "d", "f"]

player = Player()
settings = Settings()


class CombatMinigame(Container):
    def __init__(self, action: "CombatAction") -> None:
        super().__init__()
        self.action = action
        self.minigame = Minigame(self.action.duration)

    def compose(self):
        with Container():
            yield CombatDisplay(self.action)
            with Vertical():
                yield self.minigame
                yield ProgressBar(show_eta=False)

    def toggle_paused(self):
        self.display = self.minigame.paused
        self.minigame.paused = not self.minigame.paused
        self.minigame.focus()

    @property
    def bonus(self):
        if settings.mini_games_disabled or not self.minigame.total:
            return 1
        score = self.minigame.total_correct / self.minigame.total
        if score < BONUS_THRESHOLD:
            bonus = score - BONUS_THRESHOLD
        else:
            bonus = (score - BONUS_THRESHOLD) * 3
        return 1 + bonus


class CombatDisplay(Static):
    def __init__(self, action: "CombatAction"):
        super().__init__()
        self.action = action

    def on_mount(self):
        self.tick()
        self.set_interval(1, self.tick)

    def tick(self):
        allies = Army(player.army.living_members)
        enemies = Army(self.action.enemies.living_members)
        table = Table.grid()
        table.add_row("[orange1]Oh no! You're under attack[/]\n")
        table.add_row(f"[bold]Round {self.action.round}[/]")
        table.add_row(f"Fighting... ({self.action.duration} seconds left)\n")
        table.add_row("⚔️   " * (5 - (self.action.duration - 1) % 5))
        table.add_row("\n[bold]Your Army[/]")
        table.add_row(allies.compact_view if settings.compact_mode else allies.battle_view)
        table.add_row("\n[bold]Enemy Army[/]")
        table.add_row(enemies.compact_view if settings.compact_mode else enemies.battle_view)
        self.update(table)


class Minigame(Static):
    can_focus = True
    active_key = reactive(None)
    visible_lines = reactive([])
    color = reactive("dodger_blue1")

    def __init__(self, duration: int):
        super().__init__()
        self.paused = False

        self.lines = [""] * 12
        self.solutions: list[int | None] = [None] * 12
        for _ in range(duration * TICKS_PER_SECOND):
            position = random.randint(0, 3)
            length = random.randint(4, 6)
            shafts = ["|"] * (length - 2)
            lines = [f"  {' ' * position * 5}{char}" for char in ["▼", *shafts, "v"]]
            self.lines.extend(lines)
            self.solutions.extend([position] * length)
            # Gap
            self.lines.extend([""] * 2)
            self.solutions.extend([None] * 2)
        self.lines.reverse()
        self.solutions.reverse()

        self.total = 0
        self.total_correct = 0

    def render(self):
        table = Table.grid()
        for line in self.visible_lines:
            table.add_row(line)
        table.add_row(f"[{self.color}]════════════════════[/]")
        keys = "".join(
            f"[bold on dodger_blue1]  {key.upper()}  [/]"
            if key == self.active_key
            else f"[bold]  {key.upper()}  [/]"
            for key in KEYS
        )
        table.add_row(keys)
        return table

    def on_mount(self):
        self.focus()
        self.tick()
        self.set_interval(1 / TICKS_PER_SECOND, self.tick)

    def on_key(self, key: events.Key):
        if key.name in KEYS:
            self.active_key = key.name

    def watch_color(self):
        color = {
            "dodger_blue1": "dodgerblue",
            "green1": "lime",
            "red1": "red",
        }[self.color]
        self.styles.border = ("double", color)

    def tick(self):
        if self.paused:
            return
        self.lines.pop()
        self.solutions.pop()
        self.visible_lines = self.lines[-15:]

        if self.active_key and self.solution is not None:
            self.total += 1
            if self.correct:
                self.total_correct += 1
                self.color = "green1"
            else:
                self.color = "red1"

        if query := self.app.query("CombatMinigame ProgressBar"):
            progress = query.first(ProgressBar)
            if self.total:
                progress.total = self.total
                progress.progress = self.total_correct

    @property
    def solution(self):
        return self.solutions[-1]

    @property
    def correct(self):
        if not self.active_key:
            return False
        try:
            return KEYS.index(self.active_key) == self.solution
        except ValueError:
            return False
