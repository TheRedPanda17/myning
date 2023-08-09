from myning.migrations.migrate import check_for_migrations
from myning.objects.game import Game
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.research_facility import ResearchFacility
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.git_interactions import check_for_updates


def main():
    check_for_updates()
    check_for_migrations()

    FileManager.setup()
    Player.initialize()
    ResearchFacility.initialize()
    Garden.initialize()
    Game.initialize()
    Trip.initialize()
    Macguffin.initialize()
    Settings.initialize()

    try:
        Game.play()
    except KeyboardInterrupt:
        FileManager.save(Game())
        FileManager.save(Player())
        FileManager.save(Trip())
        print("Game saved. Thank you for playing Myning!")
