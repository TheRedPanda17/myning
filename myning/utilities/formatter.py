from myning.utilities.ui import Colors


class Formatter:
    @staticmethod
    def gold(g: int):
        return Colors.GOLD(f"{g:,}g")

    @staticmethod
    def xp(x: int):
        return Colors.XP(f"{x} xp")

    @staticmethod
    def soul_credits(sc: float):
        return Colors.SOUL_CREDITS(f"{sc:.2f} soul credits")

    @staticmethod
    def research_points(rp: float):
        return Colors.RESEARCH_POINTS(f"{rp:.2f} research points")

    @staticmethod
    def level(lvl: int):
        return Colors.LEVEL(lvl)

    @staticmethod
    def locked(s: str):
        return Colors.LOCKED(s)

    @staticmethod
    def water(w: int):
        return Colors.WATER(f"{w} water")

    @staticmethod
    def percentage(p: float):
        p *= 100
        return f"{p:.0f}%" if p.is_integer else f"{p:.2f}%"

    @staticmethod
    def title(t: str):
        return t.replace("_", " ").title()

    @staticmethod
    def keybind(k: str):
        return f"[bold dodger_blue1]{k}[/]"
