from myning.objects.character import Character
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.stats import FloatStatKeys, Stats
from myning.utils.file_manager import FileManager
from myning.utils.io import confirm, pick
from myning.utils.ui import columnate, get_gold_string, get_soul_string


def play():
    player = Player()

    while True:
        if not player.fallen_allies:
            pick(["Bummer!"], "\nYou have no fallen allies to revive.")
            return

        options = columnate(
            [
                [
                    entity.icon,
                    entity.name,
                    entity.level_str,
                    f"⚔️ {entity.stats['damage']}",
                    f"🛡️ {entity.stats['armor']}",
                    f"❤️‍ {entity.health_mod} ",
                    get_soul_string(soul_cost(player.ghost_count)),
                    get_gold_string(gold_cost(entity)),
                ]
                for entity in player.fallen_allies
            ]
        )

        option, i = pick(
            [*options, "Go Back"],
            f"Select a fallen ally to revive or lay to rest ({get_soul_string(player.soul_credits)})",
        )
        if option == "Go Back":
            return None

        ally = player.fallen_allies[i]
        option, _ = pick(["Revive", "Lay to Rest", "Go Back"])

        if option == "Go Back":
            continue
        elif option == "Revive":
            revive(player, ally)
        elif option == "Lay to Rest":
            lay_to_rest(player, ally)


def lay_to_rest(player: Player, ally: Character):
    macguffin = Macguffin()
    stats = Stats()
    confirmation = confirm(
        message=f"Send {ally.icon} {ally.name} to the afterlife and gain {get_soul_string(macguffin.soul_credit_boost)} for letting their soul rest?"
    )

    if confirmation:
        player.add_soul_credits(macguffin.soul_credit_boost)
        stats.increment_float_stat(FloatStatKeys.SOUL_CREDITS_EARNED, macguffin.soul_credit_boost)
        player.remove_fallen_ally(ally)
        FileManager.multi_save(stats, player)


def revive(player: Player, ally: Character):
    cost = soul_cost(player.ghost_count)
    gold = gold_cost(ally)
    if cost > player.soul_credits:
        pick(
            ["Bummer!"],
            "You don't have enough soul credits! Send fallen allies to the afterlife (where their souls can rest) to earn more.",
        )
        return

    if player.pay(
        gold,
        confirmation_msg=f"Revive {ally.name} for {get_soul_string(cost)} and {get_gold_string(gold)}?",
        failure_msg="You don't have enough gold.",
        failure_option="Bummer!",
    ):
        ally.is_ghost = True
        player.revive_ally(ally)
        player.remove_soul_credits(cost)
        FileManager.multi_save(player, ally)


def soul_cost(ghost_count: int) -> int:
    return int(ghost_count * 1.1)


def gold_cost(ally: Character):
    return int(ally.value * 0.75 + ally.level * 100)
