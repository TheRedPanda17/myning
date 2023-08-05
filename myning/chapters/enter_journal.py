from blessed import Terminal

from myning.config import SPECIES
from myning.objects.character import SpeciesEmoji
from myning.objects.player import Player
from myning.objects.scroll import Scroll
from myning.objects.species import Species
from myning.utils.io import pick
from myning.utils.ui import columnate

term = Terminal()


def play():
    player = Player()

    species_list = [SPECIES[species] for species in SPECIES]

    while True:
        options = columnate(
            [
                [
                    SpeciesEmoji(species.icon)
                    if species in player.discovered_species
                    else SpeciesEmoji("🔒"),
                    species.name
                    if species in player.discovered_species
                    else term.dimgray("*" * len(species.name)),
                ]
                for species in species_list
            ]
        )

        option, index = pick([*options, "Go Back"], "Select a Species to learn about them.")
        if option == "Go Back":
            return
        elif species_list[index] not in player.discovered_species:
            show_undiscovered_prompt()
        else:
            show_species(species_list[index])


def show_undiscovered_prompt():
    option, _ = pick(["Go Back"], "You have not discovered this species yet.")

    if option == "Go Back":
        return


def show_species(species: Species):
    with term.fullscreen(), term.cbreak():
        scroll = Scroll()

        build_species_scroll_view(scroll, species)
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


def build_species_scroll_view(scroll: Scroll, species: Species):
    scroll.build_title(f"{species.icon} - {species.name}")
    scroll.build_heading("Alignment")
    scroll.build_indented_paragraph(species.alignment)
    scroll.build_heading("Rarity")
    scroll.build_indented_paragraph(species.rarity_str)
    scroll.build_heading("Stats")
    scroll.build_indented_paragraph(species.skills_str)
    scroll.build_heading("Description")
    scroll.build_indented_paragraph(species.description)
