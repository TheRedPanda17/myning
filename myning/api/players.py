from myning.api import API_CONFIG, fetch
from myning.objects.player import Player
from myning.objects.stats import Stats

player = Player()
stats = Stats()

BASE_PLAYERS_URL = f"{API_CONFIG['base_url']}/players"


async def sync(score: int):
    headers = {"Authorization": API_CONFIG["auth"]}
    payload = {
        "name": player.name,
        "level": player.level,
        "stats": stats.all_stats,
        "icon": player.icon,
        "id": player.id,
        "score": score,
    }
    exists = await get_player(player.id)
    if exists:
        await fetch(
            f"{BASE_PLAYERS_URL}/{player.id}",
            method="PATCH",
            headers=headers,
            json=payload,
        )
    else:
        await fetch(BASE_PLAYERS_URL, method="POST", headers=headers, json=payload)


async def get_players():
    result = await fetch(BASE_PLAYERS_URL)
    return sorted(result["data"], key=lambda p: p["score"], reverse=True)


async def get_player(player_id: str):
    return await fetch(f"{BASE_PLAYERS_URL}/{player_id}")
