import unittest
from unittest.mock import MagicMock, Mock, patch

from myning.config import SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.utilities.species_rarity import get_current_tier, get_recruit_species


class TestSpeciesRarity(unittest.TestCase):
    """Test for Species Rarity"""

    @patch("myning.objects.player.FileManager.load", return_value=None)
    @patch("builtins.input", return_value="TestPlayerName")
    def test_initialize(self, mock_input, mock_load):
        # Mock FileManager.load to return None, simulating a new player
        mock_load.return_value = None

        # Create a mock Character instance to represent the player
        mock_player = MagicMock(spec=Player)
        mock_player._allies = []
        mock_player._fallen_allies = []
        mock_player._discovered_species = []

        Player._instance = mock_player
        Player.initialize()

        return mock_player

    def test_get_current_tier(self):
        mock_player = self.test_initialize()

        self.assertEqual(mock_player.discovered_species, [SPECIES[CharacterSpecies.HUMAN.value]])
        self.assertEqual(get_current_tier(), 1)

        mock_player.discovered_species = [
            SPECIES[CharacterSpecies.HUMAN.value],
            SPECIES[CharacterSpecies.GOLIATH.value],
        ]
        self.assertEqual(get_current_tier(), 4)

        mock_player.discovered_species = [
            SPECIES[CharacterSpecies.HUMAN.value],
            SPECIES[CharacterSpecies.GOLIATH.value],
            SPECIES[CharacterSpecies.UNICORN.value],
        ]
        self.assertEqual(get_current_tier(), 7)

    def test_get_recruit_species(self):
        mock_player = self.test_initialize()
        mock_player.discovered_species = [
            SPECIES[CharacterSpecies.HUMAN.value],
            SPECIES[CharacterSpecies.GOLIATH.value],
        ]

        rarity = get_current_tier()
        species = get_recruit_species(rarity)
        self.assertLessEqual(species.rarity_tier, rarity)
