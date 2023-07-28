from myning.objects.object import Object


class Macguffin(Object):
    def __init__(self, exp_boost=1, mineral_boost=1):
        self.exp_boost = exp_boost
        self.mineral_boost = mineral_boost

    @classmethod
    def from_dict(cls, data) -> "Macguffin":
        if data is None:
            return Macguffin()
        return Macguffin(data["exp_boost"], data["store_boost"])

    def to_dict(self) -> dict:
        return {
            "exp_boost": self.exp_boost,
            "store_boost": self.mineral_boost,
        }

    @property
    def exp_percentage(self):
        return f"{int(self.exp_boost * 100)}%"

    @property
    def store_percentage(self):
        return f"{int(self.mineral_boost * 100)}%"
