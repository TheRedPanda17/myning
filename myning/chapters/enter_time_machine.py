from blessed import Terminal

from myning.config import XP_COST
from myning.objects.garden import Garden
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.singleton import Singleton
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.ui import columnate
from myning.utils.ui_consts import Icons

term = Terminal()


def play():
    player = Player()
    macguffin = Macguffin()

    value = get_total_value()
    standard_boost = macguffin.get_new_standard_boost(value)
    small_boost = macguffin.get_new_smaller_boost(value)

    while True:
        option, _ = pick(
            ["View Potential Macguffin", "Go Back in Time", "About", "Go Back"],
            "What would you like to do?",
        )

        if option == "Go Back":
            return

        if option == "Go Back in Time":
            journal = player.discovered_species
            migrations = player.completed_migrations
            option, _ = pick(
                ["Yes", "No"],
                "Are you sure you want to erase ALL progress and go back in time?",
                sub_title=f"You'll lose all your progress and gain a {int(standard_boost*100)}% xp and mineral value boost"
                + f"\nand a {int(small_boost*100)}% research, soul credit boost, and plant value.",
            )

            if option == "No":
                continue

            player_name = player.name
            player_id = player.id

            # Reset the game
            FileManager.backup_game()
            FileManager.reset_game()
            Singleton.reset()

            Player.initialize(player_name)
            player = Player()
            player.discovered_species = journal
            player.completed_migrations = migrations
            player.id = player_id

            Macguffin.initialize()
            macguffin = Macguffin()
            macguffin.xp_boost = standard_boost
            macguffin.mineral_boost = standard_boost
            macguffin.research_boost = small_boost
            macguffin.soul_credit_boost = small_boost
            macguffin.plant_boost = small_boost

            FileManager.multi_save(player, macguffin)

            # Janky, but this will exit to the run.sh loop which will reboot the game. Basically purges the memory of the game.
            exit(123)

        if option == "View Potential Macguffin":
            value = get_total_value()
            standard_boost_str = f"{round(standard_boost * 100, 2)}%"
            small_boost_str = f"{round(small_boost * 100, 2)}%"

            boost_str = (
                term.underline("Potential Macguffin Boosts")
                + "\n"
                + "\n".join(
                    columnate(
                        [
                            [
                                "Mineral value:",
                                f"{Icons.MINERAL} {term.gold(standard_boost_str)}",
                            ],
                            [
                                "XP gain:",
                                f"{Icons.XP} {term.magenta(standard_boost_str)}",
                            ],
                            [
                                "Soul credits:",
                                f"{Icons.GRAVEYARD} {term.blue(small_boost_str)}",
                            ],
                            [
                                "Research speed:",
                                f"{Icons.RESEARCH_FACILITY} {term.violetred1(small_boost_str)}",
                            ],
                            [
                                "Plant value:",
                                f"{Icons.PLANT} {term.green(small_boost_str)}",
                            ],
                        ]
                    )
                )
            )
            pick(["Cool cool cool"], boost_str)

        if option == "About":
            pick(
                ["I understand"],
                "Going Back in Time",
                sub_title="When you go back in time, you will gain a macguffin which \n"
                "will provide an xp, mineral value, soul credit, research, and plant \n"
                "value boost. Unfortunately, you'll lose everything else you have \n"
                "(including upgrades). Journal unlocks will not be lost.",
            )
            continue


# This is the same function as in the stats page. I haven't figured
# out a great place where they can share this function and I don't
# want to cross import
def get_total_value() -> int:
    player = Player()
    facility = ResearchFacility()
    garden = Garden()

    return player.total_value + facility.total_value + garden.total_value
