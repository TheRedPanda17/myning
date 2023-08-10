import math
from itertools import zip_longest
from time import sleep

from blessed import Terminal

term = Terminal()


def get_gold_string(gold: int):
    return term.gold(f"{gold}g")


def get_water_string(water: int):
    return term.skyblue1(f"{water} water")


def get_level_string(level: int):
    return term.cyan(f"lvl {level}")


def get_soul_string(count: float):
    return term.blue(f"{round(count, 2)} soul credits")


def get_research_string(points: float):
    return term.violetred1(f"{round(points, 2)} research points")


def get_locked_str(string: str):
    return term.snow4(string)


def get_exp_string(exp: int):
    return term.magenta(f"{exp} exp")


def normalize_title(key: str) -> str:
    return key.replace("_", " ").title()


def get_health_bar(health: int, max_health: int, bar_count: int = 11):
    health_fraction = health / max_health if max_health else 0
    green_count = math.ceil(health_fraction * bar_count)
    health_fraction_str = f"{health}/{max_health}".center(bar_count)
    return "".join(
        f"[grey0 on green]{char}[/]" if i < green_count else f"[on red]{char}[/]"
        for i, char in enumerate(health_fraction_str)
    )


def get_progress_bar(progress: int, total: int, bar_count: int = 11):
    fraction = progress / total
    green_count = math.ceil(fraction * bar_count)

    s = "".join(
        term.blue("█") if i < green_count else term.white("█") for i in range(bar_count - 1)
    )

    s += term.white("█") if progress < total else term.blue("█")
    return s


def columnate(items: list[list[str]], *, sep: str = " "):
    """
    Print a table of items formatted in columns.

    Arguments:
    items -- A list of lists of strings. Each sublist is a row.

    Keyword arguments:
    sep -- The string to use as a column separator.

    Example:
    ```python
    columnate([
        ["a", "b", "c"],
        ["dd", "eee", "ff"],
    ], sep=" | ")
    ```

    Output:
    a  | b   | c
    dd | eee | ff
    """

    widths = [
        max(map(len if "Emoji" in col[0].__class__.__name__ else term.length, col))
        for col in zip_longest(*items)
    ]
    return [
        sep.join([term.ljust(item, width) for item, width in zip(row, widths)]) for row in items
    ]
