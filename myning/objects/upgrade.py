from enum import Enum

from rich.text import Text

from myning.objects.object import Object
from myning.utilities.formatter import Formatter


class UpgradeType(Enum):
    """
    The current specialty types of stores in the game
    """

    UPGRADE = "upgrade"
    RESEARCH = "research"


class Upgrade(Object):
    def __init__(self, id, name, descriptions, costs, values: list, type):
        self.id = id
        self.name = name
        self.descriptions = descriptions
        self.costs = costs
        self.values = values
        self.level = 0
        self.type = type

    # name and player_name
    @property
    def name(self):
        return self._name if len(self.values) == 1 else f"{self._name} - lvl {self.level + 1}"

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def player_name(self):
        return self._name if len(self.values) == 1 else f"{self._name} ({self.level})"

    @property
    def description(self):
        return self.descriptions[self.level]

    @property
    def player_description(self):
        return self.descriptions[self.level - 1]

    # value and player_value
    @property
    def value(self):
        return self.values[self.level]

    @property
    def player_value(self):
        return self.values[self.level - 1]

    # misc attributes
    @property
    def cost(self):
        return self.costs[self.level]

    @property
    def max_level(self):
        return len(self.costs) == self.level

    @property
    def cost_str(self):
        if self.type == UpgradeType.RESEARCH:
            return Formatter.research_points(self.cost)
        if self.type == UpgradeType.UPGRADE:
            return Formatter.gold(self.cost)
        return self.cost

    @property
    def arr(self):
        return [
            self.name,
            Text.from_markup(self.cost_str, justify="right"),
            self.description,
        ]

    @property
    def player_arr(self):
        return [
            self.player_name,
            self.player_description,
        ]

    @classmethod
    def from_dict(cls, attrs: dict, type=UpgradeType.UPGRADE):
        return cls(**attrs, type=type)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self._name,
            "description": self.description,
            "cost": self.cost,
            "level": self.level,
            "type": self.type,
        }
