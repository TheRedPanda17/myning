import random
from typing import List

from myning.chapters import visit_store
from myning.config import STRINGS, UPGRADES
from myning.objects.blacksmith_item import BlacksmithItem
from myning.objects.buying_option import BuyingOption, StoreType
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.objects.settings import Settings, SortOrder
from myning.objects.stats import IntegerStatKeys, Stats
from myning.objects.store import Store
from myning.utils import utils
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.ui import get_gold_string

BLACKSMITH_ITEMS = [
    BlacksmithItem("Soldier", 15, 50),
    BlacksmithItem("Commander", 20, 250),
    BlacksmithItem("General", 30, 500),
    BlacksmithItem("Samurai", 40, 1000),
    BlacksmithItem("Ninja", 50, 2000),
    BlacksmithItem("Jedi", 75, 5000),
    BlacksmithItem("Blademaster", 100, 10000),
    BlacksmithItem("Spartan", 150, 40000),
]


def play():
    player, stats, settings = Player(), Stats(), Settings()

    while True:
        smith_level = player.blacksmith_level
        store = Store()
        available_classes = BLACKSMITH_ITEMS[:smith_level]
        items = generate_items(available_classes)
        for item in items:
            store.add_item(item)

        _, index = pick(
            [
                "Buy",
                f"Upgrade Smith ({get_gold_string(smith_cost(smith_level))})",
                "Go Back",
            ],
            f"What would you like to do? ({get_gold_string(player.gold)})",
        )
        if index == 0:  # Buy
            buying_options = None
            if player.has_upgrade("buy_full_set"):
                set = UPGRADES["buy_full_set"].player_value
                buying_options = BuyingOption(
                    name=f"all {set} items",
                    store_type=StoreType.BLACKSMITH,
                    options_string="Buy Full Set",
                    filter=f"{set}'s",
                )

            items = store.items
            if (
                player.has_upgrade("sort_by_value")
                and "blacksmith" in UPGRADES["sort_by_value"].player_value
                and settings.sort_order == SortOrder.VALUE
            ):
                items = store.items_by_value

            bought_items = visit_store.buy(items, player, buying_options)
            for item in bought_items:
                store.remove_item(item)
                player.inventory.add_item(item)

                if item.type == ItemType.WEAPON:
                    stats.increment_int_stat(IntegerStatKeys.WEAPONS_PURCHASED)
                else:
                    stats.increment_int_stat(IntegerStatKeys.ARMOR_PURCHASED)

                FileManager.multi_save(item, stats)
        elif index == 1:  # Upgrade
            if player.blacksmith_level >= len(BLACKSMITH_ITEMS):
                pick(
                    ["Go Back"],
                    f"Blacksmith cannot build anything more beneficial than {BLACKSMITH_ITEMS[-1].name}.",
                )
                continue

            new_level = upgrade_blacksmith(player)
            if new_level is not None:
                player.blacksmith_level = new_level
                FileManager.save(player)
        elif index == 2:  # Go Back
            FileManager.multi_delete(*store.items)
            break


def upgrade_blacksmith(player: Player) -> int:
    cost = smith_cost(player.blacksmith_level)
    _, index = pick(
        [f"Upgrade to level {player.blacksmith_level + 1}", "Maybe Later"],
        f"Are you sure you want to upgrade your blacksmith for {cost}g?",
    )
    if index != 0:
        return None
    if player.pay(
        cost,
        failure_msg="You don't have enough gold to upgrade your blacksmith.",
        failure_option="Shucks",
    ):
        return player.blacksmith_level + 1
    return None


def generate_items(classes: List["BlacksmithItem"]):
    items = []
    for cls in classes:
        for type in ItemType:
            if type == ItemType.MINERAL or type == ItemType.PLANT:
                continue
            if type == ItemType.WEAPON:
                value = cls.value
            else:
                value = int(cls.value * 0.4)
            type_name = random.choice(STRINGS[type.lower()])
            name = f"{cls.name}'s {type_name}"
            description = f"A {type.name}'s  {type_name}."
            items.append(Item(name, description, type, value, cls.main_affect))

    return items


def smith_cost(level):
    return utils.fibonacci(level + 4) * 100
