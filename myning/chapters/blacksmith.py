import random
from functools import partial

from myning.chapters import PickArgs
from myning.chapters.base_store import BaseStore
from myning.config import STRINGS, UPGRADES
from myning.formatter import Formatter
from myning.objects.blacksmith_item import BlacksmithItem
from myning.objects.buying_option import BuyingOption
from myning.objects.equipment import EQUIPMENT_TYPES
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utils import utils
from myning.utils.file_manager import FileManager

player = Player()

TIERS = [
    BlacksmithItem("Soldier", 15, 50),
    BlacksmithItem("Commander", 20, 250),
    BlacksmithItem("General", 30, 500),
    BlacksmithItem("Samurai", 40, 1000),
    BlacksmithItem("Ninja", 50, 2000),
    BlacksmithItem("Jedi", 75, 5000),
    BlacksmithItem("Blademaster", 100, 10000),
    BlacksmithItem("Spartan", 150, 40000),
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

    # TODO improve logic and refactor BlacksmithItem class, lots of room for improvement
    def generate(self):
        for tier in TIERS:
            for item_type in EQUIPMENT_TYPES:
                value = tier.value if item_type == ItemType.WEAPON else int(tier.value * 0.4)
                type_name = random.choice(STRINGS[item_type.lower()])
                name = f"{tier.name}'s {type_name}"
                description = f"A {item_type.name}'s  {type_name}."
                self.add_item(Item(name, description, item_type, value, tier.main_affect))

    def enter(self):
        cost = smith_cost(self.level)
        upgrade_option = (
            Formatter.locked("Upgrade Smith (maxed)")
            if self.maxed
            else f"Upgrade Smith ({Formatter.gold(cost)})"
        )
        return PickArgs(
            message="What would you like to do?",
            options=[
                ("Buy", self.pick_buy),
                (upgrade_option, partial(self.confirm_upgrade, cost)),
                ("Go Back", self.exit),
            ],
        )

    def confirm_upgrade(self, cost: int):
        if self.maxed:
            return PickArgs(
                message=f"Blacksmith cannot build anything more beneficial than {TIERS[-1].name}.",
                options=[("Go Back", self.enter)],
            )
        if player.gold < cost:
            return PickArgs(
                message="You don't have enough gold to upgrade your blacksmith.",
                options=[("Shucks", self.enter)],
            )
        return PickArgs(
            message=f"Are you sure you want to upgrade your blacksmith for {cost}g?",
            options=[
                (f"Upgrade to level {self.level+1}", partial(self.upgrade, cost)),
                ("Maybe Later", self.enter),
            ],
        )

    def upgrade(self, cost: int):
        player.gold -= cost
        player.blacksmith_level += 1
        FileManager.save(player)
        return self.enter()


def smith_cost(level):
    return utils.fibonacci(level + 4) * 100
