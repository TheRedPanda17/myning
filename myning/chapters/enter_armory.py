from blessed.terminal import Terminal

from myning.objects.character import Character
from myning.objects.equipment import EQUIPMENT_TYPES
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.io import pick

term = Terminal()


def play():
    player = Player()
    army = player.army
    # Sort by name, putting the player's character first
    army.sort(key=lambda character: -100 if character.name == player.name else -character.level)

    while True:
        options = army.abbreviated
        if player.has_upgrade("armory_hints"):
            for i, option in enumerate(options):
                if "✨" in option:
                    break
                member = army[i]
                for slot in EQUIPMENT_TYPES:
                    equipped = member.equipment.get_slot_item(slot)
                    has_better = player.inventory.has_better_item(equipped, slot)
                    if has_better:
                        options[i] += " ✨"
                        break

        if player.has_upgrade("auto_equip"):
            options.append("Auto-equip Best Items")

        option, index = pick([*options, "Go Back"], "Upgrade Your Army Members' Gear")
        if option == "Go Back":
            return

        if option == "Auto-equip Best Items":
            auto_equip()
            continue

        update_inventory(army[index])
    FileManager.save(player)


def update_inventory(character: Character):
    player = Player()
    cont = True
    while cont:
        slots = []
        for slot in EQUIPMENT_TYPES:
            equipped = character.equipment.get_slot_item(slot)
            has_better = player.inventory.has_better_item(equipped, slot)
            inventory_hints = player.has_upgrade("inventory_hints")
            slots.append(f"{slot.capitalize()} {'✨' if has_better and inventory_hints else ''}")

        slots.append("Go Back")
        option, index = pick(
            slots,
            "Select slot:",
            dashboard=lambda: f"{' '.join([term.bold(character.name), character.damage_str, character.armor_str])}\n\n{character.equipment}",
        )
        if option == "Go Back":
            return

        slot = EQUIPMENT_TYPES[index]

        items = player.inventory.get_slot(slot)
        if not items:
            _, _ = pick(["Bummer"], f"You have no {slot}.")
            continue

        item_strs = [str(item) for item in items]

        option, index = pick(
            item_strs + ["Go Back"],
            f"Choose {slot} to equip",
            dashboard=lambda: f"{' '.join([term.bold(character.name), character.damage_str, character.armor_str])}\n\n{character.equipment}",
        )
        if option == "Go Back":
            continue

        to_equip = items[index]
        equipped = character.equipment.get_slot_item(slot)

        if equipped:
            player.inventory.add_item(equipped)
        player.inventory.remove_item(to_equip)

        character.equipment.change_item(slot, to_equip)


def auto_equip():
    player = Player()

    for character in player.army:
        for slot in EQUIPMENT_TYPES:
            equipped = character.equipment.get_slot_item(slot)
            has_better = player.inventory.has_better_item(equipped, slot)
            if has_better:
                best = player.inventory.get_best_in_slot(slot)
                if equipped:
                    player.inventory.add_item(equipped)
                player.inventory.remove_item(best)
                character.equipment.change_item(slot, best)
