from functools import partial

from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.store import Store
from new_tui.chapters import PickArgs, town

player = Player()


def enter(store: Store | None = None):
    if not store:
        store = Store(player.level)
        store.generate()
    return PickArgs(
        message="What would you like to do?",
        options=[
            ("Buy", partial(buy, store)),
            ("Sell", partial(sell, store)),
            ("Go Back", town.enter),
        ],
    )


def buy(store: Store):
    options = []
    for item in store.inventory.items:
        options.append(
            (
                f"{item.tui_str} ([gold1]{item.value}g[/])",
                partial(
                    confirm_buy,
                    store,
                    item,
                ),
            )
        )

    return PickArgs(
        message="What would you like to buy?",
        options=[
            *options,
            ("Go Back", partial(enter, store)),
        ],
    )


def confirm_buy(store: Store, item: Item):
    return f"Are you sure you want to buy [blue]{item.name}[/] for [gold1]{item.value}g[/]?", [
        ("Yes", partial(complete_buy, store, item)),
        ("No", partial(buy, store)),
    ]


def complete_buy(store: Store, item: Item):
    return f"Succesfully bought {item.name}", [("Sweet", partial(enter, store))]


def sell(store: Store):
    return PickArgs(
        message="What would you like to sell?",
        options=[
            *(
                (item.tui_str, partial(confirm_sell, store, item))
                for item in player.inventory.items
            ),
            ("Go Back", partial(enter, store)),
        ],
    )


def confirm_sell(store: Store, item: Item):
    return PickArgs(
        message=f"Are you sure you want to sell [blue]{item.name}[/] for [gold1]{item.value}g[/]?",
        options=[
            ("Yes", partial(complete_sell, store, item)),
            ("No", partial(sell, store)),
        ],
    )


def complete_sell(store: Store, item: Item):
    return PickArgs(
        message=f"Succesfully sold {item.name}",
        options=[("Sweet", partial(enter, store))],
    )
