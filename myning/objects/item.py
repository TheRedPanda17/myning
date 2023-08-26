from enum import Enum

from rich.text import Text

from myning.chapters import OptionLabel
from myning.objects.object import Object
from myning.utilities.rand import get_random_int
from myning.utilities.ui import Colors, Icons


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
        self.affects: dict[str, int] = {}
        self.id = f"{self.name} - {get_random_int(10000000000000)}"

        if main_affect:
            self.add_affect(self.main_affect_type, main_affect)

    def add_affect(self, stat, value):
        self.affects[stat] = value

    def remove_affect(self, stat):
        del self.affects[stat]

    @property
    def file_name(self):
        return f"items/{self.id}"

    @property
    def main_affect(self):
        if self.type in (ItemType.MINERAL, ItemType.PLANT):
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
        s = f"{self.icon} [{self.color}]{self.name}[/]"
        if self.type not in (ItemType.MINERAL, ItemType.PLANT):
            s += f" ([{self.color}]{self.main_affect}[/])"
        return s

    @property
    def arr(self):
        return [
            self.icon,
            self.name,
            Text.from_markup(f"[{self.color}]{self.main_affect}[/]", justify="right"),
        ]

    @property
    def tutorial_new_str(self):
        return f"New {self.type} added: [{self.color}]{self.name}[/]"

    @property
    def battle_new_str(self):
        return (
            f"New {self.type} added: "
            f"{self.icon} [{self.color}]{self.name}[/] "
            f"([{self.color}]{self.main_affect}[/])"
        )
