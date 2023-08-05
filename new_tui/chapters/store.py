import functools

from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.store import Store
from new_tui.chapters import Handler, town

player = Player()


def enter(store: Store | None = None) -> Handler:
    if not store:
        store = Store(player.level)
        store.generate()
    return "What would you like to do?", [
        ("Buy", functools.partial(buy, store)),
        ("Sell", functools.partial(sell, store)),
        ("Go Back", town.enter),
    ]


def buy(store: Store) -> Handler:
    options = []
    for item in store.inventory.items:
        options.append(
            (
                f"{item.tui_str} ([gold1]{item.value}g[/])",
                functools.partial(
                    confirm_buy,
                    store,
                    item,
                ),
            )
        )

    return "What would you like to buy?", [
        *options,
        ("Go Back", functools.partial(enter, store)),
    ]


def confirm_buy(store: Store, item: Item) -> Handler:
    return f"Are you sure you want to buy [blue]{item.name}[/] for [gold1]{item.value}g[/]?", [
        ("Yes", functools.partial(complete_buy, store, item)),
        ("No", functools.partial(buy, store)),
    ]


def complete_buy(store: Store, item: Item) -> Handler:
    return f"Succesfully bought {item.name}", [("Sweet", functools.partial(enter, store))]


def sell(store: Store) -> Handler:
    return "What would you like to sell?", [
        *(
            (item.tui_str, functools.partial(confirm_sell, store, item))
            for item in player.inventory.items
        ),
        ("Go Back", functools.partial(enter, store)),
    ]


def confirm_sell(store: Store, item: Item) -> Handler:
    return f"Are you sure you want to sell [blue]{item.name}[/] for [gold1]{item.value}g[/]?", [
        ("Yes", functools.partial(complete_sell, store, item)),
        ("No", functools.partial(sell, store)),
    ]


def complete_sell(store: Store, item: Item) -> Handler:
    return f"Succesfully sold {item.name}", [("Sweet", functools.partial(enter, store))]
