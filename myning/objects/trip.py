from blessed import Terminal

from myning.config import MINES
from myning.objects.character import Character
from myning.objects.item import Item, ItemType
from myning.objects.mine import Mine
from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager, Subfolders
from myning.utils.ui import columnate
from myning.utils.ui_consts import Icons

LOST_RATIO = 2
term = Terminal()


class Trip(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        trip = FileManager.load(Trip, cls.file_name)
        if not trip:
            trip = cls()
        cls._instance = trip

    def __init__(self) -> None:
        self.clear()

    def clear(self):
        self.minerals_mined: list[Item] = []
        self.items_found: list[Item] = []
        self.allies_gained: list[Character] = []
        self.allies_lost: list[Character] = []
        self.battles_won = 0
        self.enemies_defeated = 0
        self.seconds_left = 0
        self.experience_gained = 0
        self.total_seconds = 0
        self.species_discovered = 0
        self.mine: Mine = None

    def add_item(self, item: Item):
        if item.type == ItemType.MINERAL:
            self.minerals_mined.append(item)
        else:
            self.items_found.append(item)

    def add_ally(self, ally: Character):
        self.allies_gained.append(ally)

    def remove_ally(self, ally: Character):
        self.allies_lost.append(ally)

    def add_battle(self, enemies_defeated: int, won: bool):
        self.enemies_defeated += enemies_defeated
        self.experience_gained += enemies_defeated * self.mine.exp_multiplier
        if won:
            self.battles_won += 1

    def tick_passed(self, seconds: int):
        self.seconds_left -= seconds

    def start_trip(self, seconds: int):
        self.seconds_left = seconds
        self.total_seconds = seconds

    def subtract_losses(self):
        self.minerals_mined = self.subtract_loss(self.minerals_mined)
        self.items_found = self.subtract_loss(self.items_found)
        self.experience_gained = int(self.enemies_defeated / LOST_RATIO)
        self.allies_gained = [ally for i, ally in enumerate(self.allies_gained) if i % 2 == 0]
        self.total_seconds = self.total_seconds - self.seconds_left

    def subtract_loss(self, arr: list):
        new = []
        for i, item in enumerate(arr):
            if i % LOST_RATIO != 0:
                new.append(item)
        return new

    def to_dict(self) -> dict:
        return {
            "minerals_mined": [item.id for item in self.minerals_mined],
            "items_found": [item.id for item in self.items_found],
            "battles_won": self.battles_won,
            "enemies_defeated": self.enemies_defeated,
            "seconds_left": self.seconds_left,
            "allies_gained": [ally.to_dict() for ally in self.allies_gained],
            "allies_lost": [ally.to_dict() for ally in self.allies_lost],
            "mine": self.mine.name if self.mine else None,
            "experience_gained": self.experience_gained,
            "total_seconds": self.total_seconds,
        }

    @classmethod
    @property
    def file_name(cls):
        return "trip"

    @classmethod
    def from_dict(cls, dict: dict) -> "Trip":
        summary = Trip()
        summary.minerals_mined = []

        for item_id in dict["minerals_mined"]:
            item = FileManager.load(Item, item_id, Subfolders.ITEMS)
            if not item:
                print("Could not find mineral", item_id)
                continue
            else:
                summary.minerals_mined.append(item)

        summary.items_found = [
            FileManager.load(Item, item_id, Subfolders.ITEMS) for item_id in dict["items_found"]
        ]
        summary.allies_gained = [Character.from_dict(ally) for ally in dict["allies_gained"]]
        if "allies_lost" in dict:
            summary.allies_lost = [Character.from_dict(ally) for ally in dict["allies_lost"]]
        summary.mine = MINES[dict["mine"]] if dict["mine"] else None
        summary.battles_won = dict["battles_won"]
        summary.enemies_defeated = dict["enemies_defeated"]
        summary.seconds_left = dict["seconds_left"]
        summary.experience_gained = dict["experience_gained"]
        summary.total_seconds = dict.get("total_seconds") or 0
        return summary

    def get_minerals_string(self):
        mineral = Item("", "", type=ItemType.MINERAL)

        levels = {}
        for item in self.minerals_mined:
            if item:
                levels[item.main_affect] = levels.get(item.main_affect, 0) + 1

        return " ".join(
            [
                f"{mineral.color}{mineral.icon} {level}{term.normal} ({levels[level]})"
                for level in sorted(levels)
            ]
        )

    @property
    def summary(self):
        mine = f"{term.bold}{self.mine.name}{term.normal}"
        time_left = f"{int(self.seconds_left / 60) + 1} minutes left"
        battles = f"{Icons.VICTORY} {self.battles_won}"
        enemies = f"{Icons.SWORD} {self.enemies_defeated}"
        minerals = f"{Icons.MINERAL} {len(self.minerals_mined)}"

        return f"{mine}: {time_left} {battles} {enemies} {minerals}"

    def __str__(self):
        title = term.bold("\nYour Mining Trip\n")
        return title + "\n".join(
            columnate(
                [
                    [
                        "Minerals",
                        self.get_minerals_string() if self.minerals_mined else "None",
                    ],
                    [
                        "Items",
                        " ".join(
                            f"{item.color}{item.icon} {item.main_affect}{term.normal}"
                            for item in self.items_found
                        )
                        if self.items_found
                        else "None",
                    ],
                    [
                        "New Allies",
                        " ".join(f"{ally.name} {ally.level_str}," for ally in self.allies_gained)
                        if self.allies_gained
                        else "None",
                    ],
                    [
                        "Lost Allies",
                        " ".join(f"{ally.name} {ally.level_str}," for ally in self.allies_lost)
                        if self.allies_lost
                        else "None",
                    ],
                    [
                        "Battles Won",
                        f"{term.bold}{self.battles_won}{term.normal}",
                    ],
                    [
                        "Enemies Defeated",
                        f"{term.bold}{self.enemies_defeated}{term.normal}",
                    ],
                ]
            )
        )
