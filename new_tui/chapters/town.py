from functools import partial

from myning.config import MINES
from myning.objects.menu_item import MenuItem
from new_tui.chapters import ExitArgs, PickArgs, healer, mine, store
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


def enter():
    implemented_chapters = {
        "Mine": mine.pick_mine,
        "Store": store.Store().enter,
        "Healer": healer.enter,
        "Exit": ExitArgs,
    }
    rows = columnate([chapter.tui_arr for chapter in CHAPTERS])
    handlers = [
        implemented_chapters.get(chapter.name, partial(unimplemented, chapter.name))
        for chapter in CHAPTERS
    ]

    return PickArgs(
        message="Where would you like to go next?",
        options=list(zip(rows, handlers)),
        border_title="Town",
    )


def unimplemented(location: str):
    return PickArgs(
        message=f"Sorry, {location} has not been implemented yet.",
        options=[("Bummer!", enter)],
    )
