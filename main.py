import builtins

import rich

from myning.migrations.migrate import check_for_migrations
from myning.objects.game import Game
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.objects.stats import Stats
from myning.objects.trip import Trip
from myning.utilities.file_manager import FileManager
from myning.utilities.git import check_for_updates


def main():
    # Use rich print for any initialization
    ogprint = builtins.print
    builtins.print = rich.print

    check_for_updates()
    check_for_migrations()

    FileManager.setup()
    Player.initialize()

    Game.initialize()
    Garden.initialize()
    Macguffin.initialize()
    ResearchFacility.initialize()
    Settings.initialize()
    Stats.initialize()
    Trip.initialize()

    # This ensures new players have the new migrations. Preferably, we'd loop through the
    # MIGRATIONS, but we have a circular dependency if we do, so this is the hack right now.
    Player().completed_migrations = [1, 2, 3, 4, 5, 6, 7, 8]

    # Restore builtin print before starting tui
    builtins.print = ogprint

    # Load tui after importing and initializing objects to allow global references
    from myning.tui.app import MyningApp  # pylint: disable=import-outside-toplevel

    MyningApp().run()
    FileManager.multi_save(
        Game(),
        Garden(),
        Macguffin(),
        Player(),
        ResearchFacility(),
        Settings(),
        Stats(),
        Trip(),
    )
    print("Game saved. Thank you for playing Myning!")


if __name__ == "__main__":
    main()