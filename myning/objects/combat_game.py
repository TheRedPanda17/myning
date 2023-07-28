from random import choice, randint, shuffle
from string import ascii_lowercase
from typing import List

from blessed import Terminal

from myning.objects.settings import Settings
from myning.utils.ui import get_progress_bar
from myning.utils.utils import get_random_array_item

term = Terminal()


class CombatGame:
    STANDARD_PERCENT = 66

    def __init__(self, spear_count=None):
        self.block_keys = self.get_block_keys()
        self.block_position = None
        self.height = 15
        self.spears = []
        self.total_ticks = 0
        self.correct_ticks = 0
        self.neutral_ticks = 0
        self.spear_count = spear_count
        self.block_keys = self.block_keys[: self.spear_count]

    def tick(self):
        self.total_ticks += 1
        if self.total_ticks < 10:
            self.neutral_ticks += 1
            return

        self._advance_spears()
        self._add_spears()
        self._remove_spears()

        if self._cursor_correct:
            self.correct_ticks += 1
        elif self._cursor_neutral:
            self.neutral_ticks += 1

    def change_block(self, new_key: str):
        if new_key in self.block_keys:
            self.block_position = new_key

    @property
    def started(self):
        return self.block_position is not None

    @property
    def bonus(self):
        if not self.started or Settings().mini_games_disabled:
            return 1

        if self._correct_percentage < CombatGame.STANDARD_PERCENT:
            bonus = self._correct_percentage - CombatGame.STANDARD_PERCENT
        else:
            bonus = (self._correct_percentage - CombatGame.STANDARD_PERCENT) * 3

        return 1 + (bonus / 100)

    @property
    def _cursor_correct(self):
        spear = self._spear_at_height(self.height)
        if not spear:
            return False
        return spear.block_char == self.block_position

    @property
    def _cursor_neutral(self):
        return not self._spear_at_height(self.height)

    @property
    def _correct_percentage(self):
        ticks = self.total_ticks - self.neutral_ticks
        if ticks == 0:
            return 100
        return (self.correct_ticks / ticks) * 100

    def _add_spears(self):
        fully_visible = list(filter(lambda spear: spear.is_deployed, self.spears))
        started = list(filter(lambda spear: spear.started, self.spears))
        min_length = 4
        max_length = 6

        if len(started) == len(fully_visible):
            char = get_random_array_item(self.block_keys)
            self.spears.append(Spear(char, randint(min_length, max_length)))

    def _advance_spears(self):
        shuffle(self.spears)
        for spear in self.spears:
            spear.y_position += 1

    def _remove_spears(self):
        for spear in list(filter(lambda spear: spear.y_position > self.height, self.spears)):
            self.spears.remove(spear)

    def _spears_with_char(self, key: str) -> List["Spear"]:
        return list(filter(lambda spear: spear.block_char == key, self.spears))

    def _spear_at_height(self, y: int) -> "Spear":
        for spear in self.spears:
            if spear.occupies_cell(y):
                return spear

    def get_block_keys(self):
        if Settings().hard_combat_disabled:
            return ["a", "s", "d", "f"]
        chars = []
        options = ascii_lowercase.replace("x", "")
        for _ in range(4):
            char = choice(options)
            chars.append(char)
            options = options.replace(char, "")
        return chars

    def __str__(self) -> str:
        s = "╔" + "═" * (8 * len(self.block_keys) + 5) + "╗\n"
        for col in range(self.height):
            r = "║"
            for key in self.block_keys:
                char = "  "
                for spear in list(
                    filter(lambda spear: spear.occupies_cell(col), self._spears_with_char(key))
                ):
                    char = spear.char_at(col)
                r += f"      {char}"
            s += r + "     ║\n"

        s += "║" + "─" * (8 * len(self.block_keys) + 5) + "║\n"
        s += "║   "
        for i in range(self.spear_count):
            if self.block_keys[i] == self.block_position:
                s += term.underline + term.cyan
            s += f"   {self.block_keys[i].capitalize()}{self.block_keys[i]}   {term.normal}"

        s += "  ║"
        if not self.started:
            s += "    Exit (↵)"
        s += "\n╚" + "═" * (8 * len(self.block_keys) + 5) + "╝\n\n"

        s += self._score_str
        return s

    @property
    def _score_str(self):
        s = f" {term.bold}Correct: {term.normal}"
        if not self.started:
            return s + "N/A"

        s += get_progress_bar(self._correct_percentage, 100, 8 * len(self.block_keys) - 3)

        s += f" {round(self._correct_percentage)}%"

        return s


class Spear:
    def __init__(self, block_char: str, length: int = 4) -> None:
        self.y_position = -length
        self.block_char = block_char
        self.length = length

    @property
    def is_deployed(self):
        return self.y_position > randint(0, 2)

    @property
    def started(self):
        return self.y_position > -self.length

    def occupies_cell(self, y: int):
        return self.y_position <= y and y < self.y_position + self.length

    def char_at(self, y: int):
        if y < self.y_position:
            return "  "
        elif y == self.y_position:
            return f"{term.green}VV{term.normal}"
        elif y < self.y_position + self.length - 1:
            return f"{term.brown}||{term.normal}"
        else:
            return "\\/"
