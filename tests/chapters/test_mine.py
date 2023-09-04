from unittest.mock import patch

from textual.pilot import Pilot
from textual.widgets import Static

from myning.config import MINES
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.tui.app import MyningApp
from myning.tui.chapter import ChapterWidget
from tests.utilities import get_option

trip = Trip()
player = Player()


def get_content(app: MyningApp):
    # pylint: disable=protected-access
    return "".join(
        str(w._renderable)
        for w in app.query("MineScreen ScrollableContainer Static")
        if isinstance(w, Static)
    )


@patch("myning.chapters.mine.mining_minigame.COLORS", ["yellow1"] * 7)
async def test_mining(app: MyningApp, pilot: Pilot, chapter: ChapterWidget):
    # patch action to always be mineral
    hole_in_the_ground = MINES["Hole in the ground"]
    hole_in_the_ground.odds = [{"action": "mineral", "chance": 1}]

    # pick mine
    await pilot.press("enter")
    assert chapter.border_title == "Mine"

    # pick duration
    await pilot.press("enter")
    assert chapter.question.message == "How long would you like to mine in 🪨 Hole in the ground?\n"

    # start mine
    await pilot.press("enter")
    assert trip.mine is hole_in_the_ground
    assert "Mining..." in get_content(app)
    assert not trip.items_found

    # enter to skip mining
    await pilot.press("enter")
    assert "New mineral added" in get_content(app)
    assert len(trip.minerals_mined) == 1
    mineral = trip.minerals_mined[0]
    assert mineral.name in get_content(app)

    # tick after getting mineral goes back to mining
    await pilot.pause(4)
    assert "Mining..." in get_content(app)

    # complete trip
    trip.seconds_left = 2
    await pilot.press("enter")
    assert not app.query("MineScreen")
    assert chapter.border_title == "Main Menu"
    assert "Your mining trip" in chapter.question.message
    await pilot.press("enter")
    assert "You have completed a mining trip" in chapter.question.message
    await pilot.press("enter")
    assert chapter.question.message == "Where would you like to go next?"


async def test_abandon(app: MyningApp, pilot: Pilot, chapter: ChapterWidget):
    # pick and start mine
    await pilot.press("enter", "enter", "enter")

    # ctrl+q to abandon
    await pilot.press("ctrl+q")
    assert "Are you sure you want to abandon your trip?" in get_content(app)

    # cancel abandon
    await pilot.press("enter")
    assert "Mining..." in get_content(app)

    # abandon again
    await pilot.press("ctrl+q", "ctrl+q")
    assert not trip.mine
    assert chapter.border_title == "Main Menu"


async def test_unlock_mine(app: MyningApp, pilot: Pilot, chapter: ChapterWidget):
    # try to unlock small pit
    await pilot.press("enter", "u", "enter")
    assert chapter.question.message == "You aren't a high enough level for this mine"

    player.level = 3
    await pilot.press("enter", "enter")
    assert chapter.question.message == "You don't have enough gold to unlock this mine"

    player.gold = 25
    await pilot.press("enter", "enter")
    assert "You have unlocked" in chapter.question.message

    await pilot.press("enter")
    assert "Small pit" in get_option(app, 1)


async def test_victory(app: MyningApp, pilot: Pilot, chapter: ChapterWidget):
    hole_in_the_ground = MINES["Hole in the ground"]
    hole_in_the_ground.odds = [{"action": "combat", "chance": 1}]

    # pick and start mine
    await pilot.press("enter", "enter", "enter")

    # increase player stats
    player.level = 30
    # wait for trip to be over
    trip.seconds_left = 10
    while app.query("MineScreen"):
        await pilot.pause(1)

    assert "Your mining trip" in chapter.question.message


async def test_defeat(app: MyningApp, pilot: Pilot, chapter: ChapterWidget):
    chasm = MINES["Chasm"]
    chasm.odds = [{"action": "combat", "chance": 1}]
    player.mines_available.append(chasm)

    # pick and start mine
    await pilot.press("enter", "enter", "enter")

    # wait for trip to be over
    trip.seconds_left = 10
    while app.query("MineScreen"):
        await pilot.pause(1)

    # chasm is impossible for a level one player
    assert "You lost the battle" in chapter.question.message
