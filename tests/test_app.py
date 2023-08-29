# TODO move tests into their own files. This is just mvp for testing the tui

import re

from rich.text import Text
from textual.pilot import Pilot

from myning.objects.player import Player
from myning.tui.app import MyningApp
from myning.tui.chapter import ChapterWidget
from myning.tui.chapter.option_table import OptionTable
from myning.tui.currency import CurrencyWidget
from myning.tui.inventory import InventoryWidget

player = Player()


def get_option(app: MyningApp, index: int):
    option_table = app.query_one("OptionTable", OptionTable)
    arr = []
    for x in option_table.get_row_at(index):
        if not x:
            continue
        if isinstance(x, Text):
            arr.append(x.plain)
        else:
            arr.append(x)
    return " ".join(arr)


def get_gold(app: MyningApp):
    currency = app.query_one("CurrencyWidget", CurrencyWidget).render()
    # pylint: disable=protected-access
    gold_text = Text.from_markup(str(currency.columns[2]._cells[0])).plain
    return int(gold_text.replace(",", "").rstrip("g"))


def test_main_menu(app: MyningApp):
    chapter = app.query_one("ChapterWidget", ChapterWidget)
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


async def test_mine(app: MyningApp, pilot: Pilot):
    chapter = app.query_one("ChapterWidget", ChapterWidget)
    await pilot.press("enter")
    assert chapter.border_title == "Mine"
    await pilot.press("enter")
    assert chapter.question.message == "How long would you like to mine in 🪨 Hole in the ground?\n"
    await pilot.press("enter")
    assert app.query("MineScreen")


async def test_store(app: MyningApp, pilot: Pilot):
    chapter = app.query_one("ChapterWidget", ChapterWidget)
    inventory = app.query_one("InventoryWidget", InventoryWidget)
    starting_gold = get_gold(app)
    await pilot.press("down")
    await pilot.press("enter")
    assert chapter.border_title == "Store"

    assert inventory.row_count == 0
    assert starting_gold == 1

    await pilot.press("enter")
    first_item = get_option(app, 1)
    match = re.search(r"(\d+)g", first_item)
    assert match
    price = int(match[1])
    assert price == 1  # player is level 1 so item value must be 1

    await pilot.press("enter")
    assert "Are you sure" in str(chapter.question.message)

    await pilot.press("enter")
    assert inventory.row_count == 1
    assert get_gold(app) == 0


async def test_healer(app: MyningApp, pilot: Pilot):
    player.health -= 5
    chapter = app.query_one("ChapterWidget", ChapterWidget)
    await pilot.press("4")
    await pilot.press("enter")
    assert chapter.border_title == "Healer"
    assert chapter.question.message == "Start Recovery?"

    await pilot.press("enter")
    assert app.query("HealScreen")

    await pilot.press("enter")
    assert player.health == player.max_health
    assert chapter.question.message == "Everyone is healthy."
