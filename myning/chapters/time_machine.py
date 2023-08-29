import sys

from rich.table import Table

from myning.chapters import Option, PickArgs, main_menu
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.singleton import Singleton
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import confirm
from myning.utilities.ui import Colors, Icons

facility = ResearchFacility()
garden = Garden()
macguffin = Macguffin()
player = Player()


def enter():
    return PickArgs(
        message="What would you like to do?",
        options=[
            Option("View Potential Macguffin", view_potential),
            Option("Go Back in Time", go_back_in_time),
            Option("About", about),
            Option("Go Back", main_menu.enter),
        ],
    )


# This is the same function as in the stats page. I haven't figured out a great place where they can
# share this function and I don't want to cross import
def get_total_value():
    return player.total_value + facility.total_value + garden.total_value


def get_potential_standard_boost():
    return macguffin.get_new_standard_boost(get_total_value())


def get_potential_smaller_boost():
    return macguffin.get_new_smaller_boost(get_total_value())


def view_potential():
    standard = get_potential_standard_boost()
    smaller = get_potential_smaller_boost()
    table = Table.grid(padding=(0, 1))
    table.title = "Potential Macguffin Boosts"
    table.title_style = "bold underline"
    table.min_width = len(table.title)
    table.add_row(
        "Mineral value:",
        Icons.GOLD,
        f"[{Colors.GOLD}]{Formatter.percentage(standard)}[/]",
    )
    table.add_row(
        "XP gain:",
        Icons.XP,
        f"[{Colors.XP}]{Formatter.percentage(standard)}[/]",
    )
    table.add_row(
        "Soul credits:",
        Icons.GRAVEYARD,
        f"[{Colors.SOUL_CREDITS}]{Formatter.percentage(smaller)}[/]",
    )
    table.add_row(
        "Research speed:",
        Icons.RESEARCH_FACILITY,
        f"[{Colors.RESEARCH_POINTS}]{Formatter.percentage(smaller)}[/]",
    )
    table.add_row(
        "Plant value:",
        Icons.PLANT,
        f"[{Colors.PLANT}]{Formatter.percentage(smaller)}[/]",
    )
    return PickArgs(
        message=table,
        options=[Option("Cool cool cool", enter)],
    )


@confirm(
    "\n".join(
        [
            "Are you sure you want to erase ALL progress and go back in time?",
            f"[{Colors.LOCKED}]You'll lose all your progress and gain the following boosts:",
            f"{Formatter.percentage(get_potential_standard_boost())} mineral value",
            f"{Formatter.percentage(get_potential_standard_boost())} xp gain",
            f"{Formatter.percentage(get_potential_smaller_boost())} soul credits",
            f"{Formatter.percentage(get_potential_smaller_boost())} research speed",
            f"{Formatter.percentage(get_potential_smaller_boost())} plant value",
            "",
            "Oh, yeah, and there's a slight chance you may experience a bit of transmogrification.",
        ]
    ),
    enter,
)
def go_back_in_time():
    standard = get_potential_standard_boost()
    smaller = get_potential_smaller_boost()

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
    new_player.species = new_species
    new_player.health = new_player.max_health

    Macguffin.initialize()
    new_macguffin = Macguffin()
    new_macguffin.xp_boost = standard
    new_macguffin.mineral_boost = standard
    new_macguffin.research_boost = smaller
    new_macguffin.soul_credit_boost = smaller
    new_macguffin.plant_boost = smaller

    FileManager.multi_save(new_player, new_macguffin)

    # TODO fix jank, don't use exit ideally
    # Janky, but this will exit to the run.sh loop which will reboot the game. Basically purges
    # the memory of the game.
    sys.exit(123)


def about():
    return PickArgs(
        message="About Going Back in Time",
        options=[Option("I understand", enter)],
        subtitle="When you go back in time, you will gain a macguffin which will provide a mineral "
        "value, xp gain, soul credit, research speed, and plant value boost. Unfortunately, you'll "
        "lose everything else you have (including upgrades). Journal unlocks will not be lost.",
    )
