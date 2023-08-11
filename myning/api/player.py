import requests

from myning.api.api import API_CONFIG
from myning.objects.player import Player
from myning.objects.stats import Stats
from myning.utils.file_manager import FileManager


def sync():
    player = Player()
    stats = Stats()
    url = API_CONFIG["base_url"] + "/players"
    headers = {"Authorization": API_CONFIG["auth"]}

    payload = {
        "name": player.name,
        "level": player.level,
        "stats": stats.all_stats,
        "icon": player.icon.symbol,
        "id": player.id,
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    FileManager.save(player)


def get_players():
    url = API_CONFIG["base_url"] + "/players"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return data["data"]


def get_player(id: str):
    url = API_CONFIG["base_url"] + f"/players/{id}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return data
