from functools import partial

from textual import message

from myning.config import MINES
from myning.objects.menu_item import MenuItem
from myning.utils.ui_consts import Icons
from new_tui.chapters import PickArgs, store

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


def chapter_option(menu_item: MenuItem):
    icon = f"{menu_item.emoji} " if menu_item.unlocked else Icons.LOCKED
    name = menu_item.name if menu_item.unlocked else f"[grey53]{menu_item.name}[/]"
    return f"{icon} {name}"


def exit():
    return PickArgs(message="__exit__", options=[])


implemented_chapters = {
    "Store": store.enter,
    "Exit": exit,
}


def enter():
    return PickArgs(
        message="Where would you like to go next?",
        options=[
            (chapter_option(chapter), implemented_chapters[chapter.name])
            if implemented_chapters.get(chapter.name)
            else (str(chapter), partial(handle_unimplemented, chapter.name))
            for chapter in CHAPTERS
        ],
    )


def handle_unimplemented(location: str):
    return PickArgs(
        message=f"Sorry, {location} has not been implemented yet.",
        options=[("Bummer!", enter)],
    )
