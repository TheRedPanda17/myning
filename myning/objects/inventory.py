from typing import Literal, overload

from myning.objects.item import Item, ItemType
from myning.objects.plant import Plant
from myning.utilities.file_manager import FileManager, Subfolders


class Inventory:
    def __init__(self):
        self._items: dict[ItemType, list[Item]] = {}

    def add_item(self, item: Item):
        if item.type in self._items:
            self._items[item.type].append(item)
        else:
            self._items[item.type] = [item]

    def add_items(self, items: list[Item]):
        for item in items:
            self.add_item(item)

    def remove_item(self, item: Item):
        if item.type in self._items and item in self._items[item.type]:
            self._items[item.type].remove(item)

    def remove_items(self, *items: Item):
        for item in items:
            if item.type in self._items and item in self._items[item.type]:
                self._items[item.type].remove(item)

    @overload
    def get_slot(self, slot: Literal[ItemType.PLANT]) -> list[Plant]:
        ...

    @overload
    def get_slot(self, slot: ItemType) -> list[Item]:
        ...

    def get_slot(self, slot) -> list[Item] | list[Plant]:
        return self._items.get(slot, [])

    def has_better_item(self, slot: ItemType, current: Item | None):
        if slot_items := self.get_slot(slot):
            if current:
                # pylint: disable=not-an-iterable
                return any(item for item in slot_items if item.main_affect > current.main_affect)
            return True
        return False

    def get_best_in_slot(self, slot: ItemType):
        if slot_items := self.get_slot(slot):
            return max(slot_items, key=lambda item: item.main_affect)
        return None

    @property
    def items(self):
        return [item for type in self._items for item in self._items[type]]

    def to_dict(self) -> dict:
        dict = {}
        for type_name, type in self._items.items():
            dict[type_name] = []
            for item in type:
                dict[type_name].append(item.id)
        return dict

    @classmethod
    def from_dict(cls, dict: dict):
        inventory = Inventory()
        for type_name, type in dict.items():
            inventory._items[type_name] = []
            for item_id in type:
                icls = Plant if type_name == ItemType.PLANT.value else Item
                fetched = FileManager.load(icls, item_id, Subfolders.ITEMS)
                if fetched:
                    inventory._items[type_name].append(fetched)
        return inventory
