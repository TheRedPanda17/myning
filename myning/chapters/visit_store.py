from itertools import groupby
from typing import List

from blessed.terminal import Terminal

from myning.config import UPGRADES
from myning.objects.buying_option import BuyingOption
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utils.io import confirm, pick
from myning.utils.ui import columnate, get_gold_string

term = Terminal()

MARKDOWN_RATIO = 1 / 2


def buy(items: List[Item], player: Player, buying_options: BuyingOption = None) -> List[Item]:
    while True:
        options = []
        for item in items:
            s = [*item.str_arr, f"({get_gold_string(item.value)})"]
            if player.has_upgrade("advanced_store_hints") and is_best_item(item):
                s.append(" 🔥")
            elif player.has_upgrade("store_hints") and is_useful_item(item):
                s.append(" ✨")
            else:
                s.append("")
            options.append(s)

        options = [*columnate(options)]

        if buying_options:
            options.append(buying_options.options_string)

        option, index = pick(
            [*options, "Go Back"],
            f"What would you like to buy? ({get_gold_string(player.gold)})",
        )
        if option == "Go Back":
            return []

        items_to_buy = []  # start with an empty list to avoid UnboundLocalError

        if not buying_options:  # if there are no buying options, just list the items
            items_to_buy = [items[index]]

        if buying_options and not buying_options.filter:
            # if there are buying options, but no filter, just list the items with the additional option
            # example: buy all the seeds in the Garden Store
            items_to_buy = [*items] if option == buying_options.options_string else [items[index]]

        if buying_options and buying_options.filter:
            # if there are buying options and a filter, list the items that match the filter
            # example: buy all the Blademaster items in the Blacksmith Store
            filtered_gear = [item for item in items if buying_options.filter in item.name]
            items_to_buy = (
                [*filtered_gear] if option == buying_options.options_string else [items[index]]
            )

        price = sum([item.value for item in items_to_buy])
        name = items_to_buy[0].name
        if buying_options and option == buying_options.options_string:
            name = buying_options.name

        confirmation = f"Are you sure you want to buy {name} for {get_gold_string(price)}?"
        if player.pay(
            price,
            failure_msg="Not enough gold!",
            failure_option="Bummer!",
            confirmation_msg=confirmation,
        ):
            return items_to_buy
    return []


def sell(
    items: list[Item],
    has_sell_minerals: bool,
    has_sell_almost_everything: bool,
    has_sell_everything: bool,
    bonus_ratio: int = 1,
):
    item_to_sell, price = None, None

    while True:
        options = columnate(
            [
                [
                    *item.str_arr,
                    f"({get_gold_string(get_sell_price(item, bonus_ratio))})",
                ]
                for item in items
            ]
        )
        if has_sell_minerals:
            options.append("Sell Minerals")
        if has_sell_almost_everything:
            options.append("Sell Almost Everything")
        if has_sell_everything:
            options.append("Sell Everything")

        option, index = pick(
            [*options, "Go Back"],
            "What would you like to sell?",
        )
        if option == "Go Back":
            break
        elif option == "Sell Minerals":
            non_tax = 1 - (UPGRADES["sell_minerals"].player_value / 100)
            return mass_sell(items, ItemType.MINERAL, bonus_ratio * non_tax)
        elif option == "Sell Almost Everything":
            non_tax = 1 - (UPGRADES["sell_almost_everything"].player_value / 100)
            return sell_almost_everything(items, bonus_ratio * non_tax)
        elif option == "Sell Everything":
            non_tax = 1 - (UPGRADES["sell_everything"].player_value / 100)
            return mass_sell(items, bonus_ratio=bonus_ratio * non_tax)

        item_to_sell = items[index]
        price = get_sell_price(item_to_sell, bonus_ratio)
        if confirm(
            f"Are you sure you want to sell your {item_to_sell.name} for {get_gold_string(price)}?",
        ):
            break

    return [item_to_sell] if item_to_sell else None, price


def mass_sell(items: list[Item], item_type: ItemType | None = None, bonus_ratio: int = 1):
    is_selling_everything = item_type is None
    items_plural = f"{is_selling_everything and 'item' or item_type}s"

    if not is_selling_everything:
        items = [item for item in items if item.type == item_type]

    if not items:
        pick(["You caught me."], f"Nice try. You don't have any {items_plural} to sell.")
        return None, None

    price = int(sum(get_sell_price(item, bonus_ratio) for item in items))
    if not confirm(
        f"Are you sure you want to sell all of your {items_plural} for {get_gold_string(price)}?",
    ):
        return None, None

    return items, price


def sell_almost_everything(items: list[Item], bonus_ratio: int = 1):
    items = groupby(items, key=lambda i: i.type)
    items = [i for _, type_items in items for i in sorted(type_items, key=lambda ti: ti.value)[:-3]]

    price = int(sum(get_sell_price(item, bonus_ratio) for item in items)) or 1
    if not confirm(
        f"Are you sure you want to sell all but your top 3 items in each category for {get_gold_string(price)}?",
    ):
        return None, None

    return items, price


def get_sell_price(item: Item, bonus_ratio: int = 1):
    markdown = bonus_ratio if item.type == ItemType.MINERAL else MARKDOWN_RATIO
    price = int(item.value * markdown) or 1
    return price


def is_useful_item(item: Item):
    if item.type == ItemType.MINERAL or item.type == ItemType.PLANT:
        return False

    player = Player()

    for character in player.army:
        equipped = character.equipment.get_slot_item(item.type)
        if equipped is None or item.main_affect > equipped.main_affect:
            return True

    return False


def is_best_item(item: Item):
    if item.type == ItemType.MINERAL or item.type == ItemType.PLANT:
        return False

    player = Player()

    best = player.inventory.get_best_in_slot(item.type)
    for character in player.army:
        equipped = character.equipment.get_slot_item(item.type)
        if equipped is None:
            continue
        if best is None or equipped.main_affect > best.main_affect:
            best = equipped

    return best is None or item.main_affect > best.main_affect
