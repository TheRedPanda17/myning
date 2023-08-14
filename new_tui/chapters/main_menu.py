from functools import partial

from myning.config import MINES
from myning.objects.mine import Mine
from myning.objects.player import Player
from myning.utils.ui_consts import Icons
from new_tui.chapters import ExitArgs, Handler, PickArgs, armory, healer, mine, store, wizard_hut
from new_tui.formatter import Formatter

player = Player()


class MenuItem:
    def __init__(self, name: str, handler: Handler, prerequisite_mine: Mine | None = None):
        self.name = name
        self.icon: Icons = getattr(Icons, name.upper().replace(" ", "_"))
        self.handler = handler
        self.prerequisite_mine = prerequisite_mine

    @property
    def unlocked(self):
        return not self.prerequisite_mine or self.prerequisite_mine in player.mines_completed

    @property
    def play(self):
        if not self.prerequisite_mine or self.unlocked:
            # TODO remove next two lines
            if self.handler.__name__ == "unimplemented":
                return partial(unimplemented, self.name)
            return self.handler
        return partial(mine_required, self.prerequisite_mine.name)

    @property
    def arr(self):
        return [
            self.icon if self.unlocked else Icons.LOCKED,
            self.name if self.unlocked else Formatter.locked(self.name),
        ]


def enter():
    chapters = [
        MenuItem("Mine", mine.pick_mine),
        MenuItem("Store", store.enter),
        MenuItem("Armory", armory.pick_member),
        MenuItem("Healer", healer.enter),
        MenuItem("Wizard Hut", wizard_hut.enter, MINES["Hole in the ground"]),
        MenuItem("Barracks", unimplemented, MINES["Small pit"]),
        MenuItem("Blacksmith", unimplemented, MINES["Trench"]),
        MenuItem("Graveyard", unimplemented, MINES["Large pit"]),
        MenuItem("Garden", unimplemented, MINES["Cave"]),
        MenuItem("Research Facility", unimplemented, MINES["Cavern"]),
        MenuItem("Time Machine", unimplemented, MINES["Cave System"]),
        MenuItem("Journal", unimplemented),
        MenuItem("Settings", unimplemented),
        MenuItem("Exit", ExitArgs),
    ]
    return PickArgs(
        message="Where would you like to go next?",
        options=[(chapter.arr, chapter.play) for chapter in chapters],
        border_title="Main Menu",
    )


def mine_required(mine_name: str):
    return PickArgs(
        message=f"You must complete {mine_name} first",
        options=[("I'll get on it", enter)],
    )


def unimplemented(location: str):
    return PickArgs(
        message=f"Sorry, {location} has not been implemented yet.",
        options=[("Bummer!", enter)],
    )
