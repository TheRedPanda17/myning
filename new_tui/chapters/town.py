import functools

from myning.config import MINES
from myning.objects.menu_item import MenuItem
from new_tui.chapters import Handler, store

CHAPTERS = [
    MenuItem("Mine"),
    MenuItem("Store"),
    MenuItem("Armory"),
    MenuItem("Healer"),
    MenuItem("Wizard Hut", prerequisites=[MINES["Hole in the ground"]]),
    MenuItem("Barracks", prerequisites=[MINES["Small pit"]]),
    MenuItem("Blacksmith", prerequisites=[MINES["Trench"]]),
    MenuItem("Graveyard", prerequisites=[MINES["Large pit"]]),
    MenuItem("Garden", prerequisites=[MINES["Cave"]]),
    MenuItem("Research Facility", prerequisites=[MINES["Cavern"]]),
    MenuItem("Time Machine", prerequisites=[MINES["Cave System"]]),
    MenuItem("Journal"),
    MenuItem("Settings"),
    MenuItem("Exit"),
]


# def str_arr(self):
#     icon = f"{self.emoji} " if self.unlocked else Icons.LOCKED
#     name = self.name if self.unlocked else term.snow4(self.name)
#     return [icon, name]


def handle_unimplemented(location: str) -> Handler:
    return f"Sorry, {location} has not been implemented yet.", [("Bummer!", enter)]


def enter() -> Handler:
    return (
        "Where would you like to go next?",
        [
            (str(chapter), store.enter)
            if chapter.name == "Store"
            else (str(chapter), functools.partial(handle_unimplemented, chapter.name))
            for chapter in CHAPTERS
        ],
    )
