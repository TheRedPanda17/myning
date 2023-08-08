import random

from myning.config import RACES, RESEARCH
from myning.objects.character import CharacterRaces
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.utils.utils import get_random_array_item

RACE_TIERS = [
    [CharacterRaces.HUMAN],
    [
        CharacterRaces.DWARF,
        CharacterRaces.ELF,
        CharacterRaces.GOBLIN,
        CharacterRaces.HALFLING,
        CharacterRaces.ORC,
        CharacterRaces.GNOME,
    ],
    [
        CharacterRaces.HALF_ELF,
        CharacterRaces.HALF_ORC,
        CharacterRaces.BUGBEAR,
        CharacterRaces.HOBGOBLIN,
        CharacterRaces.LIZARDFOLK,
    ],
    [
        CharacterRaces.GOLIATH,
        CharacterRaces.DRAGONBORN,
        CharacterRaces.TIEFLING,
        CharacterRaces.TRITON,
    ],
    [CharacterRaces.FIRBOLG, CharacterRaces.KENKU, CharacterRaces.KOBOLD],
    [CharacterRaces.TABAXI, CharacterRaces.YUAN_TI_PUREBLOOD],
    [CharacterRaces.AASIMAR, CharacterRaces.UNICORN],
]


RACE_WEIGHTS = [150, 75, 40, 20, 10, 7, 4]


def _recruit_in_tier(tier: list[CharacterRaces]) -> CharacterRaces:
    if len(tier) == 0:
        raise ValueError("Empty tier")
    player = Player()
    facility = ResearchFacility()
    undiscovered = [
        RACES[race_index] for race_index in tier if RACES[race_index] not in player.discovered_races
    ]
    discovered_weight = 1 / len(tier)
    undiscovered_weight = 0
    if len(undiscovered) > 0:
        undiscovered_probability = len(undiscovered) / len(tier)
        percent_increase = 0
        if facility.has_research("species_discovery"):
            percent_increase = RESEARCH["species_discovery"].player_value / 100
        undiscovered_probability += undiscovered_probability * percent_increase
        discovered_probability = 1 - undiscovered_probability
        undiscovered_weight = undiscovered_probability / len(undiscovered)
        discovered_count = len(tier) - len(undiscovered)
        if discovered_count > 0:
            discovered_weight = discovered_probability / discovered_count
    weights = []
    for race in tier:
        if RACES[race] in player.discovered_races:
            weights.append(discovered_weight)
        else:
            weights.append(undiscovered_weight)
    race_index = random.choices(tier, weights=weights)[0]
    return RACES[race_index]


def get_recruit_species(highest_rarity: int):
    facility = ResearchFacility()
    tiers = list(range(1, highest_rarity + 1))
    race_weights = RACE_WEIGHTS[:highest_rarity]
    if facility.has_research("species_rarity"):
        race_weights = [
            weight + RESEARCH["species_rarity"].player_value + (i * 3)
            for i, weight in enumerate(race_weights)
        ]

    rarity = random.choices(tiers, weights=race_weights)[0]

    tier = RACE_TIERS[rarity - 1]
    return _recruit_in_tier(tier)
