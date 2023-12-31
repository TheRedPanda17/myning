from enum import Enum

from rich.table import Table
from rich.text import Text

from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter


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
    FALLEN_SOLDIERS = "fallen_soldiers"
    DISCOVERED_SPECIES = "discovered_species"

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

    def __init__(
        self,
        integer_stats: dict[str, int] | None = None,
        float_stats: dict[str, float] | None = None,
    ):
        self.integer_stats = integer_stats or {}
        self.float_stats = float_stats or {}

    @classmethod
    def from_dict(cls, data: dict) -> "Stats":
        if data is None:
            return Stats()
        return Stats(data["integer_stats"], data.get("float_stats", {}))

    @property
    def all_stats(self) -> dict[str, int | float]:
        return {**self.integer_stats, **self.float_stats}

    @property
    def display(self):
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        for key, value in self.all_stats.items():
            table.add_row(
                Formatter.title(key),
                Text.from_markup(
                    f"{value:,.0f}"
                    if isinstance(value, int) or value.is_integer()
                    else f"{value:,.2f}",
                    justify="right",
                ),
            )
        return table

    def to_dict(self) -> dict:
        return {"integer_stats": self.integer_stats, "float_stats": self.float_stats}

    def increment_int_stat(self, key: IntegerStatKeys, increment_by: int = 1):
        self.integer_stats[key.value] = int(self.integer_stats.get(key.value, 0) + increment_by)

    def set_int_stat(self, key: IntegerStatKeys, value: int):
        self.integer_stats[key.value] = value

    def increment_float_stat(self, key: FloatStatKeys, increment_by: float):
        self.integer_stats[key.value] = self.integer_stats.get(key.value, 0) + increment_by
