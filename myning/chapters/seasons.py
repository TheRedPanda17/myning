from myning.api_v2 import MyningClient
from myning.chapters import AsyncArgs, Option, PickArgs, main_menu


async def enter():
    client = MyningClient()

    # Fetch saves
    seasons = await client.fetch(f"/users/{client.user_id}/seasons")

    # If no save, create save and refetch
    if not seasons:
        await client.fetch(
            f"users/{client.user_id}/seasons",
            "POST",
            json={
                "season_id": 1,
                "user_id": client.user_id,
            },
        )
        seasons = await client.fetch(f"/users/{client.user_id}/seasons")

    options = [
        Option(season["name"], lambda: AsyncArgs(lambda: select_season(season)))
        for season in seasons
    ]
    options.append(Option("Join another season", lambda: AsyncArgs(join_seasons)))
    options.append(Option("Go Back", main_menu.enter))
    return PickArgs(message="Select a season", options=options)


async def select_season(season: dict):
    pass


async def join_seasons():
    pass
