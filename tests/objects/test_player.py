from myning.config import SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player

player = Player()


def test_roll_for_species():
    player.species = SPECIES[CharacterSpecies.HUMAN]
    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN],
        SPECIES[CharacterSpecies.GOLIATH],
    ]
    new_species = player.roll_for_species()
    assert new_species.name == "Goliath"
    # Species always changes when rolling
    player.species = new_species
    assert player.roll_for_species().name == "Human"
