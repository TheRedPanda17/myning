import random
from enum import Enum, auto
from functools import lru_cache

from textual.widgets import Static


class MiningScore(Enum):
    RED = auto()
    ORANGE = auto()
    YELLOW = auto()
    GREEN = auto()


COLORS = ["red1", "orange1", "yellow1", "green1", "yellow1", "orange1", "red1"]
WIDTHS = [1, 1.5, 1.5, 2, 1.5, 1.5, 1]
assert len(COLORS) == len(WIDTHS)
assert sum(WIDTHS) == 10


class MiningMinigame(Static):
    def __init__(self, duration: int):
        super().__init__()
        self.duration = duration
        self.segment_width = random.choice([2, 4, 6])
        self.segment_widths = [int(width * self.segment_width) for width in WIDTHS]
        self.width = sum(self.segment_widths)
        self.cursor = random.randint(0, self.width - 1)
        self.direction = random.choice([-1, 1])
        self.paused = False

    def on_mount(self):
        self.tick()
        self.tick_duration()
        self.set_interval(1 / 30, self.tick)
        self.set_interval(1, self.tick_duration)

    def tick(self):
        if self.paused:
            return
        self.cursor = (self.cursor + self.direction) % self.width
        if self.cursor <= 0 or self.cursor >= self.width - 1:
            self.direction = -self.direction
        self.update(
            "\n".join(
                [
                    f"Mining... ({self.duration} seconds left)\n",
                    "💎  " * (5 - (self.duration - 1) % 5),
                    "",
                    "".join(
                        f"[{color}]{'█' * width}[/]"
                        for color, width in zip(COLORS, self.segment_widths)
                    ),
                    f"{' ' * (self.cursor)}[bold]⛏︎[/]",
                ]
            )
        )

    def tick_duration(self):
        if self.paused:
            return
        self.duration -= 1
        if self.duration < 0:
            self.remove()

    def toggle_paused(self):
        self.display = self.paused
        self.paused = not self.paused

    @property
    @lru_cache(maxsize=1)
    def score(self):
        self.remove()
        score = MiningScore.YELLOW
        if self.duration <= 1:
            return score
        acc_width = 0
        for i, width in enumerate(self.segment_widths):
            acc_width += width
            if acc_width >= self.cursor:
                color = COLORS[i]
                score = MiningScore[color.removesuffix("1").upper()]
                break
        return score
