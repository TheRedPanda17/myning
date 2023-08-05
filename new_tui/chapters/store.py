from functools import partial
from itertools import zip_longest

from rich.text import Text

from myning.objects.item import Item
from myning.objects.player import Player
from myning.objects.store import Store
from myning.utils.ui_consts import Icons
from new_tui.chapters import PickArgs, town

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
    rows = columnate(
        [[*item.tui_arr, f"([gold1]{item.value}g[/])"] for item in store.inventory.items]
    )
    options = [
        (
            row,
            partial(confirm_buy, store, item),
        )
        for row, item in zip(rows, store.inventory.items)
    ]
    return PickArgs(
        message="What would you like to buy?",
        options=[
            *options,
            ("Go Back", partial(enter, store)),
        ],
    )


def confirm_buy(store: Store, item: Item):
    return PickArgs(
        message=f"Are you sure you want to buy {item.icon} [{item.tui_color}]{item.name}[/] for [gold1]{item.value}g[/]?",
        options=[
            ("Yes", partial(buy, store, item)),
            ("No", partial(pick_buy, store)),
        ],
    )


def buy(store: Store, item: Item):
    print(f"bought {item.name}")
    return enter(store)


def pick_sell(store: Store):
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
        message=f"Are you sure you want to sell {item.icon} [{item.tui_color}]{item.name}[/] for [gold1]{item.value}g[/]?",
        options=[
            ("Yes", partial(sell, store, item)),
            ("No", partial(enter, store)),
        ],
    )


def sell(store: Store, item: Item):
    print(f"sold {item.name}")
    return enter(store)


def columnate(items: list[list[str]], *, sep=" ") -> list[Text]:
    widths = []
    for col in zip_longest(*items):
        max_width = 0
        for cell in col:
            width = 1 if isinstance(cell, Icons) else len(Text.from_markup(cell))
            if width > max_width:
                max_width = width
        widths.append(max_width)
    rows = []
    for row in items:
        texts = []
        for item, width in zip(row, widths):
            text = Text.from_markup(item)
            text.truncate(width + 1, pad=True)
            texts.append(text)
        rows.append(Text(sep).join(texts))
    return rows
