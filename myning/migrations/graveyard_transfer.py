import json

from myning.objects.graveyard import Graveyard
from myning.utilities.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        data = json.load(f)
        if "soul_credits" in data or "fallen_allies" in data:
            migration_dict = {
                "soul_credits": data.get("soul_credits", 0),
                "fallen_allies": data.get("fallen_allies", []),
            }
            graveyard = Graveyard.from_dict(migration_dict)
        else:
            graveyard = Graveyard()

        FileManager.save(graveyard)

        print("\nJust doing some back-end maintainance.")
