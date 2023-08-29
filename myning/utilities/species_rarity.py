import random

from myning.config import RESEARCH, SPECIES
from myning.objects.character import CharacterSpecies
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.species import Species
from myning.utilities.rand import boosted_random_choice

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


def get_current_tier():
    player = Player()
    return max(s.rarity_tier for s in player.discovered_species)


def _recruit_in_tier(tier: list[CharacterSpecies]):
    player = Player()

    is_undiscovered = lambda species_name: SPECIES[species_name] not in player.discovered_species

    facility = ResearchFacility()
    percent_boost = 0.0
    if facility.has_research("species_discovery"):
        percent_boost = RESEARCH["species_discovery"].player_value / 100

    selected_species_name = boosted_random_choice(tier, is_undiscovered, percent_boost)
    return SPECIES[selected_species_name] if selected_species_name else None


def get_recruit_species(highest_rarity: int):
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


def get_time_travel_species(lowest_tier: int = 0) -> Species:
    player = Player()
    non_me_species = [species for species in player.discovered_species if species != player.species]

    tiers = get_available_tiers(non_me_species)
    if lowest_tier > tiers[-1]:
        lowest_tier = tiers[-1]

    available_species = [s for s in non_me_species if s.rarity_tier >= lowest_tier]
    return random.choice(available_species)


def get_available_tiers(discovered_species: list[Species]) -> list[int]:
    if not discovered_species or len(discovered_species) <= 1:
        return [1]

    available_tiers = set()
    for species in discovered_species:
        available_tiers.add(species.rarity_tier)

    return list(sorted(available_tiers))
