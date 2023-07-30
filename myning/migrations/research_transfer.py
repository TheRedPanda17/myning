import json
from myning.objects.research_facility import ResearchFacility

from myning.utils.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        data = json.load(f)
        facility_data = data["research_facility"]
        facility_data["research"] = data["research"]

        facility = ResearchFacility.from_dict(facility_data)
        FileManager.save(facility)

        print("\nJust doing some back-end maintainance.")
