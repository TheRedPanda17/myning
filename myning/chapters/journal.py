from functools import partial

from rich.table import Table

from myning.chapters import Option, PickArgs, main_menu
from myning.config import SPECIES
from myning.objects.player import Player
from myning.objects.species import Species
from myning.utilities.ui import Colors, Icons

player = Player()


def enter():
    species_list = SPECIES.values()
    options: list[Option] = [
        (
            [species.icon, species.name]
            if species in player.discovered_species
            else [Icons.LOCKED, f"[{Colors.LOCKED}]{'*'*len(species.name)}[/]"],
            partial(show, species),
        )
        for species in species_list
    ]
    options.append((["", "Go Back"], main_menu.enter))
    return PickArgs(
        message="Select a Species to learn about them.",
        options=options,
    )


def show(species: Species):
    if species not in player.discovered_species:
        return PickArgs(
            message="You have not discovered this species yet.",
            options=[("Go Back", enter)],
        )
    table = Table.grid(padding=(0, 2))
    table.title = f"{species.icon} {species.name}"
    table.title_style = "bold"
    table.add_row()
    table.add_row("Rarity", species.rarity)
    table.add_row("Stats", species.stats)
    table.add_row("Alignment", species.alignment)
    return PickArgs(
        message=table,
        options=[("Go Back", enter)],
        subtitle="\n" + species.description,
    )
