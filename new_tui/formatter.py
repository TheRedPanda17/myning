from itertools import zip_longest

from rich.text import Text

from myning.utils.ui_consts import Icons


def columnate(items: list[list[str]], *, sep=" ") -> list[Text]:
    widths = []
    for col in zip_longest(*items):
        max_width = 0
        for cell in col:
            width = 1 if isinstance(cell, Icons) else len(Text.from_markup(cell))
            if width > max_width:
                max_width = width
        widths.append(max_width)
    rows = []
    for row in items:
        texts = []
        for item, width in zip(row, widths):
            text = Text.from_markup(item)
            text.truncate(width + 1, pad=True)
            texts.append(text)
        rows.append(Text(sep).join(texts))
    return rows


class Colors:
    ARMOR = "dodger_blue1"
    GOLD = "gold1"
    LEVEL = "cyan1"
    PLANT = "green1"
    RESEARCH_POINTS = "deep_pink3"
    SOUL_CREDITS = "slate_blue3"
    WEAPON = "red1"
    XP = "magenta1"


class Formatter:
    @staticmethod
    def gold(gold: int):
        return f"[{Colors.GOLD}]{gold}g[/]"

    @staticmethod
    def soul_credits(soul_credits: int):
        return f"[{Colors.SOUL_CREDITS}]{soul_credits} soul credits[/]"

    @staticmethod
    def research_points(research_points: int):
        return f"[{Colors.RESEARCH_POINTS}]{research_points} research points[/]"

    @staticmethod
    def xp(xp: int):
        return f"[{Colors.XP}]{xp} xp[/]"
