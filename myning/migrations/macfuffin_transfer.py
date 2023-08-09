import json

from myning.objects.macguffin import Macguffin
from myning.utils.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        data = json.load(f)
        if "macguffin" in data:
            mac_data = data["macguffin"]

            potential = 1 + mac_data["exp_boost"] / 5

            mac_data["research_boost"] = potential
            mac_data["soul_credit_boost"] = potential
            macguffin = Macguffin.from_dict(mac_data)
        else:
            macguffin = Macguffin()
        FileManager.save(macguffin)

        print("\nJust doing some back-end maintainance.")
