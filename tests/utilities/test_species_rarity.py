from myning.config import SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.utilities.species_rarity import get_current_tier, get_recruit_species

player = Player()


def test_get_current_tier():
    assert player.discovered_species == [SPECIES[CharacterSpecies.HUMAN.value]]
    assert get_current_tier() == 1

    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
    ]
    assert get_current_tier() == 4

    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
        SPECIES[CharacterSpecies.UNICORN.value],
    ]
    assert get_current_tier() == 7


def test_get_recruit_species():
    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
    ]
    rarity = get_current_tier()
    species = get_recruit_species(rarity)
    assert species
    assert species.rarity_tier <= rarity
