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
        exp_boost=1,
        mineral_boost=1,
        research_boost=1,
        soul_credit_boost=1,
    ):
        self.exp_boost = exp_boost
        self.mineral_boost = mineral_boost
        self.research_boost = research_boost
        self.soul_credit_boost = soul_credit_boost

    @classmethod
    def from_dict(cls, data) -> "Macguffin":
        if data is None:
            return Macguffin()
        return Macguffin(**data)

    def to_dict(self) -> dict:
        return {
            "exp_boost": self.exp_boost,
            "store_boost": self.mineral_boost,
            "research_boost": self.research_boost,
            "soul_credit_boost": self.soul_credit_boost,
        }

    @property
    def exp_percentage(self):
        return f"{int(self.exp_boost * 100)}%"

    @property
    def store_percentage(self):
        return f"{int(self.mineral_boost * 100)}%"
