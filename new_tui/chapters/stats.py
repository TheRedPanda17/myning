from datetime import datetime
from functools import partial

from rich.table import Table
from rich.text import Text

from myning import api
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.stats import Stats
from myning.utils.ui import normalize_title
from myning.utils.ui_consts import Icons
from new_tui.chapters import Option, PickArgs, main_menu
from new_tui.formatter import Formatter

facility = ResearchFacility()
garden = Garden()
macguffin = Macguffin()
player = Player()
stats = Stats()


def enter():
    return PickArgs(
        message="Stats\n",
        options=[
            ("Sync Stats", sync),
            ("View Highscores", pick_player),
            ("Go Back", main_menu.enter),
        ],
        subtitle=stats.tui_display,
    )


def sync():
    # score = macguffin.get_new_standard_boost(get_total_value())
    # api.player.sync(int(score))
    return enter()


def pick_player():
    players = api.player.get_players()
    options: list[Option] = [
        (
            [
                # player["icon"],
                "🙎",
                player["name"],
                f"{Icons.LEVEL} {Formatter.level(player['level'])}",
                f"{Icons.STATS} [bold]{player['score']}[/]",
            ],
            partial(view_player_stats, player["id"]),
        )
        for player in players
    ]
    options.append((["", "Exit"], enter))
    return PickArgs(
        message="Select a player to view stats:",
        options=options,
    )


def view_player_stats(player_id: str):
    _player = api.player.get_player(player_id)
    _player["icon"] = "🙎"
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    for key, value in _player["stats"].items():
        if key in ("id", "player_id"):
            continue
        if key in ("created_dt", "updated_dt"):
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d %b %Y")
        else:
            value = float(value)
            value = (
                f"{value:,.0f}" if isinstance(value, int) or value.is_integer() else f"{value:,.2f}"
            )
        table.add_row(
            normalize_title(key),
            Text.from_markup(value, justify="right"),
        )
    return PickArgs(
        message=f"{_player['icon']} {_player['name']}\n",
        options=[("Nice!", enter)],
        subtitle=table,
    )


# This is the same function as in the time machine. I haven't figured
# out a great place where they can share this function and I don't
# want to cross import
def get_total_value() -> int:
    return player.total_value + facility.total_value + garden.total_value


def unimplemented():
    return PickArgs(
        message="This has not been implemented yet.",
        options=[("Bummer!", enter)],
    )
