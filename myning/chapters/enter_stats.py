from blessed import Terminal
from requests import HTTPError

from myning import api
from myning.objects.character import SpeciesEmoji
from myning.objects.stats import Stats
from myning.utils.io import pick
from myning.utils.ui import columnate, normalize_title
from myning.utils.ui_consts import Colors, Icons

term = Terminal()


def play():
    stats = Stats()

    while True:
        option, _ = pick(
            ["Sync Stats", "View Stats", "Exit"],
            stats.display,
        )

        try:
            if option == "Exit":
                return
            elif option == "View Stats":
                view_stats()
            elif option == "Sync Stats":
                api.player.sync()
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
                ]
                for player in players
            ]
        )
        options.append("Exit")

        option, i = pick(options)

        if option == "Exit":
            return

        view_stat(players[i - 1]["id"])


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
