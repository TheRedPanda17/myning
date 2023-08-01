import os

from myning.migrations import MIGRATIONS
from myning.objects.player import Player
from myning.utils.file_manager import FileManager


def check_for_migrations():
    if not os.path.exists(".data"):
        return

    Player.initialize()
    player = Player()

    latest_migration = player.completed_migrations[-1]
    while latest_migration != list(MIGRATIONS.keys())[-1]:
        latest_migration = latest_migration + 1
        MIGRATIONS[latest_migration].run()
        player.completed_migrations.append(latest_migration)

        input(f"\nMIGRATION {latest_migration} RAN (Enter to continue)")

    FileManager.save(player)
