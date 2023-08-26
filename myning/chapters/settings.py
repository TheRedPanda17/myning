from myning.chapters import Option, PickArgs, main_menu
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.utilities.formatter import Formatter

player = Player()
settings = Settings()


def enter():
    options = [
        Option(["Compact Mode", f"({settings.compact_status})"], toggle_compact_mode),
    ]

    if player.has_upgrade("sort_by_value"):
        options.append(
            Option(
                ["Sort Order", f"({settings.sort_order})"], toggle_sort_order, enable_hotkeys=True
            )
        )

    options.append(Option("Go Back", main_menu.enter))
    return PickArgs(
        message="What settings would you like to adjust?",
        options=options,
    )


def toggle_compact_mode():
    settings.toggle_compact_mode()
    return PickArgs(
        message=f"Compact Mode is now {settings.compact_status}",
        options=[Option("Done.", enter)],
        subtitle="By the way, you can also toggle compact mode by focusing the Army widget "
        f"and pressing {Formatter.keybind('c')}.",
    )


def toggle_sort_order():
    settings.toggle_sort_order()
    return PickArgs(
        message=f"Sort Order is now {settings.sort_order}",
        options=[Option("Done", enter)],
    )

    # option, _ = pick(
    #     [
    #         "Adjust Army Column Height",
    #         f"Enable/Disable Mini-Games ({settings.mini_games_status})",
    #         f"Combat Mode ({settings.hard_combat_status})",
    #         f"Compact Mode ({settings.compact_status})",
    #         "Exit",
    #     ],
    #     "What settings would you like to adjust?",
    # )

    # if option == "Exit":
    #     return

    # if "Column Height" in option:
    #     value = get_int_input(
    #         "What would you like to change the army column height to?",
    #         f"Current: {settings.army_columns}",
    #         5,
    #         25,
    #     )
    #     if value:
    #         settings.set_army_columns(value)

    # if "Disable Mini-Games" in option:
    #     settings.toggle_mini_games()
    #     pick(["Got it"], f"Mini-Games are now {settings.mini_games_status}")

    # if "Combat Mode" in option:
    #     settings.toggle_hard_combat()
    #     pick(["Done."], f"Combat Mode is now set to difficulty: {settings.hard_combat_status}")

    # if "Compact Mode" in option:
    #     settings.toggle_compact_mode()
    #     pick(["Done."], f"Compact Mode is now {settings.compact_status}")

    # FileManager.save(settings)
