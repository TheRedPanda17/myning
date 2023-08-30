from functools import partial

from rich.table import Table

from myning.chapters import Option, PickArgs, main_menu
from myning.config import RESEARCH, SPECIES
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.species import Species
from myning.utilities.ui import Colors, Icons

player = Player()
facility = ResearchFacility()


def enter():
    species_list = SPECIES.values()
    options = [
        Option(
            [species.icon, species.name]
            if species in player.discovered_species
            else [Icons.LOCKED, f"[{Colors.LOCKED}]{'*'*len(species.name)}[/]"],
            partial(show, species),
            enable_hotkeys=False,
        )
        for species in species_list
        if species.name != "Alien"
    ]
    options.append(Option(["", "Go Back"], main_menu.enter))
    return PickArgs(
        message="Select a Species to learn about them.",
        options=options,
    )


def show(species: Species):
    if species not in player.discovered_species:
        return PickArgs(
            message="You have not discovered this species yet.",
            options=[Option("Go Back", enter)],
        )

    exact_stats = (
        facility.has_research("show_species_stats")
        and RESEARCH["show_species_stats"].player_value >= species.rarity_tier
    )

    table = Table.grid(padding=(0, 2))
    table.title = f"{species.icon} {species.name}"
    table.title_style = "bold"
    table.add_row()
    table.add_row("Rarity", species.rarity)
    table.add_row("Stats", species.get_stats(exact_stats))
    table.add_row("Alignment", species.alignment)
    return PickArgs(
        message=table,
        options=[Option("Go Back", enter)],
        subtitle="\n" + species.description,
    )
