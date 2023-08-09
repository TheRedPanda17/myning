from enum import Enum

from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager


class IntegerStatKeys(str, Enum):
    TRIPS_FINISHED = "trips_finished"
    ARMY_DEFEATS = "army_defeats"
    BATTLES_WON = "battles_won"
    ENEMIES_DEFEATED = "enemies_defeated"
    MINERALS_MINED = "minerals_mined"


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

    def __init__(self, integer_stats: dict = {}):
        self.integer_stats = integer_stats

    @classmethod
    def from_dict(cls, data) -> "Stats":
        if data is None:
            return Stats()
        return Stats(data["integer_stats"])

    def to_dict(self) -> dict:
        return {"integer_stats": self.integer_stats}

    def increment_int_stat(self, key: IntegerStatKeys, incredment_by: int = 1):
        self.integer_stats[key.value] = self.integer_stats.get(key.value, 0) + incredment_by
