from myning.config import UPGRADES
from myning.objects.player import Player
from myning.utilities.file_manager import FileManager


def run():
    player = Player()
    if player.has_upgrade("buy_full_set"):
        upgrade = UPGRADES["buy_full_set"]
        upgrade.level = 5
        FileManager.save(player)
    print("\nUpdating your blacksmith upgrades")
