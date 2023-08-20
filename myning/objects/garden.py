from datetime import datetime, timedelta

from blessed import Terminal

from myning.objects.object import Object
from myning.objects.plant import Plant
from myning.objects.singleton import Singleton
from myning.utilities import rand
from myning.utilities.fib import fibonacci
from myning.utilities.file_manager import FileManager, Subfolders

term = Terminal()


class Garden(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        garden = FileManager.load(Garden, cls.file_name)
        if not garden:
            garden = cls()
        cls._instance = garden

    @classmethod
    @property
    def file_name(cls):
        return "garden"

    def __init__(
        self,
        level: int = 1,
        water: int = 0,
        last_collected_water: datetime = None,
        rows: list[list[Plant]] = None,
    ):
        self.level = level
        self.water = water if water else level
        self.last_collected_water = last_collected_water
        self.rows = rows if rows else [[None for _ in range(level)] for _ in range(level)]

    def to_dict(self):
        return {
            "level": self.level,
            "water": self.water,
            "last_collected_water": self.last_collected_water.isoformat()
            if self.last_collected_water
            else None,
            "rows": [[plant.id if plant else None for plant in row] for row in self.rows],
        }

    @classmethod
    def from_dict(cls, dict: dict):
        if not dict:
            return Garden(1)
        return Garden(
            dict["level"],
            dict["water"],
            datetime.strptime(dict["last_collected_water"], "%Y-%m-%dT%H:%M:%S.%f")
            if dict.get("last_collected_water")
            else None,
            [
                [FileManager.load(Plant, plant_id, subfolder=Subfolders.ITEMS) for plant_id in row]
                for row in dict["rows"]
            ],
        )

    @property
    def next_empty_row(self):
        return self.next_empty_coords[0]

    @property
    def next_empty_coords(self):
        for row in range(self.level):
            for column in range(self.level):
                plant = self.get_plant(row, column)
                if not plant:
                    return row, column
        return None, None

    @property
    def next_unharvest_row(self):
        return self.next_plant_coords[0]

    @property
    def next_plant_coords(self):
        for row in range(self.level):
            for column in range(self.level):
                plant = self.get_plant(row, column)
                if plant and plant.ready:
                    return row, column
        return None, None

    @property
    def upgrade_cost(self) -> int:
        return self.get_upgrade_cost(self.level + 1)

    @property
    def total_value(self) -> int:
        return sum(self.get_upgrade_cost(level) for level in range(1, self.level))

    def get_upgrade_cost(self, level: int) -> int:
        return fibonacci(level + 4) * 100

    def collect_water(self):
        if not self.last_collected_water:
            self.last_collected_water = datetime.now()
            return
        time_since_last_water = (datetime.now() - self.last_collected_water).total_seconds()
        new_water = min(self.level, self.water + int(time_since_last_water / 60))
        if new_water > self.water:
            self.last_collected_water = datetime.now()
            self.water = new_water

    def level_up(self):
        self.level += 1
        self.water += 1
        for row in self.rows:
            row.append(None)

        self.rows.append([None for _ in range(self.level)])

    def add_plant(self, plant: "Plant", row: int, column: int):
        self.rows[row][column] = plant

    def get_plant(self, row: int, column: int):
        return self.rows[row][column]

    def check_ready(self, row: int, column: int) -> bool:
        plant = self.get_plant(row, column)
        return plant and plant.ready

    def uproot_plant(self, row: int, column: int):
        uprooted_plant = self.rows[row][column]
        self.rows[row][column] = None
        return uprooted_plant

    def harvest_plant(self, row: int, column: int):
        plant: Plant = self.rows[row][column]
        plant.grow()
        plant.value = plant.value * (int(self.level / 2) + 4)
        self.uproot_plant(row, column)
        return plant

    def water_plant(self, row: int, column: int):
        plant = self.get_plant(row, column)
        if not plant:
            return
        plant.started = plant.started - timedelta(minutes=1 * self.level)
        self.water -= 1
        return plant

    def __str__(self):
        s = "╔" + "════╦" * (self.level - 1) + "════╗\n"
        for i in range(len(self.rows)):
            s += f"║{'║'.join([plant.garden_string if plant else ' xx ' for plant in self.rows[i]])}║\n"

        s += "╚" + "════╩" * (self.level - 1) + "════╝"
        return s
