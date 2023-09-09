from enum import Enum

from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utilities.file_manager import FileManager


class SortOrder(str, Enum):
    TYPE = "type"
    VALUE = "value"


class Settings(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        trip = FileManager.load(Settings, cls.file_name)
        if not trip:
            trip = cls()
        cls._instance = trip

    def __init__(
        self,
        army_columns=15,
        mini_games_disabled=False,
        hard_combat_disabled=True,
        compact_mode=False,
        sort_order=SortOrder.TYPE,
        purchase_confirmation=True,
    ) -> None:
        self.army_columns = army_columns
        self.mini_games_disabled = mini_games_disabled
        self.hard_combat_disabled = hard_combat_disabled
        self.compact_mode = compact_mode
        self.sort_order: SortOrder = sort_order
        self.purchase_confirmation = purchase_confirmation

    @classmethod
    def from_dict(cls, attrs: dict):
        return cls(**attrs)

    def to_dict(self) -> dict:
        return {
            "army_columns": self.army_columns,
            "mini_games_disabled": self.mini_games_disabled,
            "hard_combat_disabled": self.hard_combat_disabled,
            "compact_mode": self.compact_mode,
            "sort_order": self.sort_order,
            "purchase_confirmation": self.purchase_confirmation,
        }

    @classmethod
    @property
    def file_name(cls):
        return "settings"

    def set_army_columns(self, value: int):
        if self.army_columns >= 5 <= 25:
            self.army_columns = value

    def toggle_mini_games(self):
        self.mini_games_disabled = not self.mini_games_disabled

    def toggle_hard_combat(self):
        self.hard_combat_disabled = not self.hard_combat_disabled

    def toggle_compact_mode(self):
        self.compact_mode = not self.compact_mode

    def toggle_sort_order(self):
        self.sort_order = SortOrder.TYPE if self.sort_order == SortOrder.VALUE else SortOrder.VALUE

    def toggle_purchase_confirmation(self):
        self.purchase_confirmation = not self.purchase_confirmation

    @property
    def mini_games_status(self) -> str:
        return "disabled" if self.mini_games_disabled else "enabled"

    @property
    def hard_combat_status(self) -> str:
        return "normal" if self.hard_combat_disabled else "hard"

    @property
    def compact_status(self) -> str:
        return "enabled" if self.compact_mode else "disabled"

    @property
    def purchase_confirmation_status(self) -> str:
        return "enabled" if self.purchase_confirmation else "disabled"
