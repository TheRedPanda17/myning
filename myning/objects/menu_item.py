from typing import List

from blessed import Terminal

from myning import chapters
from myning.objects.mine import Mine
from myning.objects.player import Player
from myning.utils.ui_consts import Icons

term = Terminal()


class MenuItem:
    def __init__(
        self,
        name: str,
        prerequisites: List[Mine] = [],
    ):
        self.name = name
        self.action = getattr(chapters, f"enter_{self.lower_name()}").play
        self.emoji = getattr(Icons, self.upper_name())
        self.prerequisites = prerequisites

    @property
    def __str__(self):
        return f""

    @property
    def unlocked(self):
        return set(self.prerequisites).issubset(set(Player().mines_completed))

    def str_arr(self):
        icon = f"{self.emoji} " if self.unlocked else Icons.LOCKED
        name = self.name if self.unlocked else term.snow4(self.name)
        return [icon, name]

    @property
    def required_mines_str(self):
        return " and ".join([mine.name for mine in self.prerequisites])

    def lower_name(self):
        return self.name.lower().replace(" ", "_")

    def upper_name(self):
        return self.name.upper().replace(" ", "_")

    def __call__(self):
        return self.action()

    def __str__(self) -> str:
        return " ".join(self.str_arr())
