from functools import partial

from myning.chapters import (
    ExitArgs,
    Handler,
    Option,
    PickArgs,
    armory,
    barracks,
    blacksmith,
    garden,
    graveyard,
    healer,
    journal,
    mine,
    research_facility,
    settings,
    stats,
    store,
    time_machine,
    wizard_hut,
)
from myning.config import MINES
from myning.objects.mine import Mine
from myning.objects.player import Player
from myning.utilities.formatter import Formatter
from myning.utilities.ui import Icons

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
            return self.handler
        return partial(mine_required, self.prerequisite_mine.name)

    @property
    def arr(self):
        return (
            [self.icon, self.name] if self.unlocked else [Icons.LOCKED, Formatter.locked(self.name)]
        )


def enter():
    chapters = [
        MenuItem("Mine", mine.pick_mine),
        MenuItem("Store", store.enter),
        MenuItem("Armory", armory.pick_member),
        MenuItem("Healer", healer.enter),
        MenuItem("Wizard Hut", wizard_hut.enter, MINES["Hole in the ground"]),
        MenuItem("Barracks", barracks.enter, MINES["Small pit"]),
        MenuItem("Blacksmith", blacksmith.enter, MINES["Trench"]),
        MenuItem("Graveyard", graveyard.enter, MINES["Large pit"]),
        MenuItem("Garden", garden.enter, MINES["Cave"]),
        MenuItem("Research Facility", research_facility.enter, MINES["Cavern"]),
        MenuItem("Time Machine", time_machine.enter, MINES["Cave System"]),
        MenuItem("Journal", journal.enter),
        MenuItem("Stats", stats.enter),
        MenuItem("Settings", settings.enter),
        MenuItem("Exit", ExitArgs),
    ]
    options: list[Option] = [(chapter.arr, chapter.play) for chapter in chapters]
    return PickArgs(
        message="Where would you like to go next?",
        options=options,
        border_title="Main Menu",
    )


def mine_required(mine_name: str):
    return PickArgs(
        message=f"You must complete {mine_name} first",
        options=[("I'll get on it", enter)],
    )
