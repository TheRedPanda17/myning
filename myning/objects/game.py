from enum import Enum

from myning.config import MINES
from myning.objects.object import Object
from myning.objects.player import Player
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager


class GameState(int, Enum):
    TUTORIAL = 1
    READY = 2


class Game(Object, metaclass=Singleton):
    _state = GameState.TUTORIAL

    @classmethod
    def initialize(cls):
        game = FileManager.load(Game, "game") or cls()
        cls._instance = game

        # Fill mines with progress
        player = Player()
        for name, mine in MINES.items():
            mine.player_progress = player.get_mine_progress(name)

    @classmethod
    @property
    def file_name(cls):
        return "game"

    def to_dict(self):
        return {
            "state": self._state,
        }

    @classmethod
    def from_dict(cls, dict: dict):
        game = cls()
        game._state = dict["state"]
        return game
