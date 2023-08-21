from enum import Enum

from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from myning.objects.mine_stats import MineStats
from myning.objects.object import Object
from myning.utilities.formatter import Formatter
from myning.utilities.ui import Colors, Icons


class MineType(str, Enum):
    REGULAR = "regular"
    COMBAT = "combat"
    RESOURCE = "resource"


class Mine(Object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.min_player_level = 0
        self.cost = 0
        self.max_enemy_items = 0
        self.max_item_level = 0
        self.max_enemy_item_level = 0
        self.enemy_item_scale = 1
        self.exp_boost = None
        self.enemies = []
        self.character_levels = []
        self.odds = []
        self.win_criteria: MineStats = None
        self.player_progress: MineStats = None
        self.resource = None
        self.companion_rarity = 0

    @property
    def file_name(self):
        return f"mines/{self.name}"

    @property
    def exp_multiplier(self):
        return self.exp_boost + 1

    @property
    def win_value(self):
        if not self.win_criteria:
            return 0
        return self.win_criteria.total_items

    @classmethod
    def from_dict(cls, dict: dict):
        mine = Mine(dict["name"], dict["type"])
        mine.min_player_level = dict["min_player_level"]
        mine.cost = dict["cost"]
        mine.character_levels = dict["character_levels"]
        mine.enemies = dict["enemies"]
        mine.max_enemy_items = dict["max_enemy_items"]
        mine.max_item_level = dict["max_item_level"]
        mine.max_enemy_item_level = dict["max_enemy_item_level"]
        mine.enemy_item_scale = dict.get("enemy_item_scale", 1)
        mine.odds = dict["odds"]
        mine.exp_boost = dict.get("exp_boost", 0)
        mine.win_criteria = (
            MineStats.from_dict(dict["win_criteria"]) if "win_criteria" in dict else None
        )
        mine.resource = dict["resource"] if "resource" in dict else None
        mine.companion_rarity = dict.get("companion_rarity", 0)
        return mine

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "min_player_level": self.min_player_level,
            "cost": self.cost,
            "character_levels": self.character_levels,
            "enemies": self.enemies,
            "max_enemy_items": self.max_enemy_items,
            "max_item_level": self.max_item_level,
            "max_enemy_item_level": self.max_enemy_item_level,
            "enemy_item_scale": self.enemy_item_scale,
            "odds": self.odds,
            "type": self.type,
            "exp_boost": self.exp_boost,
            "win_criteria": self.win_criteria.to_dict() if self.win_criteria else None,
            "resource": self.resource,
            "companion_rarity": self.companion_rarity,
        }

    @property
    def icon(self):
        match self.type:
            case MineType.REGULAR:
                return Icons.MINERAL
            case MineType.COMBAT:
                return Icons.WEAPON
            case MineType.RESOURCE:
                return Icons.RESOURCE
            case _:
                return Icons.UNKNOWN

    def get_action_odds(self, action: str):
        for odd in self.odds:
            if odd["action"] == action:
                return odd["chance"]
        return 0

    @property
    def complete(self) -> bool:
        if self.win_criteria is None:
            return False
        return (
            self.player_progress.minerals >= self.win_criteria.minerals
            and self.player_progress.kills >= self.win_criteria.kills
            and self.player_progress.minutes >= self.win_criteria.minutes
        )

    @property
    def progress_bar(self):
        current = (
            min(self.player_progress.minerals, self.win_criteria.minerals)
            + min(self.player_progress.kills, self.win_criteria.kills)
            + min(self.player_progress.minerals, self.win_criteria.minutes)
        )
        return ProgressBar(total=self.win_criteria.total_items, completed=current, width=20)

    @property
    def progress(self):
        table = Table.grid(padding=(0, 1, 0, 0))
        if self.win_criteria:
            table.add_row("Progress:", self.progress_bar)
            table.add_row(
                "Minerals:",
                remaining_str(self.player_progress.minerals, self.win_criteria.minerals),
            )
            table.add_row(
                "Kills:",
                remaining_str(self.player_progress.kills, self.win_criteria.kills),
            )
            table.add_row(
                "Minutes Survived:",
                remaining_str(int(self.player_progress.minutes), int(self.win_criteria.minutes)),
            )
        return table

    @property
    def has_death_action(self):
        return bool(self.get_action_odds("lose_ally"))

    def __str__(self) -> str:
        death_str = Icons.DEATH if self.has_death_action else ""
        return f"{self.icon} {self.name} {death_str}"

    @property
    def death_chance_str(self):
        odds = self.get_action_odds("lose_ally")
        chances = {
            -1: "[green1]none[/]",
            0: "[green_yellow]low[/]",
            0.5: "[yellow1]medium[/]",
            0.7: "[orange1]high[/]",
            1: "[red1]very high[/]",
        }
        closest_key_floor = max(c for c in chances if c < odds)
        return f"{Icons.DEATH} {chances[closest_key_floor]}"

    @property
    def arr(self):
        arr = [self.icon, self.name, self.death_chance_str]
        if self.win_criteria:
            if self.complete:
                arr.append("✨ cleared ✨")
            else:
                arr.append(self.progress_bar)
        return arr

    def get_unlock_arr(self, player_level: int):
        if player_level < self.min_player_level:
            return [
                self.icon,
                Formatter.locked(f"{Icons.LOCKED} {self.name} "),
                Text.from_markup(Formatter.locked(f"{self.cost:,}g"), justify="right"),
                Formatter.locked(f"{Icons.LEVEL} {self.min_player_level} "),
                Formatter.locked(f"{int(self.exp_boost * 100):2}% xp") if self.exp_boost else "",
                Formatter.locked(Text.from_markup(self.death_chance_str).plain),
            ]
        return [
            self.icon,
            self.name,
            Text.from_markup(Formatter.gold(self.cost), justify="right"),
            f"{Icons.LEVEL} {Formatter.level(self.min_player_level)}",
            f"[{Colors.XP}]{int(self.exp_boost*100):2}% xp[/]" if self.exp_boost else "",
            self.death_chance_str,
        ]


def remaining_str(current: int, total: int):
    return f"{current}/{total}" if current < total else "Complete"
