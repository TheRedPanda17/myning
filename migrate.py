import sys

from myning.migrations import MIGRATIONS
from myning.objects.player import Player
from myning.utils.file_manager import FileManager


def migrate(id: int):
    Player.initialize()
    player = Player()

    if not id:
        id = player.completed_migrations[-1] + 1
    else:
        try:
            id = int(id)
        except ValueError:
            sys.exit("That's not a valid migration id")

    if id in player.completed_migrations:
        sys.exit(f"You already ran migration {id}")

    if id not in MIGRATIONS.keys():
        sys.exit(f"{id} is not a valid migration id")

    MIGRATIONS[id].run()
    player = Player()
    player.completed_migrations.append(id)
    FileManager.save(player)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        migrate(0)
    else:
        migrate(sys.argv[1])
