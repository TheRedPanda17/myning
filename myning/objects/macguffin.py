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
        xp_boost=1,
        mineral_boost=1,
        research_boost=1,
        soul_credit_boost=1,
        plant_boost=1,
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

    def to_dict(self) -> dict:
        return {
            "exp_boost": self.xp_boost,
            "store_boost": self.mineral_boost,  # Mineral boost, old key
            "research_boost": self.research_boost,
            "soul_credit_boost": self.soul_credit_boost,
            "plant_boost": self.plant_boost,
        }

    @property
    def xp_percentage(self):
        return self.percentage(self.xp_boost)

    @property
    def mineral_percentage(self):
        return self.percentage(self.mineral_boost)

    @property
    def research_percentage(self):
        return self.percentage(self.research_boost)

    @property
    def soul_credit_percentage(self):
        return self.percentage(self.soul_credit_boost)

    @property
    def plant_percentage(self):
        return self.percentage(self.plant_boost)

    def percentage(self, number):
        return f"{int(number * 100)}%"
