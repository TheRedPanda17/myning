import requests

from myning.api.api import API_CONFIG
from myning.objects.player import Player
from myning.objects.stats import Stats
from myning.utils.file_manager import FileManager


def sync(score: int):
    player = Player()
    stats = Stats()

    url = API_CONFIG["base_url"] + "/players"
    headers = {"Authorization": API_CONFIG["auth"]}
    try:
        current = get_player(player.id)
        if current:
            exists = True
    except requests.HTTPError:
        exists = False

    payload = {
        "name": player.name,
        "level": player.level,
        "stats": stats.all_stats,
        "icon": player.icon.symbol,
        "id": player.id,
        "score": score * 100,
    }

    # Convert object to array needed by the API.
    mine_stats_payload = [{"name": key, **value} for key, value in player.mine_progressions.items()]

    if exists:
        url += f"/{player.id}"
        response = requests.patch(url, json=payload, headers=headers)
        minestats_response = requests.patch(url + "/mine_stats", json=mine_stats_payload, headers=headers)
    else:
        response = requests.post(url, json=payload, headers=headers)
        # This is a dependent query, the player has to exist first.
        # If these calls happen in sequence (i.e., response ^ completes first), then it should be fine.
        minestats_response = requests.patch(url + "/" + player.id + "/mine_stats", json=mine_stats_payload, headers=headers)

    minestats_response.raise_for_status()
    response.raise_for_status()


def get_players():
    url = API_CONFIG["base_url"] + "/players"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return sorted(data["data"], key=lambda p: p["score"], reverse=True)


def get_player(id: str):
    url = API_CONFIG["base_url"] + f"/players/{id}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return data
