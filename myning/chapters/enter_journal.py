from blessed import Terminal

from myning.config import RACES
from myning.objects.character import RaceEmoji
from myning.objects.player import Player
from myning.objects.race import Race
from myning.objects.scroll import Scroll
from myning.utils.io import pick
from myning.utils.ui import columnate

term = Terminal()


def play():
    player = Player()

    race_list = [RACES[race] for race in RACES]

    while True:
        options = columnate(
            [
                [
                    RaceEmoji(race.icon) if race in player.discovered_races else RaceEmoji("🔒"),
                    race.name
                    if race in player.discovered_races
                    else term.dimgray("*" * len(race.name)),
                ]
                for race in race_list
            ]
        )

        option, index = pick([*options, "Go Back"], "Select a Species to learn about them.")
        if option == "Go Back":
            return
        elif race_list[index] not in player.discovered_races:
            show_undiscovered_prompt()
        else:
            show_race(race_list[index])


def show_undiscovered_prompt():
    option, _ = pick(["Go Back"], "You have not discovered this species yet.")

    if option == "Go Back":
        return


def show_race(race: Race):
    with term.fullscreen(), term.cbreak():
        scroll = Scroll()

        build_race_scroll_view(scroll, race)
        scroll.animate(duration=0.3)

        index = 0
        while True:
            option, index = pick(
                ["Scroll Up", "Scroll Down", "Go Back"],
                dashboard=lambda: str(scroll),
                index=index,
            )
            if option == "Scroll Up":
                scroll.scroll_up()
            elif option == "Scroll Down":
                scroll.scroll_down()
            elif option == "Go Back":
                break


def build_race_scroll_view(scroll: Scroll, race: Race):
    scroll.build_title(f"{race.icon} - {race.name}")
    scroll.build_heading("Alignment")
    scroll.build_indented_paragraph(race.alignment)
    scroll.build_heading("Rarity")
    scroll.build_indented_paragraph(race.rarity_str)
    scroll.build_heading("Stats")
    scroll.build_indented_paragraph(race.skills_str)
    scroll.build_heading("Description")
    scroll.build_indented_paragraph(race.description)
