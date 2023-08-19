from unittest.mock import patch

import pytest

from myning.config import SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player


@pytest.fixture(autouse=True)
def player_instance():
    player = Player()
    player.initialize("MockPlayer")

    yield player


def test_roll_for_species(player_instance):
    player_instance.discovered_species = [SPECIES[CharacterSpecies.GOLIATH.value]]
    new_species = player_instance.roll_for_species().name
    assert (new_species is "Goliath", f"Species is not Goliath : {new_species}")
