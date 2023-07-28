import os

from myning.config import RACES
from myning.objects.character import CharacterRaces
from myning.objects.player import Player
from myning.utils import string_generation
from myning.utils.file_manager import FileManager


def run():
    Player.initialize()
    player = Player()

    for ally in player.allies:
        ally.race = RACES[CharacterRaces.HUMAN.value]
        ally.name = string_generation.generate_name(ally.race.name)
        ally.description = string_generation.generate_description(ally.race.name)
        FileManager.save(ally)

    for ally in player.fallen_allies:
        ally.race = RACES[CharacterRaces.HUMAN.value]
        ally.name = string_generation.generate_name(ally.race.name)
        ally.description = string_generation.generate_description(ally.race.name)
        FileManager.save(ally)

    for ally in player.fired_allies:
        ally.race = RACES[CharacterRaces.HUMAN.value]
        ally.name = string_generation.generate_name(ally.race.name)
        ally.description = string_generation.generate_description(ally.race.name)
        FileManager.save(ally)

    FileManager.save(player)

    os.system("pip install -r requirements.txt")

    print("Migration complete. Enjoy the update!")
