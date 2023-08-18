from myning.chapters import visit_store
from myning.config import UPGRADES
from myning.objects.buying_option import BuyingOption, StoreType
from myning.objects.garden import Garden
from myning.objects.item import ItemType
from myning.objects.plant import Plant
from myning.objects.player import Player
from myning.objects.settings import Settings, SortOrder
from myning.objects.stats import IntegerStatKeys, Stats
from myning.objects.store import Store
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_plant
from myning.utils.io import pick
from myning.utils.ui import columnate, get_gold_string, get_water_string


def play():
    player, garden, store, settings = Player(), Garden(), Store(), Settings()

    def get_seeds():
        for _ in range(1, max(garden.level, 5)):
            store.add_item(generate_plant(garden.level))

    get_seeds()

    while True:
        option, _ = pick(
            ["Manage Garden", "Buy Seeds", "Upgrade Garden", "View Harvest", "Go Back"]
        )

        if option == "Manage Garden":
            manage_garden(garden)
        elif option == "Buy Seeds":
            if store.empty:
                get_seeds()

            items = store.items
            if (
                player.has_upgrade("sort_by_value")
                and "garden" in UPGRADES["sort_by_value"].player_value
                and settings.sort_order == SortOrder.VALUE
            ):
                items = store.items_by_value

            buying_options = None
            if player.has_upgrade("buy_all_garden"):
                buying_options = BuyingOption(
                    name="all items", store_type=StoreType.GARDEN, options_string="Fast Buy All"
                )
            bought_items = visit_store.buy(items, player, buying_options)
            for seed in bought_items:
                store.remove_item(seed)
                player.inventory.add_item(seed)
                FileManager.save(seed)
            FileManager.multi_save(player, garden)

        elif option == "Upgrade Garden" and upgrade_garden(garden.upgrade_cost, player):
            garden.level_up()
            FileManager.save(garden)
        elif option == "View Harvest":
            plants = [
                plant.fruit_stand_arr
                for plant in player.inventory.get_slot(ItemType.PLANT.value)
                if plant.harvested
            ]
            options = columnate(plants)
            option, _ = pick([*options, "Go Back"], "View your plants")

            if option == "Go Back":
                continue

            pick(
                ["Bummer!"],
                "Eventually, you'll be able to do more than sell your plants. (But not yet)",
            )
        elif option == "Go Back":
            break


def manage_garden(garden: Garden):
    player = Player()
    stats = Stats()
    while True:
        garden.collect_water()
        rows = str(garden).split("\n")

        if player.has_upgrade("next_plant_button"):
            rows.append("Next Plant")

        if player.has_upgrade("harvest_row"):
            rows.append("Harvest Next Row")

        if player.has_upgrade("plant_row"):
            rows.append("Plant Next Row")

        option, index = pick(
            [*rows, "Refresh Garden", "Go Back"],
            f"Manage your garden ({get_water_string(garden.water)})",
        )

        if option == "Go Back":
            break
        if option == "Refresh Garden":
            continue
        if option == "Next Plant":
            row, col = garden.next_plant_coords
            if row is None or col is None:
                pick(["Go Back"], "There are no more plants ready to harvest")
                continue
            manage_plant(garden, row, col)
            continue
        if option == "Harvest Next Row":
            row = garden.next_unharvest_row
            if row is None:
                pick(["Go Back"], "There are no more plants ready to harvest")
                continue

            for column in range(garden.level):
                plant = garden.get_plant(row, column)
                if plant and plant.ready:
                    garden.harvest_plant(row, column)
                    stats.increment_int_stat(IntegerStatKeys.PLANTS_HARVESTED)
                    player.inventory.add_item(plant)
                    FileManager.save(plant)
            FileManager.multi_save(player, garden, stats)
            continue
        if option == "Plant Next Row":
            row = garden.next_empty_row
            if row is None:
                pick(["Go Back"], "Everything is planted!")
                continue

            for column in range(garden.level):
                plant = garden.get_plant(row, column)
                if not plant and player.seeds:
                    plant_seed(garden, row, column, 0)

            continue

        if index == 0 or index == garden.level + 1:
            pick(["Bummer!"], "Please select a valid row of plants")
            continue

        row = index - 1

        columns = [
            column.replace("║", "").replace(" ", "") for column in rows[index].split("║")[1:-1]
        ]
        option, index = pick([*columns, "Go Back"], "Manage your garden")

        if option == "Go Back":
            continue

        column = index

        plant = garden.get_plant(row, column)
        if not plant:
            plant_seed(garden, row, column)
        else:
            manage_plant(garden, row, column)


def upgrade_garden(cost: int, player: Player):
    if player.pay(
        cost,
        failure_msg=f"You need {get_gold_string(cost)} to upgrade your garden",
        failure_option="Bummer!",
        confirmation_msg=f"Upgrade your garden for {get_gold_string(cost)}?",
    ):
        return True
    return False


def plant_seed(garden: Garden, row: int, column: int, index=None):
    player = Player()
    if not player.seeds:
        pick(["Bummer!"], "You don't have any seeds to plant")
        return

    if index is None:
        options = columnate([seed.str_arr for seed in player.seeds])
        option, index = pick([*options, "Go Back"], "Select a seed to plant")

        if option == "Go Back":
            return

    plant: Plant = player.seeds[index]
    plant.sow()
    garden.add_plant(plant, row, column)
    player.inventory.remove_item(plant)
    FileManager.multi_save(player, plant, garden)


def manage_plant(garden: Garden, row: int, column: int):
    player = Player()
    stats = Stats()
    garden.collect_water()

    options = []
    plant = garden.get_plant(row, column)
    if plant.ready:
        options.append("Harvest")
    else:
        options.append("Water")
        options.append("Remove")

    option, _ = pick(
        [*options, "Go Back"],
        f"What would you like to do with this plant? ({get_water_string(garden.water)})",
        sub_title=plant.details_string,
    )

    if option == "Go Back":
        return

    if option == "Harvest":
        plant = garden.harvest_plant(row, column)
        stats.increment_int_stat(IntegerStatKeys.PLANTS_HARVESTED)
        player.inventory.add_item(plant)
        FileManager.save(stats)
    elif option == "Water":
        if garden.water:
            garden.water_plant(row, column)
        else:
            pick(
                ["Bummer!"],
                "You don't have any water to water your plants. (You'll get more over time)",
            )
    elif option == "Remove":
        option, _ = pick(["Yes", "No"], "Are you sure you want to remove this plant?")
        if option == "No":
            return
        garden.uproot_plant(row, column)

    FileManager.multi_save(player, plant, garden)
