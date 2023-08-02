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


def get_recruit_species(highest_rarity: int):
    player = Player()
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
    if facility.has_research("species_discovery"):
        individual_weights = []
        for race in tier:
            if RACES[race] in player.discovered_races:
                chance = 100 - RESEARCH["species_discovery"].player_value
                individual_weights.append(chance)
            else:
                individual_weights.append(100)
        race = random.choices(tier, weights=individual_weights)[0]
    else:
        race = get_random_array_item(tier)
    return RACES[race]
