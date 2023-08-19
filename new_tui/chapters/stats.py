from myning.objects.stats import Stats
from new_tui.chapters import PickArgs, main_menu

stats = Stats()


def enter():
    return PickArgs(
        message="Stats\n",
        options=[
            ("Sync Stats", unimplemented),
            ("View Highscores", unimplemented),
            ("Go Back", main_menu.enter),
        ],
        subtitle=stats.tui_display,
    )


def unimplemented():
    return PickArgs(
        message="This has not been implemented yet.",
        options=[("Bummer!", enter)],
    )
