from myning.chapters import Option, PickArgs, main_menu
from myning.objects.player import Player
from myning.objects.settings import Settings
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import confirm

player = Player()
settings = Settings()


def enter():
    options = [
        Option(["Minigames", f"({settings.mini_games_status})"], toggle_minigames),
        Option(["Compact Mode", f"({settings.compact_status})"], toggle_compact_mode),
        Option(
            ["Purchase Confirmation", f"({settings.purchase_confirmation_status})"],
            toggle_purchase_confirmation,
        ),
    ]

    if player.has_upgrade("sort_by_value"):
        options.append(Option(["Sort Order", f"({settings.sort_order})"], toggle_sort_order))

    options.append(Option("Go Back", main_menu.enter))
    return PickArgs(
        message="What settings would you like to adjust?",
        options=options,
    )


@confirm(
    lambda: f"Are you sure you want to {'enable' if settings.mini_games_disabled else 'disable'} "
    "Minigames?\n"
    + Formatter.locked(
        "Minigames allow you to speed up progress, earn more minerals, and have greater "
        "success in the mines. If you disable them, you will not be able to benefit from the "
        "bonuses they provide or skip time when there normally would be a mini-game. You can "
        "always enable and disable them in the settings."
    ),
    enter,
)
def toggle_minigames():
    settings.toggle_mini_games()
    FileManager.save(settings)
    return PickArgs(
        message=f"Minigames are now {settings.mini_games_status}",
        options=[Option("Done.", enter)],
    )


def toggle_compact_mode():
    settings.toggle_compact_mode()
    FileManager.save(settings)
    return PickArgs(
        message=f"Compact Mode is now {settings.compact_status}",
        options=[Option("Done.", enter)],
        subtitle="By the way, you can also toggle compact mode by focusing the Army widget "
        f"and pressing {Formatter.keybind('c')}.",
    )


def toggle_sort_order():
    settings.toggle_sort_order()
    FileManager.save(settings)
    return PickArgs(
        message=f"Sort Order is now {settings.sort_order}",
        options=[Option("Done", enter)],
    )


@confirm(
    lambda: f"Are you sure you want to {'disable' if settings.purchase_confirmation else 'enable'} "
    "purchase confirmation?\n"
    + Formatter.locked(
        "If disabled, you will not be prompted to confirm before purchasing items from a store and will stay on the items screen."
    ),
    enter,
)
def toggle_purchase_confirmation():
    settings.toggle_purchase_confirmation()
    FileManager.save(settings)
    return PickArgs(
        message=f"Purchase confirmation is now {settings.purchase_confirmation_status}",
        options=[Option("Done", enter)],
    )
