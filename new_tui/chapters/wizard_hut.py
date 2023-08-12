from new_tui.chapters import PickArgs, main_menu


def enter():
    return PickArgs(
        message="What wondrous, magical upgrades would you like to buy from the wizard?",
        options=[("Go Back", main_menu.enter)],
    )
