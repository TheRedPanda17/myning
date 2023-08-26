import random

from myning.chapters import Option, PickArgs
from myning.chapters.base_store import BaseStore
from myning.config import STRINGS, UPGRADES
from myning.objects.blacksmith_item import BlacksmithItem
from myning.objects.buying_option import BuyingOption
from myning.objects.equipment import EQUIPMENT_TYPES
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utilities.fib import fibonacci
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter

player = Player()

TIERS = [
    BlacksmithItem("Soldier", 15, 50),
    BlacksmithItem("Commander", 20, 250),
    BlacksmithItem("General", 30, 500),
    BlacksmithItem("Samurai", 40, 1_000),
    BlacksmithItem("Ninja", 50, 2_000),
    BlacksmithItem("Jedi", 75, 5_000),
    BlacksmithItem("Blademaster", 100, 10_000),
    BlacksmithItem("Spartan", 150, 40_000),
    BlacksmithItem("Hero", 250, 200_000),
]


def enter():
    return Blacksmith().enter()


class Blacksmith(BaseStore):
    def __init__(self):
        if player.has_upgrade("buy_full_set"):
            tier = UPGRADES["buy_full_set"].player_value
            self.buying_option = BuyingOption(
                f"all {tier} items",
                lambda item: tier in item.name,
            )
        super().__init__()

    @property
    def level(self):
        return player.blacksmith_level

    @property
    def maxed(self):
        return self.level >= len(TIERS)

    @property
    def upgrade_cost(self):
        return fibonacci(self.level + 4) * 100

    def generate(self):
        for tier in TIERS[: self.level]:
            for item_type in EQUIPMENT_TYPES:
                value = tier.value if item_type == ItemType.WEAPON else int(tier.value * 0.4)
                type_name = random.choice(STRINGS[item_type.lower()])
                name = f"{tier.name}'s {type_name}"
                description = f"A {item_type.name}'s  {type_name}."
                item = Item(name, description, item_type, value, tier.main_affect)
                if not any(i.value == item.value and i.type == item.type for i in self.items):
                    self.add_item(item)

    def enter(self):
        self.generate()
        return PickArgs(
            message="What would you like to do?",
            options=[
                Option("Buy", self.pick_buy, enable_hotkeys=True),
                Option(
                    Formatter.locked("Upgrade Smith (maxed)")
                    if self.maxed
                    else f"Upgrade Smith ({Formatter.gold(self.upgrade_cost)})",
                    self.confirm_upgrade,
                    enable_hotkeys=True,
                ),
                Option("Go Back", self.exit),
            ],
        )

    def confirm_multi_buy(self, items: list[Item]):
        assert self.buying_option
        if not items:
            return PickArgs(
                message=f"Blacksmith does not have {self.buying_option.name.partition(' ')[2]}; "
                "you need to upgrade the smith first.",
                options=[("Shucks", self.pick_buy)],
            )
        return super().confirm_multi_buy(items)

    def confirm_upgrade(self):
        if self.maxed:
            return PickArgs(
                message=f"Blacksmith cannot build anything more beneficial than {TIERS[-1].name}.",
                options=[Option("Go Back", self.enter)],
            )
        if player.gold < self.upgrade_cost:
            return PickArgs(
                message="You don't have enough gold to upgrade your blacksmith.",
                options=[Option("Shucks", self.enter)],
            )
        return PickArgs(
            message="Are you sure you want to upgrade your blacksmith "
            f"for {Formatter.gold(self.upgrade_cost)}?",
            options=[
                Option(f"Upgrade to level {self.level+1}", self.upgrade, enable_hotkeys=True),
                Option("Maybe Later", self.enter),
            ],
        )

    def upgrade(self):
        player.gold -= self.upgrade_cost
        player.blacksmith_level += 1
        FileManager.save(player)
        self.remove_items(*self.items)
        self.generate()
        return self.enter()
