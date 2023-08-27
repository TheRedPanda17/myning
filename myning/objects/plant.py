from datetime import datetime, timedelta
from enum import Enum

from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from myning.objects.item import Item
from myning.utilities.formatter import Formatter
from myning.utilities.ui import Colors, Icons


class PlantType(str, Enum):
    APPLE = "apple"
    BANANA = "banana"
    STRAWBERRY = "strawberry"
    CHERRY = "cherry"
    COCONUT = "coconut"
    ORANGE = "orange"


PLANT_TYPES = list(PlantType)


class Plant(Item):
    def __init__(self, *args, plant_type: PlantType | None = None, **kwargs):
        if "plant" not in args:
            args = [*args, "plant"]
        super().__init__(*args, **kwargs)
        self.plant_type = plant_type

        self.started = None
        self.harvested = None

    def to_dict(self):
        item = super().to_dict()
        return {
            **item,
            "plant_type": self.plant_type,
            "started": self.started.isoformat() if self.started else None,
            "harvested": self.harvested.isoformat() if self.harvested else None,
        }

    @classmethod
    def from_dict(cls, dict: dict):
        if not dict:
            return None

        cls = super().from_dict(dict)
        cls.plant_type = dict["plant_type"]
        cls.started = None
        if dict.get("started"):
            cls.started = datetime.strptime(dict["started"], "%Y-%m-%dT%H:%M:%S.%f")
        if dict.get("harvested"):
            cls.harvested = datetime.strptime(dict["harvested"], "%Y-%m-%dT%H:%M:%S.%f")

        return cls

    def sow(self):
        self.started = datetime.now()

    def grow(self):
        self.name = self.name.replace("seed", "plant")
        self.description = self.description.replace("seed", "plant")
        self.harvested = datetime.now()

    @property
    def icon(self):
        if self.expired:
            return "🤢"

        match self.plant_type:
            case PlantType.APPLE:
                return "🍎"
            case PlantType.BANANA:
                return "🍌"
            case PlantType.CHERRY:
                return "🍒"
            case PlantType.STRAWBERRY:
                return "🍓"
            case PlantType.COCONUT:
                return "🥥"
            case PlantType.ORANGE:
                return "🍊"
            case _:
                return Icons.UNKNOWN.value

    @property
    def growth_icon(self):
        growth_icons = {
            0: "🌱",
            0.5: "🪴",
            0.75: "🌳",
            1: self.icon,
        }
        return growth_icons[max(key for key in growth_icons if self.growth >= key)]

    @property
    def end_time(self):
        return self.started + timedelta(minutes=self.value * 10) if self.started else None

    @property
    def elapsed_time(self):
        if not self.started or not self.end_time:
            return 0
        return (datetime.now() - self.started).total_seconds()

    @property
    def total_time(self):
        if not self.started or not self.end_time:
            return 0
        return (self.end_time - self.started).total_seconds()

    @property
    def growth(self):
        return min(1, self.elapsed_time / self.total_time)

    @property
    def expires_in(self):
        ttl = self.value * 5
        if not self.harvested:
            return ttl
        return ttl - (datetime.now() - self.harvested).total_seconds()

    @property
    def expired(self):
        return self.expires_in <= 0

    @property
    def ready(self):
        return self.end_time <= datetime.now() if self.end_time else False

    @property
    def is_seed(self):
        return "seed" in self.name

    @property
    def time_left(self):
        return max(0, (self.end_time - datetime.now()).total_seconds()) if self.end_time else 0

    @property
    def details(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        table.add_column(style=Colors.LOCKED)
        table.add_row("Type", self.icon)
        table.add_row("Time left", f"{int(self.time_left // 60)} minutes")
        progress = ProgressBar(total=1, completed=self.growth, width=11)
        percentage = f"{self.growth * 100:.2f}%"
        table.add_row("Growth", progress, percentage, self.growth_icon)
        return table

    @property
    def fruit_stand_arr(self):
        return [
            self.icon,
            self.name,
            Text.from_markup(
                f"[{self.color}]{0 if self.expired else self.main_affect}[/]", justify="right"
            ),
            Icons.TIME,
            Text.from_markup(f"{Formatter.level(int(self.expires_in / 60))} mins", justify="right"),
        ]
