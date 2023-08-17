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
    def gold(gold: int):
        return f"[{Colors.GOLD}]{gold}g[/]"

    @staticmethod
    def soul_credits(soul_credits: int):
        return f"[{Colors.SOUL_CREDITS}]{soul_credits} soul credits[/]"

    @staticmethod
    def research_points(research_points: int):
        return f"[{Colors.RESEARCH_POINTS}]{research_points} research points[/]"

    @staticmethod
    def level(lvl: int):
        return f"[{Colors.LEVEL}]{lvl}[/]"

    @staticmethod
    def locked(s: str):
        return f"[{Colors.LOCKED}]{s}[/]"
