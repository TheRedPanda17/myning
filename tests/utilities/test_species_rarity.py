import pytest

from myning.config import SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.utilities.species_rarity import (
    get_available_tiers,
    get_current_tier,
    get_recruit_species,
    get_time_travel_species,
)

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


def test_get_available_tiers():
    available_tiers = get_available_tiers(None)
    assert available_tiers == [1]

    available_tiers = get_available_tiers([])
    assert available_tiers == [1]

    species = [SPECIES[CharacterSpecies.HUMAN.value]]

    available_tiers = get_available_tiers(species)
    assert available_tiers == [1]

    species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.DWARF],
        SPECIES[CharacterSpecies.HALF_ORC],
        SPECIES[CharacterSpecies.GOLIATH.value],
    ]

    available_tiers = get_available_tiers(species)
    assert available_tiers == [1, 2, 3, 4]

    species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.DWARF.value],
        SPECIES[CharacterSpecies.ELF.value],
        SPECIES[CharacterSpecies.GOBLIN.value],
        SPECIES[CharacterSpecies.HALFLING.value],
        SPECIES[CharacterSpecies.ORC.value],
        SPECIES[CharacterSpecies.GNOME.value],
        SPECIES[CharacterSpecies.HALF_ELF.value],
        SPECIES[CharacterSpecies.HALF_ORC.value],
        SPECIES[CharacterSpecies.BUGBEAR.value],
        SPECIES[CharacterSpecies.HOBGOBLIN.value],
        SPECIES[CharacterSpecies.LIZARDFOLK.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
        SPECIES[CharacterSpecies.DRAGONBORN.value],
        SPECIES[CharacterSpecies.TIEFLING.value],
        SPECIES[CharacterSpecies.TRITON.value],
        SPECIES[CharacterSpecies.FIRBOLG.value],
        SPECIES[CharacterSpecies.KENKU.value],
        SPECIES[CharacterSpecies.KOBOLD.value],
        SPECIES[CharacterSpecies.TABAXI.value],
        SPECIES[CharacterSpecies.YUAN_TI_PUREBLOOD.value],
        SPECIES[CharacterSpecies.AASIMAR.value],
        SPECIES[CharacterSpecies.UNICORN.value],
    ]

    available_tiers = get_available_tiers(species)
    assert available_tiers == [1, 2, 3, 4, 5, 6, 7]


def test_get_random_species_edge_cases():
    # Only one option
    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
    ]
    player.species = SPECIES[CharacterSpecies.HUMAN.value]

    species = get_time_travel_species()
    assert species.name == SPECIES[CharacterSpecies.GOLIATH.value].name

    # Ignore low tiers
    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.GOBLIN.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
    ]

    species = get_time_travel_species(3)
    assert species.name == SPECIES[CharacterSpecies.GOLIATH.value].name

    # Already a higher tier
    player.species = SPECIES[CharacterSpecies.GOLIATH.value]

    species = get_time_travel_species(3)
    assert species.name == SPECIES[CharacterSpecies.GOBLIN.value].name

    # Same tier as current
    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.GOBLIN.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
        SPECIES[CharacterSpecies.LIZARDFOLK.value],
    ]

    species = get_time_travel_species(3)
    assert species.name == SPECIES[CharacterSpecies.LIZARDFOLK.value].name


@pytest.mark.parametrize(
    "tier",
    [1, 2, 3, 4, 5, 6, 7],
)
def test_get_time_travel_species(tier):
    # All of them
    player.species = SPECIES[CharacterSpecies.HUMAN.value]
    player.discovered_species = [
        SPECIES[CharacterSpecies.HUMAN.value],
        SPECIES[CharacterSpecies.DWARF.value],
        SPECIES[CharacterSpecies.ELF.value],
        SPECIES[CharacterSpecies.GOBLIN.value],
        SPECIES[CharacterSpecies.HALFLING.value],
        SPECIES[CharacterSpecies.ORC.value],
        SPECIES[CharacterSpecies.GNOME.value],
        SPECIES[CharacterSpecies.HALF_ELF.value],
        SPECIES[CharacterSpecies.HALF_ORC.value],
        SPECIES[CharacterSpecies.BUGBEAR.value],
        SPECIES[CharacterSpecies.HOBGOBLIN.value],
        SPECIES[CharacterSpecies.LIZARDFOLK.value],
        SPECIES[CharacterSpecies.GOLIATH.value],
        SPECIES[CharacterSpecies.DRAGONBORN.value],
        SPECIES[CharacterSpecies.TIEFLING.value],
        SPECIES[CharacterSpecies.TRITON.value],
        SPECIES[CharacterSpecies.FIRBOLG.value],
        SPECIES[CharacterSpecies.KENKU.value],
        SPECIES[CharacterSpecies.KOBOLD.value],
        SPECIES[CharacterSpecies.TABAXI.value],
        SPECIES[CharacterSpecies.YUAN_TI_PUREBLOOD.value],
        SPECIES[CharacterSpecies.AASIMAR.value],
        SPECIES[CharacterSpecies.UNICORN.value],
    ]

    species = get_time_travel_species(tier)
    assert species.rarity_tier >= tier
