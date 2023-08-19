from functools import partial

from myning.objects.character import Character
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.stats import FloatStatKeys, Stats
from myning.utils.file_manager import FileManager
from new_tui.chapters import PickArgs, main_menu
from new_tui.formatter import Formatter
from new_tui.utilities import confirm

player = Player()
macguffin = Macguffin()
stats = Stats()


def enter():
    if not player.fallen_allies:
        return PickArgs(
            message="You have no fallen allies to revive.",
            options=[("Bummer", main_menu.enter)],
        )
    member_arrs = [member.abbreviated_tui_arr[:-1] for member in player.fallen_allies]
    handlers = [partial(action, member) for member in player.fallen_allies]
    options = list(zip(member_arrs, handlers))
    return PickArgs(
        message="Select a fallen ally to revive or lay to rest",
        options=[
            *options,
            (["", "Go Back"], main_menu.enter),
        ],
        column_titles=player.abbreviated_tui_column_titles[:-1],
    )


def action(member: Character):
    soul_cost = get_soul_cost()
    gold_cost = get_gold_cost(member)
    return PickArgs(
        message=f"Select an option for {member.icon} {member.name}",
        options=[
            (
                [
                    "Revive",
                    f"[bold red1]-{Formatter.soul_credits(soul_cost)}",
                    Formatter.gold(gold_cost),
                ],
                partial(revive, member),
            ),
            (
                [
                    "Lay to Rest",
                    f"[bold green1]+{Formatter.soul_credits(macguffin.soul_credit_boost)}",
                ],
                partial(lay_to_rest, member),
            ),
            ("Go Back", enter),
        ],
    )


def validate_revive(member: Character):
    soul_cost = get_soul_cost()
    gold_cost = get_gold_cost(member)
    if player.soul_credits < soul_cost:
        return PickArgs(
            message="You don't have enough soul credits! Send fallen allies to the afterlife "
            "(where their souls can rest) to earn more.",
            options=[("Bummer!", enter)],
        )
    if player.gold < gold_cost:
        return PickArgs(
            message="You don't have enough gold.",
            options=[("Bummer!", enter)],
        )
    return None


@confirm(
    lambda member: f"Revive {member.icon} {member.name} for "
    f"{Formatter.soul_credits(get_soul_cost())} and {Formatter.gold(get_gold_cost(member))}?",
    enter,
    validate_revive,
)
def revive(member: Character, /):
    soul_cost = get_soul_cost()
    gold_cost = get_gold_cost(member)
    player.remove_soul_credits(soul_cost)
    player.gold -= gold_cost
    member.is_ghost = True
    player.revive_ally(member)
    FileManager.multi_save(player, member)
    return enter()


@confirm(
    f"Send {{0.icon}} {{0.name}} to the afterlife and gain "
    f"{Formatter.soul_credits(macguffin.soul_credit_boost)} for letting their soul rest?",
    enter,
)
def lay_to_rest(member: Character, /):
    player.add_soul_credits(macguffin.soul_credit_boost)
    player.remove_fallen_ally(member)
    stats.increment_float_stat(FloatStatKeys.SOUL_CREDITS_EARNED, macguffin.soul_credit_boost)
    FileManager.multi_save(player, stats)
    return enter()


def get_soul_cost():
    return int(player.ghost_count * 1.1)


def get_gold_cost(member: Character):
    return int(member.value * 0.75 + member.level * 100)
