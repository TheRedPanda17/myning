from textual.pilot import Pilot

from myning.config import UPGRADES
from myning.objects.inventory import Inventory
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.tui.chapter import ChapterWidget

player = Player()
inventory = Inventory()


async def test_armory(pilot: Pilot, chapter: ChapterWidget):
    player.upgrades.append(UPGRADES["armory_hints"])
    player.upgrades.append(UPGRADES["auto_equip"])

    # no weapon
    await pilot.press("a")
    assert chapter.border_title == "Armory"
    assert chapter.question.message == "Upgrade Your Army Members' Gear"

    await pilot.press("enter")
    assert chapter.question.message == "Select slot:\n"

    await pilot.press("enter")
    assert chapter.question.message == "You have no weapon."

    # equip weapon
    inventory.add_item(Item("1", "1", ItemType.WEAPON, 1, 1))
    await pilot.press("enter")
    await pilot.press("enter")
    assert chapter.question.message == "Choose weapon to equip:\n"

    await pilot.press("enter")
    assert not inventory.items
    assert player.equipment.get_slot_item(ItemType.WEAPON)

    # auto equip
    inventory.add_item(Item("10", "10", ItemType.WEAPON, 10, 10))
    await pilot.press("q")
    await pilot.press("up")
    await pilot.press("up")
    await pilot.press("enter")
    equipped = player.equipment.get_slot_item(ItemType.WEAPON)
    assert equipped and equipped.main_affect == 10
    assert inventory.items[0].main_affect == 1
