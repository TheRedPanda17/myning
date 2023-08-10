import json

from myning.objects.macguffin import Macguffin
from myning.objects.stats import Stats
from myning.utils.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        player_data = json.load(f)

        stats = Stats(integer_stats={"trips_finished": player_data["total_trips"]})
        FileManager.save(stats)

        print("\nMoving some stats into the new Stats Object.")
