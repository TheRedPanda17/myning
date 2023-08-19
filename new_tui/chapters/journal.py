from functools import partial

from rich.table import Table

from myning.config import RACES
from myning.objects.player import Player
from myning.objects.race import Race
from myning.utils.ui_consts import Icons
from new_tui.chapters import Option, PickArgs, main_menu
from new_tui.formatter import Colors

player = Player()
RACES: dict[str, Race]


def enter():
    race_list = RACES.values()
    options: list[Option] = [
        (
            [race.icon, race.name]
            if race in player.discovered_races
            else [Icons.LOCKED, f"[{Colors.LOCKED}]{'*'*len(race.name)}[/]"],
            partial(show, race),
        )
        for race in race_list
    ]
    options.append((["", "Go Back"], main_menu.enter))
    return PickArgs(
        message="Select a Species to learn about them.",
        options=options,
    )


def show(race: Race):
    if race not in player.discovered_races:
        return PickArgs(
            message="You have not discovered this species yet.",
            options=[("Go Back", enter)],
        )
    table = Table.grid(padding=(0, 2))
    table.title = f"{race.icon} {race.name}"
    table.title_style = "bold"
    table.add_row()
    table.add_row("Rarity", race.rarity)
    table.add_row("Stats", race.stats)
    table.add_row("Alignment", race.alignment)
    return PickArgs(
        message=table,
        options=[("Go Back", enter)],
        subtitle="\n" + race.description,
    )
