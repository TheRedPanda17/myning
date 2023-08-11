from enum import Enum

from blessed import Terminal

from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.ui import columnate, normalize_title

term = Terminal()


class IntegerStatKeys(str, Enum):
    TRIPS_FINISHED = "trips_finished"
    ARMY_DEFEATS = "army_defeats"
    BATTLES_WON = "battles_won"
    ENEMIES_DEFEATED = "enemies_defeated"
    MINERALS_MINED = "minerals_mined"
    PLANTS_HARVESTED = "plants_harvested"
    WEAPONS_PURCHASED = "weapons_purchased"
    ARMOR_PURCHASED = "armor_purchased"
    GOLD_EARNED = "gold_earned"

    # Need implementation
    GOLD_SPENT_ON_GEAR = "gold_spent_on_gear"
    TAXES_PAID = "taxes_paid"
    SOILED_PLANTS = "soiled_plants"


class FloatStatKeys(str, Enum):
    SOUL_CREDITS_EARNED = "soul_credits_earned"


class Stats(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        stats = FileManager.load(Stats, cls.file_name)
        if not stats:
            stats = cls()
        cls._instance = stats

    @classmethod
    @property
    def file_name(cls):
        return "stats"

    def __init__(self, integer_stats: dict = {}, float_stats: dict = {}):
        self.integer_stats = integer_stats
        self.float_stats = float_stats

    @classmethod
    def from_dict(cls, data: dict) -> "Stats":
        if data is None:
            return Stats()
        return Stats(data["integer_stats"], data.get("float_stats", {}))

    @property
    def all_stats(self):
        return {**self.integer_stats, **self.float_stats}

    @property
    def display(self):
        columns = []
        for key, value in self.all_stats.items():
            title = f"  {term.bold(normalize_title(key))}"
            stat = f"{term.white(f'{value}')}"
            columns.append([title, stat])

        s = term.bold("Stats\n\n")
        s += "\n".join(columnate(columns))
        return s

    def to_dict(self) -> dict:
        return {"integer_stats": self.integer_stats, "float_stats": self.float_stats}

    def increment_int_stat(self, key: IntegerStatKeys, increment_by: int = 1):
        self.integer_stats[key.value] = int(self.integer_stats.get(key.value, 0) + increment_by)

    def increment_float_stat(self, key: FloatStatKeys, increment_by: float):
        self.integer_stats[key.value] = self.integer_stats.get(key.value, 0) + increment_by
