import sys
from functools import partial
from typing import TYPE_CHECKING

from rich.table import Table

from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.ui_consts import Icons
from new_tui.chapters import PickArgs, main_menu
from new_tui.formatter import Colors
from new_tui.utilities import confirm

if TYPE_CHECKING:
    from new_tui.view.chapter import ChapterWidget

facility = ResearchFacility()
garden = Garden()
macguffin = Macguffin()
player = Player()


def enter():
    value = get_total_value()
    xp_boost = get_boost(macguffin.xp_boost, value)
    mineral_boost = get_boost(macguffin.mineral_boost, value)
    return PickArgs(
        message="What would you like to do?",
        options=[
            ("View Potential Macguffin", partial(view_potential, xp_boost, mineral_boost)),
            ("Go Back in Time", partial(go_back_in_time, xp_boost, mineral_boost)),
            ("About", about),
            ("Go Back", main_menu.enter),
        ],
    )


def view_potential(xp_boost, mineral_boost):
    xp_boost_str = f"{xp_boost * 100}%"
    mineral_boost_str = f"{mineral_boost * 100}%"
    table = Table.grid(padding=(0, 1))
    table.title = "Potential Macguffin Boosts"
    table.title_style = "bold underline"
    table.min_width = len(table.title)
    table.add_row("Mineral value:", Icons.GOLD, f"[{Colors.GOLD}]{mineral_boost_str}[/]")
    table.add_row("XP gain:", Icons.XP, f"[{Colors.XP}]{xp_boost_str}[/]")
    return PickArgs(
        message=table,
        options=[("Cool cool cool", enter)],
    )


@confirm(
    # pylint: disable=line-too-long
    lambda xp_boost, mineral_boost: "Are you sure you want to erase ALL progress and go back in time?\n"
    f"[{Colors.LOCKED}]You'll lose all your progress and gain a {int(mineral_boost*100)}% mineral value boost and a {int(xp_boost*100)}% xp boost.",
    enter,
)
def go_back_in_time(xp_boost, mineral_boost):
    value = get_total_value()
    standard_boost = macguffin.get_new_standard_boost(value)
    small_boost = macguffin.get_new_smaller_boost(value)

    journal = player.discovered_species
    migrations = player.completed_migrations
    new_species = player.roll_for_species()
    player_name = player.name
    player_id = player.id

    # Reset the game
    FileManager.backup_game()
    FileManager.reset_game()
    Singleton.reset()  # type: ignore

    Player.initialize(player_name)
    new_player = Player()
    new_player.discovered_species = journal
    new_player.completed_migrations = migrations
    new_player.id = player_id
    player.species = new_species

    Macguffin.initialize()
    new_macguffin = Macguffin()
    new_macguffin.xp_boost = standard_boost
    new_macguffin.mineral_boost = standard_boost
    new_macguffin.research_boost = small_boost
    new_macguffin.soul_credit_boost = small_boost
    new_macguffin.plant_boost = small_boost

    FileManager.multi_save(new_player, new_macguffin)

    # TODO fix jank, don't use exit ideally
    # Janky, but this will exit to the run.sh loop which will reboot the game. Basically purges
    # the memory of the game.
    sys.exit(123)


def about():
    return PickArgs(
        message="About Going Back in Time",
        options=[("I understand", enter)],
        subtitle="When you go back in time, you will gain a macguffin which will provide an xp and "
        "mineral value boost. Unfortunately, you'll lose everything else you have (including "
        "upgrades). Journal unlocks will not be lost.",
    )


def get_boost(current_boost: int, game_value: int):
    return round((game_value / 500000) + current_boost, 2)


# This is the same function as in the stats page. I haven't figured out a great place where they can
# share this function and I don't want to cross import
def get_total_value() -> int:
    return player.total_value + facility.total_value + garden.total_value
