from abc import ABC, abstractmethod
from functools import partial

from rich.text import Text

from myning.chapters import PickArgs, main_menu
from myning.config import UPGRADES
from myning.objects.buying_option import BuyingOption
from myning.objects.equipment import EQUIPMENT_TYPES
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.objects.settings import Settings, SortOrder
from myning.objects.stats import IntegerStatKeys, Stats
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter

player = Player()
stats = Stats()
settings = Settings()


class BaseStore(ABC):
    buying_option: BuyingOption | None = None

    def __init__(self):
        self._items: list[Item] = []
        self.generate()

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def enter(self) -> PickArgs:
        pass

    def add_item(self, item: Item):
        self._items.append(item)

    def add_items(self, *items: Item):
        for item in items:
            self.add_item(item)

    def remove_item(self, item: Item):
        if item in self._items:
            self._items.remove(item)

    def remove_items(self, *items: Item):
        for item in items:
            if item in self._items:
                self._items.remove(item)

    @property
    def items(self):
        store_name = self.__class__.__name__.lower()
        return sorted(
            self._items,
            key=lambda i: i.value
            if (
                player.has_upgrade("sort_by_value")
                and store_name in UPGRADES["sort_by_value"].player_value
                and settings.sort_order == SortOrder.VALUE
            )
            else i.type,
        )

    @property
    def empty(self):
        return not self._items

    def exit(self):
        FileManager.multi_delete(*self._items)
        return main_menu.enter()

    def pick_buy(self):
        if self.empty:
            self.generate()
        options = [
            (
                [
                    *item.tui_arr,
                    Text.from_markup(f"({Formatter.gold(item.value)})", justify="right"),
                    self.hint_symbol(item),
                ],
                partial(self.confirm_buy, item),
            )
            for item in self.items
        ]
        if self.buying_option:
            items = [item for item in self.items if self.buying_option.filter(item)]
            cost = sum(item.value for item in items)
            options.append(
                (
                    [
                        "",
                        f"Buy {self.buying_option.name}",
                        "",
                        Text.from_markup(f"({Formatter.gold(cost)})", justify="right"),
                    ],
                    partial(self.confirm_multi_buy, items),
                )
            )
        return PickArgs(
            message="What would you like to buy?",
            options=[
                *options,
                (["", "Go Back"], self.enter),
            ],
        )

    def confirm_buy(self, item: Item):
        if player.gold < item.value:
            return PickArgs(
                message="Not enough gold!",
                options=[("Bummer!", self.pick_buy)],
            )
        return PickArgs(
            message=f"Are you sure you want to buy {item.tui_str} for {Formatter.gold(item.value)}?",  # pylint: disable=line-too-long
            options=[
                ("Yes", partial(self.buy, item)),
                ("No", self.pick_buy),
            ],
        )

    def buy(self, item: Item):
        player.gold -= item.value
        player.inventory.add_item(item)
        self.remove_item(item)
        if item.type == ItemType.WEAPON:
            stats.increment_int_stat(IntegerStatKeys.WEAPONS_PURCHASED)
        elif item.type in EQUIPMENT_TYPES:
            stats.increment_int_stat(IntegerStatKeys.ARMOR_PURCHASED)
        FileManager.multi_save(player, item, stats)
        return self.enter()

    def confirm_multi_buy(self, items: list[Item]):
        assert self.buying_option
        cost = sum(item.value for item in items)
        if player.gold < cost:
            return PickArgs(
                message="Not enough gold!",
                options=[("Bummer!", self.pick_buy)],
            )
        return PickArgs(
            message=f"Are you sure you want to buy {self.buying_option.name} for {Formatter.gold(cost)}?",  # pylint: disable=line-too-long
            options=[
                ("Yes", partial(self.multi_buy, items)),
                ("No", self.pick_buy),
            ],
        )

    def multi_buy(self, items: list[Item]):
        cost = sum(item.value for item in items)
        player.gold -= cost
        player.inventory.add_items(items)
        self.remove_items(*items)
        FileManager.multi_save(player, *items)
        return self.enter()

    def hint_symbol(self, item: Item):
        if item.type not in EQUIPMENT_TYPES:
            return None
        if player.has_upgrade("advanced_store_hints") and self.is_best_item(item):
            return "🔥"
        if player.has_upgrade("store_hints") and self.is_useful_item(item):
            return "✨"
        return None

    def is_best_item(self, item: Item):
        best = player.inventory.get_best_in_slot(item.type)
        for character in player.army:
            equipped = character.equipment.get_slot_item(item.type)
            if equipped is None:
                continue
            if best is None or equipped.main_affect > best.main_affect:
                best = equipped
        return best is None or item.main_affect > best.main_affect

    def is_useful_item(self, item: Item):
        for character in player.army:
            equipped = character.equipment.get_slot_item(item.type)
            if equipped is None or item.main_affect > equipped.main_affect:
                return True
        return False
