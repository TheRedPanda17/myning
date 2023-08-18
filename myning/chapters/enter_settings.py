from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.utils.file_manager import FileManager
from myning.utils.io import get_int_input, pick
from myning.utils.ui import columnate


def play():
    settings = Settings()
    player = Player()

    while True:
        options = [
            ["Army Column Height", f"({settings.army_columns})"],
            ["Mini-Games", f"({settings.mini_games_status})"],
            ["Combat Mode", f"({settings.hard_combat_status})"],
            ["Compact Mode", f"({settings.compact_status})"],
        ]
        if player.has_upgrade("sort_by_value"):
            options.append(["Sort Order", f"({settings.sort_order})"])

        options = columnate(options)

        options.append("Go Back")

        option, _ = pick(
            options,
            "What settings would you like to adjust?",
        )

        if option == "Go Back":
            return

        if "Column Height" in option:
            value = get_int_input(
                "What would you like to change the army column height to?",
                f"Current: {settings.army_columns}",
                5,
                25,
            )
            if value:
                settings.set_army_columns(value)

        if "Disable Mini-Games" in option:
            settings.toggle_mini_games()
            pick(["Got it"], f"Mini-Games are now {settings.mini_games_status}")

        if "Combat Mode" in option:
            settings.toggle_hard_combat()
            pick(["Done."], f"Combat Mode is now set to difficulty: {settings.hard_combat_status}")

        if "Compact Mode" in option:
            settings.toggle_compact_mode()
            pick(["Done."], f"Compact Mode is now {settings.compact_status}")

        if "Sort Order" in option:
            settings.toggle_sort_order()
            pick(["Done."], f"Sort Order is now {settings.sort_order}")

        FileManager.save(settings)
