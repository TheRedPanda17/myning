import select
import sys
from typing import Tuple

from myning.utils.io import pick


def get_idle_time(player_level, msg, sub_title):
    minutes = [
        int(player_level * 0.5) if player_level > 1 else 1,
        player_level * 1,
        player_level * 2,
        player_level * 4,
        player_level * 8,
    ]
    minute_strings = [f"{minute} minutes" for minute in minutes] + ["Go Back"]

    _, index = pick(minute_strings, msg, sub_title=sub_title)

    return minutes[index] if index < len(minutes) else 0


def timed_input(timeout: int) -> Tuple[str, bool]:
    # select will let us know when stdin is ready for reading
    read_ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if read_ready:
        return sys.stdin.readline().strip(), False
    else:
        return "", True


def slow_print(s):
    print()
    print(s)
    timed_input(timeout=1)
