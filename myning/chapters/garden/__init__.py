from myning.chapters import Option, PickArgs, main_menu
from myning.chapters.base_store import BaseStore
from myning.chapters.garden.manage import manage_garden
from myning.objects.buying_option import BuyingOption
from myning.objects.garden import Garden as GardenObject
from myning.objects.inventory import Inventory
from myning.objects.item import ItemType
from myning.objects.player import Player
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.generators import generate_plant

player = Player()
garden = GardenObject()
inventory = Inventory()


def enter():
    return Garden().enter()


class Garden(BaseStore):
    def __init__(self):
        if player.has_upgrade("buy_all_garden"):
            self.buying_option = BuyingOption("all seeds", lambda _: True)
        super().__init__()

    def generate(self):
        amount = max(garden.level, 5)
        self.add_items(*(generate_plant(garden.level) for _ in range(amount)))

    def enter(self):
        return PickArgs(
            message="Select an option:",
            options=[
                Option("Manage Garden", manage_garden),
                Option("Buy Seeds", self.pick_buy),
                Option("Upgrade Garden", self.confirm_upgrade),
                Option("View Harvest", self.view_harvest),
                Option("Go Back", main_menu.enter),
            ],
            border_title="Garden",
        )

    def confirm_upgrade(self):
        if player.gold < garden.upgrade_cost:
            return PickArgs(
                message=f"You need {Formatter.gold(garden.upgrade_cost)} to upgrade your garden "
                f"size to {garden.level + 1}",
                options=[Option("Bummer!", self.enter)],
            )
        return PickArgs(
            message=f"Upgrade your garden size to {garden.level + 1} "
            f"for {Formatter.gold(garden.upgrade_cost)}?",
            options=[
                Option("Yes", self.upgrade),
                Option("No", self.enter),
            ],
        )

    def upgrade(self):
        player.gold -= garden.upgrade_cost
        garden.level_up()
        FileManager.multi_save(player, garden)
        return self.enter()

    def view_harvest(self):
        options = [
            Option(plant.fruit_stand_arr, self.view_plant, enable_hotkeys=False)
            for plant in inventory.get_slot(ItemType.PLANT)
            if plant.harvested
        ]
        options.append(Option(["", "Go Back"], self.enter))
        return PickArgs(
            message="View your plants",
            options=options,
        )

    def view_plant(self):
        return PickArgs(
            message="Eventually, you'll be able to do more than sell your plants. (But not yet)",
            options=[Option("Bummer!", self.enter)],
        )
