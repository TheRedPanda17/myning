import json

from myning.objects.inventory import Inventory
from myning.utilities.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        data = json.load(f)
        if "inventory" in data:
            inventory = Inventory.from_dict(data["inventory"])
        else:
            inventory = Inventory()

        FileManager.save(inventory)

        print("\nJust doing some back-end maintenance.")
