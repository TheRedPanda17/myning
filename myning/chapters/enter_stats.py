from myning.objects.stats import Stats
from myning.utils.io import pick


def play():
    stats = Stats()

    while True:
        option, _ = pick(
            ["Sync Stats", "View Highscores", "Exit"],
            stats.display,
        )

        if option == "Exit":
            return
        pick(["Bummer!"], "This has not been implmented yet.")
