from datetime import datetime, timedelta
from enum import Enum

from blessed import Terminal

from myning.objects.item import Item
from myning.utils.ui_consts import Icons


class PlantType(str, Enum):
    APPLE = "apple"
    BANANA = "banana"
    STRAWBERRY = "strawberry"
    CHERRY = "cherry"
    COCONUT = "coconut"
    ORANGE = "orange"


PLANT_TYPES = [plant_type for plant_type in PlantType]
term = Terminal()


class Plant(Item):
    def __init__(self, *args, plant_type: PlantType = None, **kwargs):
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

    def sow(self):
        self.started = datetime.now()

    def grow(self):
        self.name = self.name.replace("seed", "plant")
        self.description = self.description.replace("seed", "plant")
        self.harvested = datetime.now()

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

    @property
    def growth_icon(self):
        if self.growth >= 1:
            return f" {self.icon} "
        elif self.growth >= 0.75:
            return " 🌳 "
        elif self.growth >= 0.5:
            return " 🪴 "
        return " 🌱 "

    @property
    def end_time(self):
        return self.started + timedelta(minutes=self.value * 10)

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
    def growth(self):
        if not self.started:
            return 0
        elapsed = (datetime.now() - self.started).total_seconds()
        total_time = (self.end_time - self.started).total_seconds()
        return min(1, elapsed / total_time)

    @property
    def ready(self) -> bool:
        return self.end_time <= datetime.now()

    @property
    def is_seed(self):
        return "seed" in self.name

    @property
    def garden_string(self):
        return f"{self.growth_icon}"

    @property
    def time_left(self):
        return max(0, (self.end_time - datetime.now()).total_seconds())

    @property
    def details_string(self):
        type = f"{term.bold}Type: {term.normal}{self.icon}"
        growth = f"{term.bold}Growth: {term.normal}{self.growth * 100:.2f}%"
        time_left = f"{term.bold}Time left: {term.normal}{int(self.time_left//60)} minutes"

        return f"{type}\n{growth}\n{time_left}"

    @property
    def fruit_stand_arr(self):
        return [
            self.icon,
            self.name,
            f"{self.color}{self.main_affect if not self.expired else 0}{term.normal}",
            f"{Icons.TIME} {term.cyan}{int(self.expires_in/60)}{term.normal}",
            "mins",
        ]

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
