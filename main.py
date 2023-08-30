import builtins

import rich

from myning.migrations.migrate import check_for_migrations
from myning.objects.game import Game
from myning.objects.garden import Garden
from myning.objects.graveyard import Graveyard
from myning.objects.inventory import Inventory
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
    Graveyard.initialize()
    Inventory.initialize()
    Macguffin.initialize()
    ResearchFacility.initialize()
    Settings.initialize()
    Stats.initialize()
    Trip.initialize()

    # import MIGRATIONS here to resolve circular dependencies
    from myning.migrations import MIGRATIONS  # pylint: disable=import-outside-toplevel

    Player().completed_migrations = list(MIGRATIONS.keys())

    # Restore builtin print before starting tui
    builtins.print = ogprint

    # Load tui after importing and initializing objects to allow global references
    from myning.tui.app import MyningApp  # pylint: disable=import-outside-toplevel

    MyningApp().run()
    FileManager.multi_save(
        Game(),
        Garden(),
        Graveyard(),
        Inventory(),
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
