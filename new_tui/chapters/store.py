from functools import partial


from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.objects.store import Store
from new_tui.chapters import PickArgs, town
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
    options = [(row, partial(confirm_sell, store, item)) for row, item in zip(rows, items)]
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
