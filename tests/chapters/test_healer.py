from textual.pilot import Pilot

from myning.objects.player import Player
from myning.tui.app import MyningApp
from myning.tui.chapter import ChapterWidget

player = Player()


async def test_healer(app: MyningApp, pilot: Pilot, chapter: ChapterWidget):
    player.health -= 5
    await pilot.press("4")
    await pilot.press("enter")
    assert chapter.border_title == "Healer"
    assert chapter.question.message == "Start Recovery?"

    await pilot.press("enter")
    assert app.query("HealScreen")

    await pilot.press("enter")
    assert player.health == player.max_health
    assert chapter.question.message == "Everyone is healthy."
