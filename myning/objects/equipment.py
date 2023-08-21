
from myning.objects.item import Item, ItemType
from myning.utilities.file_manager import FileManager


EQUIPMENT_TYPES = [
    item_type
    for item_type in ItemType
    if item_type is not ItemType.MINERAL and item_type is not ItemType.PLANT
]

Slots = dict[ItemType, Item | None]


class Equipment:
    def __init__(self, slots: Slots | None = None):
        if slots is None:
            self._slots: Slots = {category: None for category in EQUIPMENT_TYPES}
        else:
            self._slots = slots

    @property
    def all_items(self):
        return [item for item in self._slots.values() if item]

    def clear(self):
        self._slots = {category: None for category in EQUIPMENT_TYPES}

    def get_slot_item(self, slot):
        return self._slots[slot]

    def equip(self, slot, item):
        self._slots[slot] = item

    @property
    def stats(self):
        _stats = {
            "damage": 0,
            "armor": 0,
        }
        for category in EQUIPMENT_TYPES:
            item = self._slots[category]
            if not item:
                continue

            for affect_name, value in item.affects.items():
                if _stats.get(affect_name):
                    _stats[affect_name] += value
                else:
                    _stats[affect_name] = value

        return _stats

    def to_dict(self) -> dict:
        dict = {}
        for type_name, item in self._slots.items():
            dict[type_name] = item.id if item else None
        return dict

    @classmethod
    def from_dict(cls, dict: dict):
        equipment = Equipment(
            {
                category: FileManager.load(Item, dict[category], "items")
                if dict[category]
                else None
                for category in EQUIPMENT_TYPES
            }
        )
        return equipment

    def change_item(self, slot, item):
        self._slots[slot] = item
