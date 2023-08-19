from enum import Enum


class Emoji(str):
    pass


class Colors(str, Enum):
    ARMOR = "dodger_blue1"
    GOLD = "gold1"
    LEVEL = "cyan1"
    LOCKED = "grey53"
    PLANT = "green1"
    RESEARCH_POINTS = "deep_pink3"
    SOUL_CREDITS = "light_slate_blue"
    WEAPON = "red1"
    XP = "magenta1"


class Formatter:
    @staticmethod
    def gold(g: int):
        return f"[{Colors.GOLD}]{g:,}g[/]"

    @staticmethod
    def soul_credits(sc: float):
        return f"[{Colors.SOUL_CREDITS}]{sc:.2f} soul credits[/]"

    @staticmethod
    def research_points(rp: float):
        return f"[{Colors.RESEARCH_POINTS}]{rp:.2f} research points[/]"

    @staticmethod
    def level(lvl: int):
        return f"[{Colors.LEVEL}]{lvl}[/]"

    @staticmethod
    def locked(s: str):
        return f"[{Colors.LOCKED}]{s}[/]"

    @staticmethod
    def water(w: int):
        return f"[sky_blue1]{w} water[/]"

    @staticmethod
    def percentage(p: float):
        p *= 100
        return f"{p:.0f}%" if p.is_integer else f"{p:.2f}%"
