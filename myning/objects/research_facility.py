from datetime import datetime

from blessed import Terminal

from myning.config import RESEARCH
from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.object import Object
from myning.objects.singleton import Singleton
from myning.objects.upgrade import Upgrade
from myning.utils import utils
from myning.utils.file_manager import FileManager

term = Terminal()


class ResearchFacility(Object, metaclass=Singleton):
    @classmethod
    def initialize(cls):
        facility = FileManager.load(ResearchFacility, cls.file_name)
        if not facility:
            facility = cls()
        cls._instance = facility

    def __init__(
        self,
        level: int = 1,
        points: int = 0,
        last_research_tick: datetime | None = None,
        researchers: list[Character] | None = None,
        research: list[Upgrade] | None = None,
    ):
        self.level = level
        self._points = points
        self.last_research_tick = last_research_tick
        self._researchers = researchers or []
        self._research = research or []

        if len(self._researchers) > level:
            raise Exception("Too many researchers for this level")

    @classmethod
    @property
    def file_name(cls):
        return "research_facility"

    @property
    def army(self):
        return Army(self._researchers)

    @property
    def points(self):
        return round(self._points, 2)

    @property
    def research(self):
        return self._research

    def to_dict(self):
        return {
            "level": self.level,
            "points": self._points,
            "last_research_tick": self.last_research_tick.isoformat()
            if self.last_research_tick
            else None,
            "researchers": [ally.to_dict() for ally in self._researchers],
            "research": [
                {"id": research.id, "level": research.level} for research in self._research
            ],
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return ResearchFacility(1)

        researched = []
        for research in data.get("research") or []:
            id = research["id"] if isinstance(research, dict) else research
            level = research["level"] if isinstance(research, dict) else 1
            researched.append(RESEARCH[id])
            researched[-1].level = level

        return ResearchFacility(
            data["level"],
            data["points"],
            datetime.strptime(data["last_research_tick"], "%Y-%m-%dT%H:%M:%S.%f")
            if data.get("last_research_tick")
            else None,
            [Character.from_dict(ally) for ally in data["researchers"]],
            researched,
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
        return self.get_upgrade_cost(self.level + 1)

    def get_upgrade_cost(self, level):
        return utils.fibonacci(level) * 5

    @property
    def total_value(self):
        research = sum(sum(cost for cost in u.costs[: u.level]) for u in self.research) * 5
        facility = sum(self.get_upgrade_cost(level) for level in range(1, self.level)) * 5

        return research + facility

    def points_per_hour(self, bonus: float):
        ticks_per_hour = 60 / self.minutes_per_tick
        return ticks_per_hour * self.points_per_researcher * len(self._researchers) * bonus

    def check_in(self, bonus: float):
        if not self.last_research_tick:
            self.last_research_tick = datetime.now()
            return

        mins_since_last_tick = (datetime.now() - self.last_research_tick).total_seconds() / 60
        tick_completion = mins_since_last_tick / self.minutes_per_tick

        earned = self.points_per_researcher * len(self._researchers) * tick_completion
        self._points += earned * bonus
        self.last_research_tick = datetime.now()

    def tick(self):
        self._points += self.points_per_researcher * len(self._researchers)
        self.last_research_tick = datetime.now()

    def level_up(self):
        self.level += 1

    def add_researcher(self, researcher: Character):
        self._researchers.append(researcher)

    def remove_researcher(self, researcher: Character):
        self._researchers.remove(researcher)

    def purchase(self, cost):
        if cost > 0:
            self._points -= cost

    def has_research(self, research_id):
        return research_id in [research.id for research in self._research]
