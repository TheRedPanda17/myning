import re

from rich.text import Text
from textual.pilot import Pilot

from myning.tui.app import MyningApp
from myning.tui.chapter import ChapterWidget
from myning.tui.currency import CurrencyWidget
from myning.tui.inventory import InventoryWidget
from tests.utilities import get_option


def get_gold(app: MyningApp):
    currency = app.query_one("CurrencyWidget", CurrencyWidget).render()
    # pylint: disable=protected-access
    gold_text = Text.from_markup(str(currency.columns[2]._cells[0])).plain
    return int(gold_text.replace(",", "").rstrip("g"))


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
