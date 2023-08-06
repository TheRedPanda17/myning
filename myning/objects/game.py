from enum import Enum
from typing import List

from myning import chapters
from myning.config import MINES
from myning.objects.menu_item import MenuItem
from myning.objects.object import Object
from myning.objects.player import Player
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.tab_title import TabTitle

MAIN_MENU = [
    MenuItem("Mine"),
    MenuItem("Store"),
    MenuItem("Armory"),
    MenuItem("Healer"),
    MenuItem("Wizard Hut", prerequisites=[MINES["Hole in the ground"]]),
    MenuItem("Barracks", prerequisites=[MINES["Small pit"]]),
    MenuItem("Blacksmith", prerequisites=[MINES["Trench"]]),
    MenuItem("Graveyard", prerequisites=[MINES["Large pit"]]),
    MenuItem("Garden", prerequisites=[MINES["Cave"]]),
    MenuItem("Research Facility", prerequisites=[MINES["Cavern"]]),
    MenuItem("Time Machine", prerequisites=[MINES["Cave System"]]),
    MenuItem("Journal"),
    MenuItem("Stats"),
    MenuItem("Settings"),
    MenuItem("Exit"),
]


class GameState(int, Enum):
    SETUP = 0
    TUTORIAL = 1
    READY = 2
    STORE = 3
    EQUIP = 4
    ARMY = 5
    MINE = 6
    RECOVERY = 7


class Game(Object, metaclass=Singleton):
    _state = GameState.TUTORIAL
    # _last_update = datetime.time()

    @classmethod
    def initialize(cls):
        game = FileManager.load(Game, "game") or cls()
        cls._instance = game

        # Fill mines with progress
        player = Player()
        for name, mine in MINES.items():
            mine.player_progress = player.get_mine_progress(name)

    @classmethod
    def play(cls):
        game = cls._instance
        match game._state:
            case GameState.TUTORIAL:
                chapters.tutorial.play()
            case GameState.MINE:
                chapters.enter_mine.begin()
            case GameState.STORE:
                chapters.enter_store.play()

        game._state = GameState.READY
        game._loop()

    @classmethod
    @property
    def file_name(cls):
        return "game"

    def to_dict(self):
        return {
            "state": self._state,
            # "last_update": self._last_update.isoformat(),
        }

    @classmethod
    def from_dict(cls, dict: dict):
        game = cls()
        game._state = dict["state"]
        # game._last_update = dict["last_update"]
        return game

    def menu_options(self) -> List[MenuItem]:
        return MAIN_MENU

    def _loop(self):
        # select a menu option
        TabTitle.change_tab_status("Main Menu")

        menu_options = self.menu_options()
        _, index = pick(
            [*[str(option) for option in menu_options]],
            "Where would you like to go next?",
        )

        # validate and play selection
        menu_option = menu_options[index]
        if menu_option.unlocked:
            self._state = getattr(GameState, menu_option.upper_name(), GameState.READY)
            TabTitle.change_tab_status(menu_option.name)
            menu_option()
            self._state = GameState.READY
        else:
            pick(
                ["I'll get on it"],
                f"You must complete {menu_option.required_mines_str} first.",
            )

        self._loop()
