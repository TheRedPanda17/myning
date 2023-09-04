from textual.pilot import Pilot

from myning.tui.app import MyningApp
from myning.tui.chapter import ChapterWidget
from tests.utilities import get_option


def test_main_menu(app: MyningApp, chapter: ChapterWidget):
    assert chapter.border_title == "Main Menu"
    assert chapter.question.message == "Where would you like to go next?"
    assert chapter.option_table.row_count == 16
    expected_options = [
        "Mine",
        "Store",
        "Armory",
        "Healer",
        "Wizard Hut",
        "Barracks",
        "Blacksmith",
        "Graveyard",
        "Garden",
        "Research Facility",
        "Time Machine",
        "Telescope",
        "Journal",
        "Stats",
        "Settings",
        "Exit",
    ]
    for i, expected_option in enumerate(expected_options):
        assert expected_option in get_option(app, i)


async def test_prerequisite(pilot: Pilot, chapter: ChapterWidget):
    # Time Machine requires completing Cave System
    await pilot.press("t")
    assert chapter.question.message == "You must complete Cave System first"
