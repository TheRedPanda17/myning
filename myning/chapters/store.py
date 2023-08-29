from functools import partial

from rich.text import Text

from myning.chapters import Option, PickArgs, main_menu, tutorial
from myning.chapters.base_store import BaseStore
from myning.config import MARKDOWN_RATIO, UPGRADES
from myning.objects.item import Item, ItemType
from myning.objects.macguffin import Macguffin
from myning.objects.plant import Plant
from myning.objects.player import Player
from myning.objects.stats import IntegerStatKeys, Stats
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.generators import generate_equipment
from myning.utilities.pick import confirm

player = Player()
macguffin = Macguffin()
stats = Stats()


def enter():
    return Store().enter()


class Store(BaseStore):
    def __init__(self):
        self.level = player.level
        super().__init__()

    def generate(self):
        amount = max(self.level, 5)
        self.add_items(*(generate_equipment(self.level) for _ in range(amount)))

    def enter(self):
        return PickArgs(
            message="What would you like to do?",
            options=[
                Option("Buy", self.pick_buy),
                Option("Sell", self.pick_sell),
                Option("Go Back", self.exit),
            ],
        )

    def exit(self):
        super().exit()
        return (main_menu.enter if tutorial.is_complete() else tutorial.learn_armory)()

    def pick_sell(self):
        options = [
            Option(
                [
                    *item.arr,
                    Text.from_markup(f"({Formatter.gold(sell_price(item))})", justify="right"),
                ],
                partial(self.sell, item),
                enable_hotkeys=False,
            )
            for item in player.inventory.items
        ]
        if player.has_upgrade("sell_minerals"):
            # pylint: disable=protected-access
            minerals = player.inventory._items[ItemType.MINERAL].copy()
            tax = UPGRADES["sell_minerals"].player_value / 100
            options.append(
                Option(
                    ["", "Sell Minerals"],
                    partial(self.confirm_mass_sell, "of your minerals", minerals, tax),
                )
            )

        if player.has_upgrade("sell_almost_everything"):
            all_but_top_3_items = []
            # pylint: disable=protected-access
            for type_items in player.inventory._items.values():
                sorted_type_items = sorted(type_items, key=lambda i: i.value)
                all_but_top_3_items.extend(sorted_type_items[:-3])
            tax = UPGRADES["sell_almost_everything"].player_value / 100
            options.append(
                Option(
                    ["", "Sell Almost Everything"],
                    partial(
                        self.confirm_mass_sell,
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
                Option(
                    ["", "Sell Everything"],
                    partial(self.confirm_mass_sell, "of your items", all_items, tax),
                )
            )
        return PickArgs(
            message="What would you like to sell?",
            options=[
                *options,
                Option(["", "Go Back"], self.enter),
            ],
        )

    @confirm(
        lambda self, item: f"Are you sure you want to sell {item} for "
        f"{Formatter.gold(sell_price(item))}?",
        pick_sell,
    )
    def sell(self, item: Item):
        price = sell_price(item)
        player.gold += price
        player.inventory.remove_item(item)
        self.add_item(item)
        stats.increment_int_stat(IntegerStatKeys.GOLD_EARNED, price)
        FileManager.multi_save(player, stats)
        return self.enter()

    def confirm_mass_sell(self, description: str, items: list[Item], tax: float):
        if not items:
            return PickArgs(
                message="Nice try. You don't have any items to sell.",
                options=[Option("You caught me.", self.pick_sell)],
            )
        total = int(sum(sell_price(item) for item in items) * (1 - tax))
        return PickArgs(
            message=f"Are you sure you want to sell all {description} for {Formatter.gold(total)}?",
            options=[
                Option("Yes", partial(self.mass_sell, items, total)),
                Option("No", self.pick_sell),
            ],
        )

    def mass_sell(self, items: list[Item], total: int):
        player.gold += total
        player.inventory.remove_items(*items)
        self.add_items(*items)
        stats.increment_int_stat(IntegerStatKeys.GOLD_EARNED, total)
        FileManager.multi_save(player, stats)
        return self.enter()


def sell_price(item: Item):
    if item.type == ItemType.MINERAL:
        multiplier = macguffin.mineral_boost
    elif isinstance(item, Plant) and not item.is_seed:
        # TODO if the item is a plant and it's expired, is the value supposed to be affected?
        multiplier = macguffin.plant_boost
    else:
        multiplier = MARKDOWN_RATIO
    return int(item.value * multiplier) or 1
