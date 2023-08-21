from functools import partial

from myning.chapters import Option, PickArgs, main_menu, tutorial
from myning.objects.character import Character
from myning.objects.equipment import EQUIPMENT_TYPES
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utilities.file_manager import FileManager

player = Player()


def pick_member():
    member_arrs = [member.abbreviated_arr for member in player.army]

    if player.has_upgrade("armory_hints"):
        for i, member_arr in enumerate(member_arrs):
            member = player.army[i]
            for slot in EQUIPMENT_TYPES:
                equipped = member.equipment.get_slot_item(slot)
                if player.inventory.has_better_item(equipped, slot):
                    member_arr.append("✨")
                    break

    handlers = [partial(pick_slot, member) for member in player.army]
    options: list[Option] = list(zip(member_arrs, handlers))

    if player.has_upgrade("auto_equip"):
        options.append((["", "Auto-equip Best Items"], auto_equip))

    options.append(
        (["", "Go Back"], main_menu.enter if tutorial.is_complete() else tutorial.learn_mine)
    )
    return PickArgs(
        message="Upgrade Your Army Members' Gear",
        options=options,
        column_titles=player.abbreviated_column_titles,
    )


def pick_slot(c: Character):
    options = []
    for slot in EQUIPMENT_TYPES:
        equipped = c.equipment.get_slot_item(slot)
        has_better = player.inventory.has_better_item(equipped, slot)
        inventory_hints = player.has_upgrade("inventory_hints")
        options.append(
            (
                f"{slot.capitalize()} {'✨' if has_better and inventory_hints else ''}",
                partial(pick_equipment, c, slot),
            )
        )
    options.append(("Go Back", pick_member))
    return PickArgs(
        message="Select slot:\n",
        options=options,
        subtitle=c.equipment_table,
    )


def pick_equipment(c: Character, slot: ItemType):
    items = player.inventory.get_slot(slot)
    if not items:
        return PickArgs(
            message=f"You have no {slot}.",
            options=[("Bummer", pick_member)],
        )
    options: list[Option] = [(item.arr, partial(equip, c, slot, item)) for item in items]
    options.append((["", "Go Back"], partial(pick_slot, c)))
    return PickArgs(
        message=f"Choose {slot} to equip:\n",
        options=options,
        subtitle=c.equipment_table,
    )


def equip(c: Character, slot: ItemType, equipment: Item):
    if equipped := c.equipment.get_slot_item(slot):
        player.inventory.add_item(equipped)
    player.inventory.remove_item(equipment)
    c.equipment.change_item(slot, equipment)
    FileManager.save(c)
    return pick_slot(c)


def auto_equip():
    for character in player.army:
        for slot in EQUIPMENT_TYPES:
            equipped = character.equipment.get_slot_item(slot)
            if (
                equipped
                and player.inventory.has_better_item(equipped, slot)
                and (best := player.inventory.get_best_in_slot(slot))
            ):
                player.inventory.add_item(equipped)
                player.inventory.remove_item(best)
                character.equipment.change_item(slot, best)
    FileManager.multi_save(*player.army)
    return pick_member()
