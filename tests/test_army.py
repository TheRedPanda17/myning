"""Tests for the Amry class."""

from myning.chapters.enter_healer import recover
from myning.objects.army import Army
from myning.objects.character import Character
from myning.utils.generators import generate_character


class TestArmy:
    """Test for Army specific things"""

    def test_healing_army_members_heal_to_their_max_health(self, mock_random_array_item):
        """Test that army members are healed to their max health"""
        militia = []
        for species in Character.companion_races:
            mock_random_array_item.return_value = species
            char = generate_character(level_range=[1, 2])
            militia.append(char)
        army = Army(militia)
        # damage the army
        for character in army:
            character.health = 0
        # heal the army
        army_max_health = sum(character.max_health for character in army)
        current_health = sum(character.health for character in army)
        while current_health < army_max_health:
            recover(army)
            current_health = sum(character.health for character in army)
        # check that all members are at max health
        for character in army:
            assert character.health == character.max_health
