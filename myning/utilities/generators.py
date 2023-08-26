import math
import random

from myning.config import SPECIES, STRINGS
from myning.objects.army import Army
from myning.objects.character import Character, CharacterSpecies
from myning.objects.equipment import EQUIPMENT_TYPES
from myning.objects.item import Item, ItemType
from myning.objects.plant import PLANT_TYPES, Plant
from myning.utilities import string_generation
from myning.utilities.rand import (
    get_random_array_item,
    get_random_array_item_and_index,
    get_random_int,
)


def generate_character(
    level_range, species=None, is_enemy=False, max_items=0, max_item_level=0, item_scale=1
):
    if species is None:
        if is_enemy:
            species = SPECIES[CharacterSpecies.ALIEN.value]
        else:
            species = SPECIES[get_random_array_item(Character.companion_species).value]

    name = string_generation.generate_name(species.name)
    description = string_generation.generate_description(species.name)

    level = get_random_int(*level_range)
    character = Character(name, description, level, is_enemy, species)

    if max_items:
        item_level = max_item_level if max_item_level else level
        weapon = generate_equipment(item_level, type=ItemType.WEAPON, scale=item_scale)
        character.equipment.equip(weapon.type, weapon)

        for _ in range(get_random_int(1, max_items)):
            type = get_random_array_item(
                [
                    ItemType.HELMET,
                    ItemType.SHIRT,
                    ItemType.PANTS,
                    ItemType.SHOES,
                ]
            )
            armor = generate_equipment(level, type, scale=item_scale)
            character.equipment.equip(armor.type, armor)

    return character


def generate_equipment(level, type: ItemType | None = None, scale=1):
    type = type or get_random_array_item(EQUIPMENT_TYPES)
    modifier, weight = get_random_array_item_and_index(STRINGS["modifiers"], maximum=level)
    if weight == 0:
        weight = 1
    base_name = get_random_array_item(STRINGS[type.value])
    equipment = Item(name=f"{modifier} {base_name}", description="", type=type)

    affect_type = "damage" if type == ItemType.WEAPON else "armor"

    weight = math.floor(weight * scale)
    equipment.add_affect(affect_type, weight)
    equipment.value = weight

    # Add other random affects

    return equipment


def generate_mineral(max, mineral=None):
    modifier, weight = get_random_array_item_and_index(STRINGS["sizes"], maximum=max)
    if weight == 0:
        weight = 1
    base_name = mineral if mineral else get_random_array_item(STRINGS["minerals"])
    mineral = Item(name=f"{modifier} {base_name}", description="", type=ItemType.MINERAL)

    mineral.value = weight

    # Add other random affects

    return mineral


def generate_mineral_exact(level, mineral=None):
    modifier = STRINGS["sizes"][level]
    base_name = mineral if mineral else get_random_array_item(STRINGS["minerals"])
    mineral = Item(name=f"{modifier} {base_name}", description="", type=ItemType.MINERAL)

    mineral.value = level

    # Add other random affects

    return mineral


def generate_enemy_army(
    level_range, size_range, max_enemy_items, max_enemy_item_level, enemy_item_scale
):
    size = random.randint(*size_range)
    return Army(
        generate_character(
            level_range,
            is_enemy=True,
            max_items=max_enemy_items,
            max_item_level=max_enemy_item_level,
            item_scale=enemy_item_scale,
        )
        for _ in range(size)
    )


def generate_reward(max_item_level, entities_killed):
    items = [generate_equipment(max_item_level)]

    for _ in range(0, random.randint(0, entities_killed)):
        items.append(generate_mineral(max_item_level))

    return items


def generate_plant(garden_level: int):
    type = get_random_array_item(PLANT_TYPES)
    level = get_random_int(1, garden_level + 1)
    value = 10 * level
    adjective = STRINGS["sizes"][level]
    name = f"{adjective} {type.value} seed"
    description = f"This is a {name}"

    return Plant(
        name,
        description,
        value=value,
        plant_type=type,
    )
