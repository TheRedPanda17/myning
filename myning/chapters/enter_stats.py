from blessed import Terminal
from requests import HTTPError

from myning import api
from myning.objects.character import SpeciesEmoji
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.stats import Stats
from myning.utils.io import pick
from myning.utils.ui import columnate, normalize_title
from myning.utils.ui_consts import Colors, Icons

term = Terminal()


def play():
    stats = Stats()
    macguffin = Macguffin()

    while True:
        option, _ = pick(
            ["Sync Stats", "View Stats", "Go Back"],
            stats.display,
        )

        try:
            if option == "Go Back":
                return
            elif option == "View Stats":
                view_stats()
            elif option == "Sync Stats":
                score = macguffin.get_new_standard_boost(get_total_value())
                api.player.sync(score)
            else:
                pick(["Bummer!"], "This has not been implmented yet.")
        except HTTPError as e:
            pick(["Bummer!"], f"Error contacting the API: {e.response.status_code}")


def view_stats():
    players = api.player.get_players()

    while True:
        options = columnate(
            [
                [
                    SpeciesEmoji(player["icon"]),
                    player["name"],
                    f"{Icons.LEVEL} {Colors.LEVEL}{player['level']}{term.normal}",
                    f" {Icons.STATS} {term.bold}{player['score']}{term.normal}",
                ]
                for player in players
            ]
        )
        options.append("Go Back")

        option, i = pick(options)

        if option == "Go Back":
            return

        view_stat(players[i]["id"])


def view_stat(id: str):
    player = api.player.get_player(id)
    ignored = ["id", "player_id"]

    columns = []

    for key, value in player["stats"].items():
        if key in ignored:
            continue
        title = f"  {term.bold(normalize_title(key))}"
        stat = f"{term.white(f'{value}')}"
        columns.append([title, stat])

    s = term.bold("Stats\n\n")
    s += "\n".join(columnate(columns))

    pick(["Nice!"], s)


# This is the same function as in the time machine. I haven't figured
# out a great place where they can share this function and I don't
# want to cross import
def get_total_value() -> int:
    player = Player()
    facility = ResearchFacility()
    garden = Garden()

    return player.total_value + facility.total_value + garden.total_value
