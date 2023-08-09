from myning.chapters import visit_store
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.store import Store
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.ui import get_gold_string


def play():
    player = Player()
    macguffin = Macguffin()
    store = Store(player.level)
    store.generate()

    while True:
        option, _ = pick(
            ["Buy", "Sell", "Go Back"],
            f"What would you like to do? ({get_gold_string(player.gold)})",
        )
        if option == "Buy" and (bought_items := visit_store.buy(store.inventory.items, player)):
            for item in bought_items:
                store.inventory.remove_item(item)
                player.inventory.add_item(item)
                FileManager.save(item)
        elif option == "Sell":
            bonus_ratio = macguffin.mineral_boost
            sold_items, price = visit_store.sell(
                player.inventory.items,
                player.has_upgrade("sell_minerals"),
                player.has_upgrade("sell_almost_everything"),
                player.has_upgrade("sell_everything"),
                bonus_ratio,
            )
            if not sold_items or price is None:
                continue
            for sold_item in sold_items:
                player.inventory.remove_item(sold_item)
                store.inventory.add_item(sold_item)
            player.gold += price
        elif option == "Go Back":
            FileManager.multi_delete(*store.inventory.items)
            break
