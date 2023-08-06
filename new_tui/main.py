from myning.objects.game import Game
from myning.objects.garden import Garden
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager


def main():
    FileManager.setup()
    Player.initialize()
    ResearchFacility.initialize()
    ResearchFacility().check_in()
    Garden.initialize()
    Game.initialize()
    Trip.initialize()
    Settings.initialize()

    from new_tui.view.app import MyningApp

    MyningApp().run()
    # print("Game saved. Thank you for playing Myning!")
    print("Game was not saved because we are still in dev. Thank you for playing Myning!")


if __name__ == "__main__":
    main()
