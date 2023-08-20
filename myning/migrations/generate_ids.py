import json
import uuid

from myning.objects.player import Player
from myning.utilities.file_manager import FileManager


def run():
    with open(".data/player.json") as f:
        player = Player()
        player.id = str(uuid.uuid4())

        FileManager.save(player)
        print("\nMigrating ids to use UUID.")
