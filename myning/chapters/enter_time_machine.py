import math

from blessed import Terminal

from myning.chapters.enter_blacksmith import smith_cost
from myning.config import EXP_COST
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.io import pick

term = Terminal()


def play():
    while True:
        option, _ = pick(
            ["Go Back in Time", "View Current Macguffin", "About", "Go Back"],
            "What would you like to do?",
        )
        player = Player()

        if option == "Go Back":
            return

        if option == "Go Back in Time":
            value = get_total_value()
            exp_boost = round((value / 500000) + player.macguffin.exp_boost, 2)
            mineral_boost = round((value / 500000) + player.macguffin.mineral_boost, 2)
            journal = player.discovered_races
            option, _ = pick(
                ["Yes", "No"],
                "Are you sure you want to erase ALL progress and go back in time?",
                sub_title=f"You'll lose all your progress and gain a {int(exp_boost*100)}% xp boost \nand a {int(mineral_boost*100)}% mineral value boost.",
            )
            settings = Settings()

            if option == "No":
                continue

            player_name = player.name

            # Reset the game
            FileManager.backup_game()
            FileManager.reset_game()
            Singleton.reset()

            Player.initialize(player_name)
            player = Player()
            player.macguffin.exp_boost = exp_boost
            player.macguffin.mineral_boost = mineral_boost
            player.discovered_races = journal
            FileManager.save(player)

            Settings.initialize()
            FileManager.save(settings)

            # Janky, but this will exit to the run.sh loop which will reboot the game. Basically purges the memory of the game.
            exit(123)

        if option == "View Current Macguffin":
            pick(
                ["Cool cool cool"],
                f"XP boost: {player.macguffin.exp_percentage} Mineral value boost: {player.macguffin.store_percentage}",
            )

        if option == "About":
            pick(
                ["I understand"],
                "Going Back in Time",
                sub_title="When you go back in time, you will gain a macguffin which \n"
                "will provide an xp and mineral value boost. Unfortunately, \n"
                "you'll lose everything else you have (including upgrades).\n"
                "Journal unlocks will not be lost.",
            )
            continue


def get_total_value() -> int:
    player = Player()
    facility = ResearchFacility()

    item_value = sum(item.value for item in player.inventory.items)
    army_value = sum(member.value for member in player.army)
    exp_value = player.exp_available * EXP_COST
    upgrades_value = sum(sum(cost for cost in u.costs[: u.level]) for u in player.upgrades)
    blacksmith_cost = sum(smith_cost(level) for level in range(1, player.blacksmith_level + 1))
    unlocked_mines = sum(mine.cost for mine in player.mines_available)
    beaten_mines = sum(
        mine.win_value * math.pow(mine.cost, 1 / 3) for mine in player.mines_completed
    )
    research = sum(sum(cost for cost in u.costs[: u.level]) for u in facility.research) * 5
    research_facility = sum(smith_cost(level) for level in range(1, facility.level + 1)) * 5

    return (
        item_value
        + army_value
        + player.gold
        + exp_value
        + upgrades_value
        + blacksmith_cost
        + unlocked_mines
        + beaten_mines
        + research
        + research_facility
    )
