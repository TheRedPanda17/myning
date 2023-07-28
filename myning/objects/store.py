from blessed.terminal import Terminal

from myning.objects.inventory import Inventory
from myning.utils.generators import generate_equipment

term = Terminal()


class Store:
    def __init__(self, level=0):
        self.level = level
        self.inventory = Inventory()

    def generate(self):
        item_count = max(self.level, 5)
        for _ in range(item_count):
            self.inventory.add_item(generate_equipment(self.level))
