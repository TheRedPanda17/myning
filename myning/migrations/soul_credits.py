from myning.chapters.enter_graveyard import soul_cost
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.ui import get_soul_string
from myning.utils.utils import fibonacci


def run():
    player = Player()

    spent_credits = 0
    for i in range(0, player.ghost_count):
        spent_credits += int(fibonacci(i + 1))

    print(f"\nYou've spent {get_soul_string(spent_credits)}.")

    new_cost = 0
    for i in range(0, player.ghost_count):
        new_cost += int(soul_cost(i + 1))

    print(f"\nNew cost is {get_soul_string(new_cost)}.")

    returned = spent_credits - new_cost
    if returned > 0:
        print(f"\nYou've been returned {get_soul_string(returned)}.")
        player.soul_credits += returned
        FileManager.save(player)
    elif returned == 0:
        print(f"\nYou broke even!")
    else:
        print("\nYou actually came out ahead before, so we'll give you a pass.")

    print("\nHave fun myning!")
