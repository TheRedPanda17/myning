from functools import partial

from myning.chapters import Option, PickArgs, main_menu
from myning.objects.character import Character
from myning.objects.graveyard import Graveyard
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.stats import FloatStatKeys, Stats
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import confirm

player = Player()
macguffin = Macguffin()
graveyard = Graveyard()
stats = Stats()


def enter():
    if not graveyard.fallen_allies:
        return PickArgs(
            message="You have no fallen allies to revive.",
            options=[Option("Bummer", main_menu.enter)],
        )
    member_arrs = [member.abbreviated_arr[:-1] for member in graveyard.fallen_allies]
    handlers = [partial(action, member) for member in graveyard.fallen_allies]
    options = [Option(label, handler) for label, handler in zip(member_arrs, handlers)]
    return PickArgs(
        message="Select a fallen ally to revive or lay to rest",
        options=[
            *options,
            Option(["", "Go Back"], main_menu.enter),
        ],
        column_titles=player.abbreviated_column_titles[:-1],
    )


def action(member: Character):
    soul_cost = get_soul_cost()
    gold_cost = get_gold_cost(member)
    return PickArgs(
        message=f"Select an option for {member.icon} {member.name}",
        options=[
            Option(
                [
                    "Revive",
                    f"[bold red1]-{Formatter.soul_credits(soul_cost)}",
                    Formatter.gold(gold_cost),
                ],
                partial(revive, member),
                enable_hotkeys=True,
            ),
            Option(
                [
                    "Lay to Rest",
                    f"[bold green1]+{Formatter.soul_credits(macguffin.soul_credit_boost)}",
                ],
                partial(lay_to_rest, member),
                enable_hotkeys=True,
            ),
            Option("Go Back", enter),
        ],
    )


def validate_revive(member: Character):
    soul_cost = get_soul_cost()
    gold_cost = get_gold_cost(member)
    if graveyard.soul_credits < soul_cost:
        return PickArgs(
            message="You don't have enough soul credits! Send fallen allies to the afterlife "
            "(where their souls can rest) to earn more.",
            options=[Option("Bummer!", enter)],
        )
    if player.gold < gold_cost:
        return PickArgs(
            message="You don't have enough gold.",
            options=[Option("Bummer!", enter)],
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
    graveyard.remove_soul_credits(soul_cost)
    player.gold -= gold_cost
    member.is_ghost = True
    player.revive_ally(member)
    graveyard.remove_fallen_ally(member)
    FileManager.multi_save(player, member, graveyard)
    return enter()


@confirm(
    f"Send {{0.icon}} {{0.name}} to the afterlife and gain "
    f"{Formatter.soul_credits(macguffin.soul_credit_boost)} for letting their soul rest?",
    enter,
)
def lay_to_rest(member: Character, /):
    graveyard.add_soul_credits(macguffin.soul_credit_boost)
    graveyard.remove_fallen_ally(member)
    stats.increment_float_stat(FloatStatKeys.SOUL_CREDITS_EARNED, macguffin.soul_credit_boost)
    FileManager.multi_save(player, stats, graveyard)
    return enter()


def get_soul_cost():
    return int(player.ghost_count * 1.1)


def get_gold_cost(member: Character):
    return int(member.value * 0.75 + member.level * 100)
