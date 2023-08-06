from myning.objects.object import Object


class MineStats(Object):
    def __init__(self, minutes: float, kills: int, minerals: int):
        self.minutes = minutes
        self.kills = kills
        self.minerals = minerals

    @classmethod
    def from_dict(cls, dict: dict):
        return MineStats(dict["minutes"], dict["kills"], dict["minerals"])

    def to_dict(self) -> dict:
        return {
            "minutes": self.minutes,
            "kills": self.kills,
            "minerals": self.minerals,
        }

    @property
    def total_items(self) -> int:
        return self.minerals + self.kills + self.minutes
