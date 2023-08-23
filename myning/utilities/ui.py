import math
from enum import Enum


class Icons(str, Enum):
    ARMOR = "🛡 "
    ARMORY = "🛡"
    BARRACKS = "⛺️"
    BLACKSMITH = "🔨"
    CRIT = "🩸"
    DAMAGE = "⚔️ "
    DEATH = "💀"
    DODGE = "🍃"
    DONE = "✅"
    EXIT = "❌"
    GARDEN = "🪴"
    GOLD = "💰"
    GRAVEYARD = "🪦"
    HEALER = "🌿"
    HEART = "❤️"
    HELMET = "🪖"
    JOURNAL = "📜"
    LEVEL = "📊"
    LOCKED = "🔒"
    MINE = "⛏️"
    MINERAL = "🪨"
    PANTS = "👖"
    PLANT = "🌱"
    RESEARCH_FACILITY = "🔬"
    RESEARCH_POINTS = "🧪"
    RESOURCE = "💎"
    SETTINGS = "🔧"
    SHIRT = "🥼"
    SHOES = "🥾"
    SOUL_CREDITS = "🪙"
    STATS = "📈"
    STORE = "💰"
    SWORD = "⚔️"
    TELESCOPE = "🔭"
    TIME = "⏳"
    TIME_MACHINE = "⏳"
    UNKNOWN = "❓"
    VICTORY = "🚩"
    WARNING = "⚠️"
    WEAPON = "⚔️ "
    WIZARD = "🔮"
    WIZARD_HUT = "🔮"
    XP = "✨"


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


def get_health_bar(health: int, max_health: int, bar_count: int = 11):
    health_fraction = health / max_health if max_health else 0
    green_count = math.ceil(health_fraction * bar_count)
    health_fraction_str = f"{health}/{max_health}".center(bar_count)
    return "".join(
        f"[grey0 on green]{char}[/]" if i < green_count else f"[on red]{char}[/]"
        for i, char in enumerate(health_fraction_str)
    )
