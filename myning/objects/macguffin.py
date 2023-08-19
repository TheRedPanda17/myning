from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager


class Macguffin(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        macguffin = FileManager.load(Macguffin, cls.file_name)
        if not macguffin:
            macguffin = cls()
        cls._instance = macguffin

    @classmethod
    @property
    def file_name(cls):
        return "macguffin"

    def __init__(
        self,
        xp_boost: float = 1,
        mineral_boost: float = 1,
        research_boost: float = 1,
        soul_credit_boost: float = 1,
        plant_boost: float = 1,
    ):
        self.xp_boost = xp_boost
        self.mineral_boost = mineral_boost
        self.research_boost = research_boost
        self.soul_credit_boost = soul_credit_boost
        self.plant_boost = plant_boost

    @classmethod
    def from_dict(cls, data) -> "Macguffin":
        if data is None:
            return Macguffin()
        return Macguffin(
            data["exp_boost"],
            data["store_boost"],  # Mineral boost, old key
            data["research_boost"],
            data["soul_credit_boost"],
            data["plant_boost"],
        )

    def get_new_standard_boost(self, game_value: int):
        return round((game_value / 500_000) + self.mineral_boost, 2)

    def get_new_smaller_boost(self, game_value: int):
        bonus = (game_value / 2_500_000) + self.plant_boost
        return round(max(bonus, 1), 2)

    def to_dict(self) -> dict:
        return {
            "exp_boost": self.xp_boost,
            "store_boost": self.mineral_boost,  # Mineral boost, old key
            "research_boost": self.research_boost,
            "soul_credit_boost": self.soul_credit_boost,
            "plant_boost": self.plant_boost,
        }
