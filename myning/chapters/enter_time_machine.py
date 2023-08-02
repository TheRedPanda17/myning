import math

from blessed import Terminal

from myning.chapters.enter_blacksmith import smith_cost
from myning.config import XP_COST
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.io import pick

term = Terminal()


def play():
    player = Player()

    value = get_total_value()
    xp_boost = get_boost(player.macguffin.exp_boost, value)
    mineral_boost = get_boost(player.macguffin.mineral_boost, value)

    while True:
        option, _ = pick(
            ["View Potential Macguffin", "Go Back in Time", "About", "Go Back"],
            "What would you like to do?",
        )

        if option == "Go Back":
            return

        if option == "Go Back in Time":
            journal = player.discovered_races
            migrations = player.completed_migrations
            option, _ = pick(
                ["Yes", "No"],
                "Are you sure you want to erase ALL progress and go back in time?",
                sub_title=f"You'll lose all your progress and gain a {int(xp_boost*100)}% xp boost \nand a {int(mineral_boost*100)}% mineral value boost.",
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
            player.macguffin.exp_boost = xp_boost
            player.macguffin.mineral_boost = mineral_boost
            player.discovered_races = journal
            player.completed_migrations = migrations
            FileManager.save(player)

            Settings.initialize()
            FileManager.save(settings)

            # Janky, but this will exit to the run.sh loop which will reboot the game. Basically purges the memory of the game.
            exit(123)

        if option == "View Potential Macguffin":
            value = get_total_value()
            xp_boost_str = str(xp_boost * 100) + "%"
            mineral_boost_str = str(mineral_boost * 100) + "%"
            boost_str = f"Potential xp boost: {term.magenta(xp_boost_str)}"
            boost_str += f"\nPotential mineral value boost: {term.gold(mineral_boost_str)}"
            pick(["Cool cool cool"], boost_str)

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


def get_boost(current_boost: int, game_value: int) -> int:
    return round((game_value / 500000) + current_boost, 2)


def get_total_value() -> int:
    player = Player()
    facility = ResearchFacility()

    item_value = sum(item.value for item in player.inventory.items)
    army_value = sum(member.value for member in player.army)
    exp_value = player.exp_available * XP_COST
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
