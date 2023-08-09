import random
from typing import Optional

from myning.config import RESEARCH, SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.species import Species
from myning.utils.utils import boosted_random_choice, get_random_array_item

SPECIES_TIERS = [
    [CharacterSpecies.HUMAN],
    [
        CharacterSpecies.DWARF,
        CharacterSpecies.ELF,
        CharacterSpecies.GOBLIN,
        CharacterSpecies.HALFLING,
        CharacterSpecies.ORC,
        CharacterSpecies.GNOME,
    ],
    [
        CharacterSpecies.HALF_ELF,
        CharacterSpecies.HALF_ORC,
        CharacterSpecies.BUGBEAR,
        CharacterSpecies.HOBGOBLIN,
        CharacterSpecies.LIZARDFOLK,
    ],
    [
        CharacterSpecies.GOLIATH,
        CharacterSpecies.DRAGONBORN,
        CharacterSpecies.TIEFLING,
        CharacterSpecies.TRITON,
    ],
    [CharacterSpecies.FIRBOLG, CharacterSpecies.KENKU, CharacterSpecies.KOBOLD],
    [CharacterSpecies.TABAXI, CharacterSpecies.YUAN_TI_PUREBLOOD],
    [CharacterSpecies.AASIMAR, CharacterSpecies.UNICORN],
]


SPECIES_WEIGHTS = [150, 75, 40, 20, 10, 7, 4]


def _recruit_in_tier(tier: list[CharacterSpecies]) -> Optional[Species]:
    player = Player()

    def is_undiscovered(species_name: CharacterSpecies):
        return SPECIES[species_name] not in player.discovered_species

    facility = ResearchFacility()
    percent_boost = 0.0
    if facility.has_research("species_discovery"):
        percent_boost = RESEARCH["species_discovery"].player_value / 100

    selected_species_name = boosted_random_choice(tier, is_undiscovered, percent_boost)

    return SPECIES[selected_species_name]


def get_recruit_species(highest_rarity: int) -> Optional[Species]:
    player = Player()
    facility = ResearchFacility()
    tiers = list(range(1, highest_rarity + 1))
    species_weights = SPECIES_WEIGHTS[:highest_rarity]
    if facility.has_research("species_rarity"):
        species_weights = [
            weight + RESEARCH["species_rarity"].player_value + (i * 3)
            for i, weight in enumerate(species_weights)
        ]

    rarity = random.choices(tiers, weights=species_weights)[0]

    tier = SPECIES_TIERS[rarity - 1]
    return _recruit_in_tier(tier)
