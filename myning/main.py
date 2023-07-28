from myning.objects.game import Game
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.git_interactions import check_for_updates


def main():
    check_for_updates()

    FileManager.setup()
    Player.initialize()
    Game.initialize()
    Trip.initialize()
    Settings.initialize()

    try:
        Game.play()
    except KeyboardInterrupt:
        FileManager.save(Game())
        FileManager.save(Player())
        FileManager.save(Trip())
        print("Game saved. Thank you for playing Myning!")
