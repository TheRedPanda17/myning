from functools import partial
from typing import TYPE_CHECKING

from myning.chapters import DynamicArgs, Handler, Option, PickArgs
from myning.chapters.garden.garden_table import GardenTable
from myning.objects.garden import Garden
from myning.objects.plant import Plant
from myning.objects.player import Player
from myning.objects.stats import IntegerStatKeys, Stats
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import confirm

if TYPE_CHECKING:
    from myning.view.chapter import ChapterWidget

player = Player()
garden = Garden()
stats = Stats()


def manage_garden():
    garden.collect_water()
    return DynamicArgs(callback=manage_garden_callback)


def manage_garden_callback(chapter: "ChapterWidget"):
    from myning.chapters.garden import enter  # pylint: disable=import-outside-toplevel

    garden_table = GardenTable()
    chapter.mount(garden_table, after=0)

    def exit_manage_garden(callback: Handler):
        garden_table.remove()
        chapter.option_table.show_cursor = True
        return callback()

    options = []
    if player.has_upgrade("next_plant_button"):
        options.append(("Next Plant", partial(exit_manage_garden, next_plant)))
    if player.has_upgrade("harvest_row"):
        options.append(("Harvest Next Row", partial(exit_manage_garden, harvest_row)))
    if player.has_upgrade("plant_row"):
        options.append(("Plant Next Row", partial(exit_manage_garden, plant_row)))
    options.append(("Go Back", partial(exit_manage_garden, enter)))
    chapter.option_table.show_cursor = False
    chapter.pick(
        PickArgs(
            message=f"Manage your garden (size {garden.level}, "
            f"{Formatter.water(garden.water)} available)",
            options=options,
        )
    )


def next_plant():
    row, col = garden.next_plant_coords
    if row is None and col is None:
        return PickArgs(
            message="There are no more plants ready to harvest",
            options=[("Go Back", manage_garden)],
        )
    return manage_plant(row, col)  # type: ignore


def harvest_row():
    row = garden.next_unharvest_row
    if row is None:
        return PickArgs(
            message="There are no more plants ready to harvest",
            options=[("Go Back", manage_garden)],
        )
    for column in range(garden.level):
        plant = garden.get_plant(row, column)
        if plant and plant.ready:
            harvest_plant(row, column)
    FileManager.multi_save(player, garden)
    return manage_garden()


def plant_row():
    row = garden.next_empty_row
    if row is None:
        return PickArgs(
            message="Everything is planted!",
            options=[("Go Back", manage_garden)],
        )
    for column in range(garden.level):
        plant = garden.get_plant(row, column)
        seed = next(iter(player.seeds), None)
        if not seed:
            return PickArgs(
                message="You have run out of seeds to plant",
                options=[("Bummer!", manage_garden)],
            )
        if not plant:
            # TODO fix return type of inventory.get_slot to resolve type issue
            assert isinstance(seed, Plant)
            plant_seed(seed, row, column)
    FileManager.multi_save(player, garden)
    return manage_garden()


def manage_plant(row: int, column: int):
    garden.collect_water()
    plant = garden.get_plant(row, column)
    if not plant:
        return pick_seed(row, column)

    options: list[Option]
    if plant.ready:
        options = [("Harvest", partial(harvest_plant, row, column))]
    else:
        options = [
            ("Water", partial(water_plant, row, column)),
            ("Remove", partial(remove_plant, row, column)),
        ]
    options.append(("Go Back", manage_garden))

    return PickArgs(
        message="What would you like to do with this plant? "
        f"({Formatter.water(garden.water)} available)",
        options=options,
        subtitle=plant.tui_details,
    )


def pick_seed(row: int, column: int):
    if not player.seeds:
        return PickArgs(
            message="You don't have any seeds to plant",
            options=[("Bummer!", manage_garden)],
        )

    options: list[Option] = [
        (seed.tui_arr, partial(plant_seed, seed, row, column))
        for seed in player.seeds
        # TODO fix return type of inventory.get_slot to resolve type issue
        if isinstance(seed, Plant)
    ]
    options.append((["", "Go Back"], manage_garden))
    return PickArgs(
        message="Select a seed to plant",
        options=options,
    )


def plant_seed(seed: Plant, row: int, column: int):
    seed.sow()
    garden.add_plant(seed, row, column)
    player.inventory.remove_item(seed)
    FileManager.multi_save(player, garden, seed)
    return manage_garden()


def harvest_plant(row: int, column: int):
    plant = garden.harvest_plant(row, column)
    player.inventory.add_item(plant)
    stats.increment_int_stat(IntegerStatKeys.PLANTS_HARVESTED)
    FileManager.multi_save(player, garden, plant, stats)
    return manage_garden()


def water_plant(row: int, column: int):
    if not garden.water:
        return PickArgs(
            message="You don't have any water to water your plants (you'll get more over time).",
            options=[("Bummer!", partial(manage_plant, row, column))],
        )
    plant = garden.water_plant(row, column)
    FileManager.multi_save(player, garden, plant)
    return manage_plant(row, column)


@confirm(
    lambda row, column: "Are you sure you want to remove this "
    f"{garden.get_plant(row, column).icon} plant?",  # type:ignore
    manage_garden,
)
def remove_plant(row: int, column: int):
    plant = garden.uproot_plant(row, column)
    FileManager.delete(plant)
    FileManager.multi_save(player, garden)
    return manage_garden()
