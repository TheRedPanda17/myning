from datetime import datetime

from blessed import Terminal

from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.object import Object
from myning.utils import utils

term = Terminal()


class ResearchFacility(Object):
    def __init__(
        self,
        level: int = 1,
        points: int = 0,
        last_research_tick: datetime = None,
        researchers: list[Character] = None,
    ):
        self.level = level
        self._points = points
        self.last_research_tick = last_research_tick
        self._researchers = researchers if researchers else []

        if len(self._researchers) > level:
            raise Exception("Too many researchers for this level")

    @property
    def army(self):
        return Army(self._researchers)

    @property
    def points(self):
        return round(self._points, 2)

    def to_dict(self):
        return {
            "level": self.level,
            "points": self._points,
            "last_research_tick": self.last_research_tick.isoformat()
            if self.last_research_tick
            else None,
            "researchers": [ally.to_dict() for ally in self._researchers],
        }

    @classmethod
    def from_dict(cls, dict: dict):
        if not dict:
            return ResearchFacility(1)
        return ResearchFacility(
            dict["level"],
            dict["points"],
            datetime.strptime(dict["last_research_tick"], "%Y-%m-%dT%H:%M:%S.%f")
            if dict.get("last_research_tick")
            else None,
            [Character.from_dict(ally) for ally in dict["researchers"]],
        )

    @property
    def minutes_per_tick(self):
        return 60 / (1 + ((self.level - 1) / 50))

    @property
    def points_per_researcher(self):
        return 1 + (self.level / 50)

    @property
    def has_free_space(self):
        return len(self._researchers) < self.level

    @property
    def upgrade_cost(self):
        return utils.fibonacci(self.level + 1) * 5

    @property
    def points_per_hour(self):
        ticks_per_hour = 60 / self.minutes_per_tick
        return ticks_per_hour * self.points_per_researcher * len(self._researchers)

    def check_in(self):
        if not self.last_research_tick:
            self.last_research_tick = datetime.now()
            return

        mins_since_last_tick = (datetime.now() - self.last_research_tick).total_seconds() / 60
        tick_completion = mins_since_last_tick / self.minutes_per_tick

        self._points += self.points_per_researcher * len(self._researchers) * tick_completion
        self.last_research_tick = datetime.now()

    def tick(self):
        self._points += self.points_per_researcher * len(self._researchers)
        self.last_research_tick = datetime.now()

    def level_up(self):
        self.level += 1

    def add_researcher(self, researcher: Character):
        self._researchers.append(researcher)

    def remover_researcher(self, researcher: Character):
        self._researchers.remove(researcher)

    def purchase(self, cost):
        if cost > 0:
            self._points -= cost
