from typing import List

from myning.objects.character import Character
from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.utilities.file_manager import FileManager


class Graveyard(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        graveyard = FileManager.load(Graveyard, cls.file_name)
        if not graveyard:
            graveyard = cls()
        cls._instance = graveyard

    @classmethod
    @property
    def file_name(cls):
        return "graveyard"

    def __init__(
        self,
        soul_credits: float = 0,
        fallen_allies: List[Character] = None,
    ):
        self.soul_credits = soul_credits
        self._fallen_allies = fallen_allies or []

    @classmethod
    def from_dict(cls, data) -> "Graveyard":
        if data is None:
            return Graveyard()
        return Graveyard(
            data["soul_credits"],
            [Character.from_dict(ally) for ally in data.get("fallen_allies", [])],
        )

    def to_dict(self) -> dict:
        return {
            "soul_credits": self.soul_credits,
            "fallen_allies": [ally.to_dict() for ally in self._fallen_allies],
        }

    def add_soul_credits(self, credits: float):
        if credits > 0:
            self.soul_credits += credits

    def remove_soul_credits(self, credits: float):
        if credits > 0:
            self.soul_credits -= credits

    @property
    def fallen_allies(self) -> list[Character]:
        return self._fallen_allies

    def remove_fallen_ally(self, ally: Character):
        self._fallen_allies.remove(ally)

    def add_fallen_ally(self, ally: Character):
        self._fallen_allies.append(ally)
