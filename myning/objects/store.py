
from myning.objects.item import Item
from myning.utilities.generators import generate_equipment



class Store:
    def __init__(self, level=0):
        self.level = level
        self._items: list[Item] = []

    def generate(self):
        item_count = max(self.level, 5)
        for _ in range(item_count):
            self.add_item(generate_equipment(self.level))

    def add_item(self, item: Item):
        self._items.append(item)

    def add_items(self, items: list[Item]):
        for item in items:
            self.add_item(item)

    def remove_item(self, item: Item):
        if item in self._items:
            self._items.remove(item)

    @property
    def items(self):
        return list(sorted(self._items, key=lambda i: i.type))

    @property
    def items_by_value(self):
        return list(sorted(self._items, key=lambda i: i.value))

    @property
    def empty(self):
        return len(self._items) == 0
