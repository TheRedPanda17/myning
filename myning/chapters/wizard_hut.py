from functools import partial

from rich.table import Table

from myning.chapters import Option, PickArgs, main_menu
from myning.config import UPGRADES
from myning.formatter import Colors, Formatter
from myning.objects.player import Player
from myning.objects.upgrade import Upgrade
from myning.utils.file_manager import FileManager

player = Player()


def enter():
    available_upgrades = [upgrade for upgrade in UPGRADES.values() if not upgrade.max_level]
    options: list[Option] = [(u.arr, partial(confirm_buy, u)) for u in available_upgrades]
    options.append(("Go Back", main_menu.enter))

    purchased_upgrades = [upgrade for upgrade in UPGRADES.values() if upgrade.level > 0]
    subtitle = Table.grid(padding=(0, 1, 0, 0))
    subtitle.add_column(style=Colors.LOCKED)
    subtitle.add_column(style=Colors.LOCKED)
    subtitle.add_row("\nPurchased upgrades:")
    for upgrade in purchased_upgrades:
        subtitle.add_row(f"  {upgrade.player_name}", upgrade.player_description)

    return PickArgs(
        message="What wondrous, magical upgrades would you like to buy from the wizard?",
        options=options,
        subtitle=subtitle if purchased_upgrades else None,
    )


def confirm_buy(upgrade: Upgrade):
    if player.gold < upgrade.cost:
        return PickArgs(
            message="You don't have enough gold to buy this upgrade",
            options=[("Bummer!", enter)],
        )
    return PickArgs(
        message=f"Are you sure you want to buy {upgrade.name} for {Formatter.gold(upgrade.cost)}?",
        options=[
            ("Yes", partial(buy, upgrade)),
            ("No", enter),
        ],
    )


def buy(upgrade: Upgrade):
    player.gold -= upgrade.cost
    upgrade.level += 1
    if upgrade.id not in [u.id for u in player.upgrades]:
        player.upgrades.append(upgrade)
    FileManager.save(player)
    return enter()
