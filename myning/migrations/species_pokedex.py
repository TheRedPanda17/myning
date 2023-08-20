import os

from myning.config import SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.utilities import string_generation
from myning.utilities.file_manager import FileManager


def run():
    Player.initialize()
    player = Player()

    for ally in player.allies:
        ally.species = SPECIES[CharacterSpecies.HUMAN.value]
        ally.name = string_generation.generate_name(ally.species.name)
        ally.description = string_generation.generate_description(ally.species.name)
        FileManager.save(ally)

    for ally in player.fallen_allies:
        ally.species = SPECIES[CharacterSpecies.HUMAN.value]
        ally.name = string_generation.generate_name(ally.species.name)
        ally.description = string_generation.generate_description(ally.species.name)
        FileManager.save(ally)

    for ally in player.fired_allies:
        ally.species = SPECIES[CharacterSpecies.HUMAN.value]
        ally.name = string_generation.generate_name(ally.species.name)
        ally.description = string_generation.generate_description(ally.species.name)
        FileManager.save(ally)

    FileManager.save(player)

    os.system("pip install -r requirements.txt")

    print("Migration complete. Enjoy the update!")
