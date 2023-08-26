from myning.config import SPECIES
from myning.objects.character import Character, CharacterSpecies
from myning.utilities.generators import generate_character


def test_alien_species_attributes():
    """Test that alien species attributes are correct"""
    char = generate_character(level_range=[1, 2])
    assert char.name.isalpha
    assert " " in char.name
    for attr in ("damage", "armor", "critical_chance", "dodge_chance"):
        assert isinstance(char.stats[attr], int)


def test_companion_classes():
    """Test that companion classes are correctly typed"""
    char = generate_character(level_range=[1, 2])
    assert isinstance(char.companion_species, list)
    for attr in char.companion_species:
        assert isinstance(attr, CharacterSpecies)


def test_species_attributes():
    """Test that species attributes are correct"""
    for species in Character.companion_species:
        species = SPECIES[species.value]
        char = generate_character(level_range=[1, 2], species=species)
        assert char.health_mod == species.health_mod
        assert char.name.isalpha
        assert " " in char.name
        for attr in ("damage", "armor", "critical_chance", "dodge_chance"):
            assert isinstance(char.stats[attr], int)
