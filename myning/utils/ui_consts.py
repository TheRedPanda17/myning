from enum import Enum

from blessed import Terminal

term = Terminal()


class Colors(str, Enum):
    GOLD = term.gold + term.bold
    WEAPON = term.crimson + term.bold
    ARMOR = term.dodgerblue + term.bold
    LEVEL = term.cyan + term.bold
    EXP = term.magenta + term.bold
    PLANT = term.green + term.bold


class Icons(str, Enum):
    ARMOR = "🛡 "
    ARMORY = "🛡 "
    BARRACKS = "⛺️"
    BLACKSMITH = "🔨"
    DAMAGE = "⚔️ "
    DEATH = "💀"
    DONE = "✅"
    EXIT = "↵ "
    GARDEN = "🪴"
    GOLD = "💰"
    GRAVEYARD = "🪦"
    HEALER = "🌿"
    HELMET = "🪖"
    JOURNAL = "📜"
    LEVEL = "📊"
    LOCKED = "🔒 "
    MINE = "⛏ "
    MINERAL = "🪨"
    PANTS = "👖"
    PICKAXE = "⛏ "
    PLANT = "🌱"
    RESEARCH_FACILITY = "🔬"
    RESEARCH_POINTS = "🧪"
    RESOURCE = "💎"
    SETTINGS = "🔧"
    SHIRT = "🥼"
    SHOES = "🥾"
    SOUL_CREDITS = "🪙"
    STORE = "💰"
    SWORD = "🗡️ "
    TIME = "⏳"
    TIME_MACHINE = "⏳"
    UNKNOWN = "❓"
    VICTORY = "🚩"
    WEAPON = "⚔️ "
    WIZARD = "🔮"
    WIZARD_HUT = "🔮"
    XP = "✨"
