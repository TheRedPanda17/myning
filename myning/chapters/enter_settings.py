from myning.objects.settings import Settings
from myning.utils.file_manager import FileManager
from myning.utils.io import get_int_input, pick


def play():
    settings = Settings()

    while True:
        option, _ = pick(
            [
                "Adjust Army Column Height",
                f"Enable/Disable Mini-Games ({settings.mini_games_status})",
                f"Combat Mode ({settings.hard_combat_status})",
                f"Compact Mode ({settings.compact_status})",
                "Exit",
            ],
            "What settings would you like to adjust?",
        )

        if option == "Exit":
            return

        if "Column Height" in option:
            value = get_int_input("What would you like to change the army column height to?", 5, 25)
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

        FileManager.save(settings)
