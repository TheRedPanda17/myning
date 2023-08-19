import math
import sys
from functools import partial
from typing import TYPE_CHECKING

from rich.table import Table

from myning.config import XP_COST
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.ui_consts import Icons
from new_tui.chapters import PickArgs, main_menu
from new_tui.chapters.blacksmith import smith_cost
from new_tui.formatter import Colors
from new_tui.utilities import confirm

if TYPE_CHECKING:
    from new_tui.view.chapter import ChapterWidget

player = Player()
facility = ResearchFacility()


def enter():
    value = get_total_value()
    xp_boost = get_boost(player.macguffin.exp_boost, value)
    mineral_boost = get_boost(player.macguffin.mineral_boost, value)
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
    journal = player.discovered_races
    migrations = player.completed_migrations
    name = player.name
    settings = Settings()

    # Reset the game
    FileManager.backup_game()
    FileManager.reset_game()
    Singleton.reset()  # type: ignore

    Player.initialize(name)
    new_player = Player()
    new_player.macguffin.exp_boost = xp_boost
    new_player.macguffin.mineral_boost = mineral_boost
    new_player.discovered_races = journal
    new_player.completed_migrations = migrations
    Settings().initialize()
    FileManager.multi_save(new_player, settings)

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


def get_total_value():
    item_value = sum(item.value for item in player.inventory.items)
    army_value = sum(member.value for member in player.army)
    exp_value = player.exp_available * XP_COST
    upgrades_value = sum(sum(u.costs[: u.level]) for u in player.upgrades)
    blacksmith_cost = sum(smith_cost(level) for level in range(1, player.blacksmith_level + 1))
    unlocked_mines = sum(mine.cost for mine in player.mines_available)
    beaten_mines = int(
        sum(mine.win_value * math.pow(mine.cost, 1 / 3) for mine in player.mines_completed)
    )
    research = sum(sum(u.costs[: u.level]) for u in facility.research) * 5
    research_facility = sum(smith_cost(level) for level in range(1, facility.level + 1)) * 5

    return (
        item_value
        + army_value
        + player.gold
        + exp_value
        + upgrades_value
        + blacksmith_cost
        + unlocked_mines
        + beaten_mines
        + research
        + research_facility
    )
