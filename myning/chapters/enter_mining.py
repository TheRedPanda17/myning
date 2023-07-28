import random
import threading
from time import sleep

from blessed import Terminal

from myning.config import CONFIG
from myning.objects.mine_game import MineGame
from myning.objects.settings import Settings
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_mineral, generate_mineral_exact
from myning.utils.user_input import slow_print, timed_input
from myning.utils.utils import get_random_array_item, get_random_int

term = Terminal()

TIMEOUT = 5
DISABLED_INTERVAL = 1 / 2


def play():
    print_thread = PrintThread()
    input_thread = InputThread()
    print_thread.brother = input_thread
    input_thread.brother = print_thread
    print_thread.daemon = True
    input_thread.daemon = True
    input_thread.start()
    print_thread.start()
    input_thread.join()
    print_thread.join()


# TODO: Abstract this into some sort of thread manager so
# we don't have threads referencing each other
# It would also make multithreading in the other
# modules easier
class PrintThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.trip = Trip()
        self.settings = Settings()
        self.minutes = self.trip.seconds_left / 60
        self.wait = random.randint(0, int(CONFIG["tick_length"] + self.minutes)) + 5
        self.total_ticks = self.wait

        self.mined = False

    def add_brother(self, brother):
        self.brother = brother

    def stop(self):
        self.mined = True

    def run(self):
        spf = get_random_int(25, 35)
        spf = spf / 1000
        size = get_random_array_item([15, 20, 25])
        mine_game = MineGame(size)
        trip_str = self.trip.summary  # So we don't keep recalculating

        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            last_count = int(self.wait) + 1

            while self.wait > 0 and not self.mined:
                if self.settings.mini_games_disabled:
                    print(term.clear, end="")
                    print(trip_str)
                    print()
                    print(f"Mining... ({int(self.wait)} seconds left)\n")
                    print("💎   " * (4 - int(self.wait) % 5))

                    sleep(DISABLED_INTERVAL)
                    self.wait -= DISABLED_INTERVAL
                else:
                    if last_count - int(self.wait) >= 1:
                        print(term.clear, end="")
                        print(trip_str)
                        print()
                        print(f"Mining... ({int(self.wait)} seconds left)")
                        print("Press enter to strike the rocks...\n")
                        print(mine_game.bar_str)
                        last_count = int(self.wait)
                    print(mine_game.arrow_str)
                    print(term.move_up(2))
                    mine_game.move_cursor()
                    sleep(spf)
                    self.wait -= spf

        mine = self.trip.mine
        if self.mined and not self.settings.mini_games_disabled:
            item_level = int(mine.max_item_level * mine_game.score / 100)
            mineral = generate_mineral_exact(item_level, mineral=mine.resource)
        else:
            mineral = generate_mineral(mine.max_item_level, mineral=mine.resource)

        self.brother.stop()
        sleep(1)  # needed to make sure the other thread is done printing
        self.trip.add_item(mineral)
        self.trip.tick_passed(self.total_ticks)
        slow_print(mineral.get_new_text())
        FileManager.multi_save(mineral, self.trip)


class InputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.done = False

    def stop(self):
        self.done = True

    def add_brother(self, brother):
        self.brother = brother

    def run(self):
        while not self.done:
            _, timed_out = timed_input(timeout=1)
            print(term.move_up(1))
            if not timed_out:
                self.brother.stop()
