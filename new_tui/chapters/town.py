from functools import partial

from myning.config import MINES
from myning.objects.menu_item import MenuItem
from myning.utils.ui_consts import Icons
from new_tui.chapters import PickArgs, mine, store
from new_tui.formatter import columnate

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


def exit():
    return PickArgs(message="__exit__", options=[])


def enter():
    implemented_chapters = {
        "Mine": mine.enter,
        "Store": store.Store().enter,
        "Exit": exit,
    }
    rows = columnate([chapter.tui_arr for chapter in CHAPTERS])
    handlers = [
        implemented_chapters.get(chapter.name, partial(handle_unimplemented, chapter.name))
        for chapter in CHAPTERS
    ]

    return PickArgs(
        message="Where would you like to go next?",
        options=list(zip(rows, handlers)),
    )


def handle_unimplemented(location: str):
    return PickArgs(
        message=f"Sorry, {location} has not been implemented yet.",
        options=[("Bummer!", enter)],
    )
