import json

from myning.objects.garden import Garden
from myning.utils.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        data = json.load(f)
        if "garden" in data:
            garden = Garden.from_dict(data["garden"])
        else:
            garden = Garden(1)
        FileManager.save(garden)

        print("\nJust doing some back-end maintainance.")
