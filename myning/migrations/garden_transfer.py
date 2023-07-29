import json
from myning.objects.garden import Garden
from myning.utils.file_manager import FileManager


def run():
    Garden.initialize()

    with open(".data/player.json") as f:
        data = json.load(f)
        garden = Garden.from_dict(data["garden"])

        FileManager.save(garden)

        print("\nJust doing some back-end maintainance.")
