from myning.objects.game import Game
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager


def main():
    # check_for_updates()
    # check_for_migrations()

    FileManager.setup()
    Player.initialize()

    Game.initialize()
    Garden.initialize()
    Macguffin.initialize()
    ResearchFacility.initialize()
    Settings.initialize()
    Trip.initialize()

    # This ensures new players have the new migrations. Preferably, we'd loop through the
    # MIGRATIONS, but we have a circular dependency if we do, so this is the hack right now.
    Player().completed_migrations = [1, 2, 3, 4, 5, 6, 7, 8]

    # Load tui after importing and initializing objects to allow global references
    from new_tui.view.app import MyningApp  # pylint: disable=import-outside-toplevel

    MyningApp().run()
    FileManager.multi_save(
        Game(),
        Garden(),
        Macguffin(),
        Player(),
        ResearchFacility(),
        Settings(),
        Trip(),
    )
    print("Game saved. Thank you for playing Myning!")


if __name__ == "__main__":
    main()
