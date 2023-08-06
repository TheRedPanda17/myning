from functools import partial

from myning.config import UPGRADES
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.objects.store import Store
from new_tui.chapters import Option, PickArgs, town
from new_tui.formatter import Formatter, columnate

MARKDOWN_RATIO = 1 / 2

player = Player()


def enter(store: Store | None = None):
    if not store:
        store = Store(player.level)
        store.generate()
    return PickArgs(
        message="What would you like to do?",
        options=[
            ("Buy", partial(pick_buy, store)),
            ("Sell", partial(pick_sell, store)),
            ("Go Back", town.enter),
        ],
    )


def pick_buy(store: Store):
    items = store.inventory.items
    rows = columnate([[*item.tui_arr, f"({Formatter.gold(item.value)})"] for item in items])
    options = [(row, partial(confirm_buy, store, item)) for row, item in zip(rows, items)]
    return PickArgs(
        message="What would you like to buy?",
        options=[
            *options,
            ("Go Back", partial(enter, store)),
        ],
    )


def confirm_buy(store: Store, item: Item):
    return PickArgs(
        message=f"Are you sure you want to buy {item.tui_str} for {Formatter.gold(item.value)}?",
        options=[
            ("Yes", partial(buy, store, item)),
            ("No", partial(pick_buy, store)),
        ],
    )


def buy(store: Store, item: Item):
    if player.gold < item.value:
        return PickArgs(
            message="Not enough gold!",
            options=[("Bummer!", partial(pick_buy, store))],
        )
    player.gold -= item.value
    player.inventory.add_item(item)
    store.inventory.remove_item(item)
    return enter(store)


def sell_price(item: Item):
    multipler = player.macguffin.mineral_boost if item.type == ItemType.MINERAL else MARKDOWN_RATIO
    return int(item.value * multipler) or 1


def pick_sell(store: Store):
    items = player.inventory.items
    rows = columnate([[*item.tui_arr, f"({Formatter.gold(sell_price(item))})"] for item in items])
    options: list[Option] = [
        (row, partial(confirm_sell, store, item)) for row, item in zip(rows, items)
    ]
    if player.has_upgrade("sell_minerals"):
        minerals = player.inventory._items[ItemType.MINERAL].copy()
        tax = UPGRADES["sell_minerals"].player_value / 100
        options.append(
            (
                "Sell Minerals",
                partial(confirm_mass_sell, store, "of your minerals", minerals, tax),
            )
        )

    if player.has_upgrade("sell_almost_everything"):
        all_but_top_3_items = []
        for type_items in player.inventory._items.values():
            sorted_type_items = sorted(type_items, key=lambda i: i.value)
            all_but_top_3_items.extend(sorted_type_items[:-3])
        tax = UPGRADES["sell_almost_everything"].player_value / 100
        options.append(
            (
                "Sell Almost Everything",
                partial(
                    confirm_mass_sell,
                    store,
                    "but your top 3 items in each category",
                    all_but_top_3_items,
                    tax,
                ),
            )
        )
    if player.has_upgrade("sell_everything"):
        all_items = player.inventory.items
        tax = UPGRADES["sell_everything"].player_value / 100
        options.append(
            (
                "Sell Everything",
                partial(confirm_mass_sell, store, "of your items", all_items, tax),
            )
        )
    return PickArgs(
        message="What would you like to sell?",
        options=[
            *options,
            ("Go Back", partial(enter, store)),
        ],
    )


def confirm_sell(store: Store, item: Item):
    return PickArgs(
        message=f"Are you sure you want to sell {item.tui_str} for {Formatter.gold(sell_price(item))}?",
        options=[
            ("Yes", partial(sell, store, item)),
            ("No", partial(enter, store)),
        ],
    )


def sell(store: Store, item: Item):
    player.gold += sell_price(item)
    player.inventory.remove_item(item)
    store.inventory.add_item(item)
    return enter(store)


def confirm_mass_sell(store: Store, description: str, items: list[Item], tax: float):
    if not items:
        return PickArgs(
            message="Nice try. You don't have any items to sell.",
            options=[("You caught me.", partial(pick_sell, store))],
        )
    total = int(sum(sell_price(item) for item in items) * (1 - tax))
    return PickArgs(
        message=f"Are you sure you want to sell all {description} for {Formatter.gold(total)}?",
        options=[
            ("Yes", partial(mass_sell, store, items, total)),
            ("No", partial(pick_sell, store)),
        ],
    )


def mass_sell(store: Store, items: list[Item], total: int):
    player.gold += total
    for item in items:
        player.inventory.remove_item(item)
        store.inventory.add_item(item)
    return enter(store)
