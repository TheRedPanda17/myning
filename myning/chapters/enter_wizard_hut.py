from myning.config import UPGRADES
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.ui import columnate


def play():
    player = Player()

    while True:
        purchased_upgrades = [upgrade for upgrade in UPGRADES.values() if upgrade.level > 0]
        purchased_str = "\n  ".join(
            columnate([upgrade.player_arr for upgrade in purchased_upgrades])
        )

        available_upgrades = [upgrade for upgrade in UPGRADES.values() if not upgrade.max_level]
        options = columnate([upgrade.string_arr for upgrade in available_upgrades])
        option, index = pick(
            [*options, "Go Back"],
            "What wondrous, magical upgrades would you like to buy from the wizard?",
            sub_title=f"Purchased upgrades:\n  {purchased_str}",
        )
        if option == "Go Back":
            return

        upgrade = available_upgrades[index]
        if player.pay(
            upgrade.cost,
            failure_msg="You don't have enough gold to buy this upgrade",
            failure_option="Bummer!",
            confirmation_msg=f"Are you sure you want to buy {upgrade.name}?",
        ):
            upgrade.level += 1
            if upgrade.id not in [u.id for u in player.upgrades]:
                player.upgrades.append(upgrade)
            FileManager.save(player)
