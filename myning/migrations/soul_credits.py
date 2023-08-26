from myning.objects.player import Player
from myning.utilities.fib import fibonacci
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter


def run():
    Player.initialize()
    player = Player()

    spent_credits = sum(int(fibonacci(i + 1)) for i in range(player.ghost_count))
    print(f"\nYou've spent {Formatter.soul_credits(spent_credits)}.")

    new_cost = sum(int((i + 1) * 1.1) for i in range(player.ghost_count))
    print(f"\nNew cost is {Formatter.soul_credits(new_cost)}.")

    returned = spent_credits - new_cost
    if returned > 0:
        print(f"\nYou've been returned {Formatter.soul_credits(returned)}.")
        player.soul_credits += returned
        FileManager.save(player)
    elif returned == 0:
        print("\nYou broke even!")
    else:
        print("\nYou actually came out ahead before, so we'll give you a pass.")

    print("\nHave fun myning!")


if __name__ == "__main__":
    run()
