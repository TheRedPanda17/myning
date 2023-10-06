from datetime import datetime
from functools import partial
from typing import TYPE_CHECKING

from rich.table import Table
from rich.text import Text

from myning import api
from myning.chapters import AsyncArgs, Option, PickArgs, api_request, main_menu
from myning.objects.garden import Garden
from myning.objects.inventory import Inventory
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.stats import Stats
from myning.utilities.formatter import Formatter
from myning.utilities.ui import Icons

if TYPE_CHECKING:
    from myning.tui.chapter import ChapterWidget

facility = ResearchFacility()
garden = Garden()
macguffin = Macguffin()
player = Player()
stats = Stats()
inventory = Inventory()


def enter():
    return PickArgs(
        message="Your Stats\n",
        options=[
            Option("Sync Stats", lambda: AsyncArgs(callback=sync)),
            Option("View Highscores", lambda: AsyncArgs(callback=view_players)),
            Option("Go Back", main_menu.enter),
        ],
        subtitle=stats.display,
    )


@api_request("Syncing Stats...", callback=enter)
async def sync(chapter: "ChapterWidget"):
    score = macguffin.get_new_standard_boost(get_total_value())
    await api.players.sync(int(score * 100))
    chapter.pick(
        PickArgs(
            message="Succesfully synced stats!",
            options=[Option("Top that, fellow miners!", enter)],
        )
    )


@api_request("Fetching Highscores...", callback=enter)
async def view_players(chapter: "ChapterWidget"):
    players = await api.players.get_players()
    # TODO remove next 3 lines when everyone has migrated to tui single-point species emojis
    for p in players:
        if p["icon"] == "👨🏾‍🌾":
            p["icon"] = "🙎"
    options = [
        Option(
            [
                player["icon"],
                player["name"],
                Formatter.level(player["level"]),
                Text.from_markup(f"[bold]{player['score']:,}[/]", justify="right"),
            ],
            partial(view_player, player),
        )
        for player in players
    ]
    options.append(Option(["", "Exit"], enter))
    chapter.pick(
        PickArgs(
            message="Select a player to view stats:",
            options=options,
            column_titles=[
                "",
                "Name",
                Text(Icons.LEVEL, justify="center"),
                Text(Icons.STATS, justify="center"),
            ],
        )
    )


def view_player(_player):
    @api_request(f"Fetching Stats for {_player['icon']} {_player['name']}...", callback=enter)
    async def callback(chapter: "ChapterWidget"):
        p = await api.players.get_player(_player["id"])
        # TODO remove next 2 lines when everyone has migrated to tui single-point species emojis
        if p["icon"] == "👨🏾‍🌾":
            p["icon"] = "🙎"
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        for key, value in p["stats"].items():
            if key in ("id", "player_id"):
                continue
            if key in ("created_dt", "updated_dt"):
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d %b %Y")
            else:
                value = float(value)
                value = (
                    f"{value:,.0f}"
                    if isinstance(value, int) or value.is_integer()
                    else f"{value:,.2f}"
                )
            table.add_row(
                Formatter.title(key),
                Text.from_markup(value, justify="right"),
            )
        chapter.pick(
            PickArgs(
                message=f"{p['icon']} {p['name']}\n",
                options=[Option("Nice!", enter)],
                subtitle=table,
            )
        )

    return AsyncArgs(callback=callback)


# This is the same function as in the time machine. I haven't figured out a great place where they
# can share this function and I don't want to cross import
def get_total_value() -> int:
    return player.total_value + facility.total_value + garden.total_value + inventory.total_value
