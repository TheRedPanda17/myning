import random

from myning.config import RESEARCH, SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.utils.utils import get_random_array_item

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


def get_recruit_species(highest_rarity: int):
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
    if facility.has_research("species_discovery"):
        individual_weights = []
        for species in tier:
            if SPECIES[species] in player.discovered_species:
                chance = 100 - RESEARCH["species_discovery"].player_value
                individual_weights.append(chance)
            else:
                individual_weights.append(100)
        species = random.choices(tier, weights=individual_weights)[0]
    else:
        species = get_random_array_item(tier)
    return SPECIES[species]
