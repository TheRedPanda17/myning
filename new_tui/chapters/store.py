from functools import partial

from myning.config import UPGRADES
from myning.objects.inventory import Inventory
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_equipment
from new_tui.chapters import Option, PickArgs, main_menu, tutorial
from new_tui.formatter import Formatter, columnate

MARKDOWN_RATIO = 1 / 2

player = Player()


def enter():
    return Store().enter()


class Store:
    def __init__(self):
        self.level = player.level
        self.inventory = Inventory()
        self.generate()

    def generate(self):
        item_count = max(self.level, 5)
        for _ in range(item_count):
            self.inventory.add_item(generate_equipment(self.level))

    def enter(self):
        return PickArgs(
            message="What would you like to do?",
            options=[
                ("Buy", self.pick_buy),
                ("Sell", self.pick_sell),
                ("Go Back", self.exit),
            ],
        )

    def exit(self):
        FileManager.multi_delete(*self.inventory.items)
        return (main_menu.enter if tutorial.is_complete() else tutorial.learn_armory)()

    def pick_buy(self):
        items = self.inventory.items
        item_arrs = []
        for item in items:
            item_arr = [*item.tui_arr, f"({Formatter.gold(item.value)})"]
            if player.has_upgrade("advanced_store_hints") and is_best_item(item):
                item_arr.append("🔥")
            elif player.has_upgrade("store_hints") and is_useful_item(item):
                item_arr.append("✨")
            item_arrs.append(item_arr)
        rows = columnate(item_arrs)
        options = [(row, partial(self.confirm_buy, item)) for row, item in zip(rows, items)]
        return PickArgs(
            message="What would you like to buy?",
            options=[
                *options,
                ("Go Back", self.enter),
            ],
        )

    def confirm_buy(self, item: Item):
        return PickArgs(
            message=f"Are you sure you want to buy {item.tui_str} for {Formatter.gold(item.value)}?",
            options=[
                ("Yes", partial(self.buy, item)),
                ("No", self.pick_buy),
            ],
        )

    def buy(self, item: Item):
        if player.gold < item.value:
            return PickArgs(
                message="Not enough gold!",
                options=[("Bummer!", self.pick_buy)],
            )
        player.gold -= item.value
        player.inventory.add_item(item)
        self.inventory.remove_item(item)
        FileManager.multi_save(player, item)
        return self.enter()

    def pick_sell(self):
        items = player.inventory.items
        rows = columnate(
            [[*item.tui_arr, f"({Formatter.gold(sell_price(item))})"] for item in items]
        )
        options: list[Option] = [
            (row, partial(self.confirm_sell, item)) for row, item in zip(rows, items)
        ]
        if player.has_upgrade("sell_minerals"):
            # pylint: disable=protected-access
            minerals = player.inventory._items[ItemType.MINERAL].copy()
            tax = UPGRADES["sell_minerals"].player_value / 100
            options.append(
                (
                    "Sell Minerals",
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
                (
                    "Sell Almost Everything",
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
                (
                    "Sell Everything",
                    partial(self.confirm_mass_sell, "of your items", all_items, tax),
                )
            )
        return PickArgs(
            message="What would you like to sell?",
            options=[
                *options,
                ("Go Back", self.enter),
            ],
        )

    def confirm_sell(self, item: Item):
        return PickArgs(
            message=f"Are you sure you want to sell {item.tui_str} for {Formatter.gold(sell_price(item))}?",
            options=[
                ("Yes", partial(self.sell, item)),
                ("No", self.pick_sell),
            ],
        )

    def sell(self, item: Item):
        player.gold += sell_price(item)
        player.inventory.remove_item(item)
        self.inventory.add_item(item)
        FileManager.save(player)
        return self.enter()

    def confirm_mass_sell(self, description: str, items: list[Item], tax: float):
        if not items:
            return PickArgs(
                message="Nice try. You don't have any items to sell.",
                options=[("You caught me.", self.pick_sell)],
            )
        total = int(sum(sell_price(item) for item in items) * (1 - tax))
        return PickArgs(
            message=f"Are you sure you want to sell all {description} for {Formatter.gold(total)}?",
            options=[
                ("Yes", partial(self.mass_sell, items, total)),
                ("No", self.pick_sell),
            ],
        )

    def mass_sell(self, items: list[Item], total: int):
        player.gold += total
        for item in items:
            player.inventory.remove_item(item)
            self.inventory.add_item(item)
        FileManager.save(player)
        return self.enter()


def sell_price(item: Item):
    multipler = player.macguffin.mineral_boost if item.type == ItemType.MINERAL else MARKDOWN_RATIO
    return int(item.value * multipler) or 1


def is_useful_item(item: Item):
    if item.type in (ItemType.MINERAL, ItemType.PLANT):
        return False

    for character in player.army:
        equipped = character.equipment.get_slot_item(item.type)
        if equipped is None or item.main_affect > equipped.main_affect:
            return True

    return False


def is_best_item(item: Item):
    if item.type in (ItemType.MINERAL, ItemType.PLANT):
        return False

    best = player.inventory.get_best_in_slot(item.type)
    for character in player.army:
        equipped = character.equipment.get_slot_item(item.type)
        if equipped is None:
            continue
        if best is None or equipped.main_affect > best.main_affect:
            best = equipped

    return best is None or item.main_affect > best.main_affect
