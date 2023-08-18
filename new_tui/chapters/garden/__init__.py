from myning.objects.buying_option import BuyingOption
from myning.objects.garden import Garden
from myning.objects.item import ItemType
from myning.objects.plant import Plant
from myning.objects.player import Player
from myning.utils import utils
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_plant
from new_tui.chapters import PickArgs, main_menu
from new_tui.chapters.base_store import BaseStore
from new_tui.chapters.garden.manage import manage_garden
from new_tui.formatter import Formatter

player = Player()
garden = Garden()


def enter():
    return PickArgs(
        message="Select an option:",
        options=[
            ("Manage Garden", manage_garden),
            ("Buy Seeds", GardenStore().pick_buy),
            ("Upgrade Garden", confirm_upgrade),
            ("View Harvest", view_harvest),
            ("Go Back", main_menu.enter),
        ],
        border_title="Garden",
    )


class GardenStore(BaseStore):
    def __init__(self):
        if player.has_upgrade("buy_all_garden"):
            self.buying_option = BuyingOption("all seeds", lambda _: True)
        super().__init__()

    def generate(self):
        for _ in range(1, max(garden.level, 5)):
            self.inventory.add_item(generate_plant(garden.level))

    def enter(self):
        return enter()


def confirm_upgrade():
    cost = garden_cost(garden.level)
    if player.gold < cost:
        return PickArgs(
            message=f"You need {Formatter.gold(cost)} to upgrade your garden size to "
            f"{garden.level + 1}",
            options=[("Bummer!", enter)],
        )
    return PickArgs(
        message=f"Upgrade your garden size to {garden.level + 1} for {Formatter.gold(cost)}?",
        options=[
            ("Yes", upgrade),
            ("No", enter),
        ],
    )


def upgrade():
    cost = garden_cost(garden.level)
    player.gold -= cost
    garden.level_up()
    FileManager.multi_save(player, garden)
    return enter()


def view_harvest():
    options = []
    for plant in player.inventory.get_slot(ItemType.PLANT.value):
        # TODO fix return type of inventory.get_slot to resolve type issue
        assert isinstance(plant, Plant)
        if plant.harvested:
            options.append((plant.fruit_stand_arr, view_plant))
    options.append((["", "Go Back"], enter))
    return PickArgs(
        message="View your plants",
        options=options,
    )


def view_plant():
    return PickArgs(
        message="Eventually, you'll be able to do more than sell your plants. (But not yet)",
        options=[("Bummer!", enter)],
    )


def garden_cost(level):
    return utils.fibonacci(level + 4) * 100
