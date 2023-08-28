from myning.utilities.ui import Colors


class Formatter:
    @staticmethod
    def gold(g: int):
        return f"[{Colors.GOLD}]{g:,}g[/]"

    @staticmethod
    def xp(x: int):
        return f"[{Colors.XP}]{x} xp[/]"

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

    @staticmethod
    def title(t: str):
        return t.replace("_", " ").title()

    @staticmethod
    def keybind(k: str):
        return f"[bold dodger_blue1]{k}[/bold]"
