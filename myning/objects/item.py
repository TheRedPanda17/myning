from enum import Enum

from blessed import Terminal

from myning.objects.object import Object
from myning.utils.output import stat_string
from myning.utils.ui_consts import Colors, Icons
from myning.utils.utils import get_random_int

term = Terminal()


class ItemType(str, Enum):
    MINERAL = "mineral"
    WEAPON = "weapon"
    HELMET = "helmet"
    SHIRT = "shirt"
    PANTS = "pants"
    SHOES = "shoes"
    PLANT = "plant"

    @classmethod
    @property
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class Item(Object):
    def __init__(
        self,
        name: str,
        description: str,
        type: ItemType,
        value: int = 0,
        main_affect: int = 0,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.value = value
        self.affects = {}
        self.id = f"{self.name} - {get_random_int(10000000000000)}"

        if main_affect:
            self.add_affect(self.main_affect_type, main_affect)

    def add_affect(self, stat, value):
        self.affects[stat] = value

    def remove_affect(self, stat):
        self.affects[stat] = None

    @property
    def file_name(self):
        return f"items/{self.id}"

    @property
    def main_affect(self):
        if self.type == ItemType.MINERAL or self.type == ItemType.PLANT:
            return self.value
        return self.affects[self.main_affect_type]

    @property
    def main_affect_type(self):
        if self.type == ItemType.WEAPON:
            return "damage"
        if self.type == ItemType.MINERAL:
            return "value"
        return "armor"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "affects": self.affects,
            "type": self.type,
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, dict: dict):
        item = cls(
            dict["name"],
            dict["description"],
            dict["type"],
            value=dict["value"],
        )
        item.affects = dict["affects"]
        item.id = dict["id"]
        return item

    @property
    def color(self):
        match self.type:
            case ItemType.MINERAL:
                return Colors.GOLD
            case ItemType.WEAPON:
                return Colors.WEAPON
            case ItemType.HELMET | ItemType.SHIRT | ItemType.PANTS | ItemType.SHOES:
                return Colors.ARMOR
            case ItemType.PLANT:
                return Colors.PLANT
            case _:
                return term.normal

    @property
    def tui_color(self):
        match self.type:
            case ItemType.MINERAL:
                return "gold1"
            case ItemType.WEAPON:
                return "red1"
            case ItemType.HELMET | ItemType.SHIRT | ItemType.PANTS | ItemType.SHOES:
                return "dodger_blue1"
            case ItemType.PLANT:
                return "green1"
            case _:
                return ""

    @property
    def icon(self):
        match self.type:
            case ItemType.MINERAL:
                return Icons.MINERAL
            case ItemType.WEAPON:
                return Icons.WEAPON
            case ItemType.HELMET:
                return Icons.HELMET
            case ItemType.SHIRT:
                return Icons.SHIRT
            case ItemType.PANTS:
                return Icons.PANTS
            case ItemType.SHOES:
                return Icons.SHOES
            case _:
                return Icons.UNKNOWN

    def __str__(self):
        return f"{self.icon} {self.name} - {self.color}{self.main_affect}{term.normal}"

    @property
    def str_arr(self):
        return [
            f"{self.icon}",
            self.name,
            f"{self.color}{self.main_affect}{term.normal}",
        ]

    @property
    def tui_arr(self):
        return [
            self.icon,
            self.name,
            f"[bold {self.tui_color}]{self.main_affect}[/]",
        ]

    @property
    def tui_str(self):
        s = f"{self.icon} [{self.tui_color}]{self.name}[/]"
        if self.type not in (ItemType.MINERAL, ItemType.PLANT):
            s += f" ([{self.tui_color}]{self.main_affect}[/])"
        return s

    def print_details(self):
        s = stat_string("Name", self.name)
        s += stat_string("Description", self.description)
        s += stat_string("Value", self.value, newline=len(self.affects) != 0)

        i = 0
        for key, affect in self.affects.items():
            s += stat_string(key.capitalize(), affect, newline=i != len(self.affects) - 1)
            i += 1

        return s

    def get_new_text(self):
        return f"New {self.type} added: {term.bold}{self.color}{self.name}{term.normal}"

    @property
    def tui_new_text(self):
        return (
            f"New {self.type} added: "
            f"{self.icon} [{self.tui_color}]{self.name}[/] "
            f"([{self.tui_color}]{self.main_affect}[/])"
        )
