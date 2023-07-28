from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager


class Settings(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        trip = FileManager.load(Settings, cls.file_name)
        if not trip:
            trip = cls()
        cls._instance = trip

    def __init__(
        self, army_columns=15, mini_games_disabled=False, hard_combat_disabled=True
    ) -> None:
        self.army_columns = army_columns
        self.mini_games_disabled = mini_games_disabled
        self.hard_combat_disabled = hard_combat_disabled

    @classmethod
    def from_dict(cls, attrs: dict):
        return cls(**attrs)

    def to_dict(self) -> dict:
        return {
            "army_columns": self.army_columns,
            "mini_games_disabled": self.mini_games_disabled,
            "hard_combat_disabled": self.hard_combat_disabled,
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

    @property
    def mini_games_status(self) -> str:
        return "disabled" if self.mini_games_disabled else "enabled"

    @property
    def hard_combat_status(self) -> str:
        return "normal" if self.hard_combat_disabled else "hard"
