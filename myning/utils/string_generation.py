from myning.config import NAMES, STRINGS
from myning.objects.character import CharacterRaces
from myning.utils.utils import get_random_array_item, get_random_array_item_and_index

creature_types = [
    "Spider",
    "Cat",
    "Fox",
    "Crab",
    "Mosquito",
    "Caterpillar",
    "Yoda",
    "Raven",
    "Bear",
    "service dog",
    "mole",
    "badger",
    "dungbeetle",
]


killers = [
    "swarm of bees",
    "ex-lover",
    "fellow companion",
    "miner",
    "childhood bully",
    "close friend",
    "father-in-law",
    "mother-in-law",
    "brother-in-law",
    "sister-in-law",
    "grandfather",
    "grandmother",
    "grandson",
    "granddaughter",
    "mentor",
    "mentee",
    "friend",
    "enemy",
    "foe",
    "coach",
]

people_adjectives = [
    "jealous",
    "helpful",
    "considerate",
    "well-behaved",
    "responsible",
    "mature",
    "sensible",
    "self-motivated",
    "warm",
    "calm",
    "serene, composed",
    "gentle",
    "mild pleasant",
    "charming",
    "delightful",
    "jovial",
    "cheerful",
    "jolly",
    "hearty",
    "serious",
    "matured",
    "natural",
    "impressionable",
    "impassionate",
    "spirited",
    "excitable",
    "imperturbable",
    "staid",
    "grave",
    "sedate",
    "demure",
    "resigned",
    "playful",
    "unaffected; affected",
    "quick",
    "ferocious",
    "acute",
    "cutting",
    "incisive",
    "fiery",
    "hysterical",
    "impetuous",
    "heady",
    "hot",
    "sentimental",
    "mettlesome",
    "over-sensitive",
    "mercurial",
    "restless",
    "boisterous",
    "impulsive",
    "volcanic",
    "stoical",
    "morose",
    "glommy",
    "moody",
    "melancholic",
    "sharp",
    "caustic",
    "cheerless",
    "pensive",
    "flashy",
    "nervous",
    "hot-headed",
    "emotionally stable",
    "fussy",
    "impulsive",
    "cynical",
    "sophisticated",
    "mature",
]

death_actions = [
    "crushed",
    "boiled",
    "burned",
    "skinned",
    "devoured",
    "decapitated",
    "murdered",
    "sliced and diced",
    "minced",
    "shot",
    "stabbed",
    "flayed",
    "frightened",
    "drowned",
    "dismembered",
    "convinced to elope",
    "convinced to flee",
]


def generate_potion_base():
    size, weight = get_random_array_item_and_index(STRINGS["sizes"])
    potion = get_random_array_item(STRINGS["minerals"])

    return {
        "name": f"{size} {potion}",
        "weight": weight,
    }


def generate_name(type):
    return f"{get_random_array_item(NAMES[type]['first'])} {get_random_array_item(NAMES[type]['last'])}"


def generate_description(type):
    size = get_random_array_item(STRINGS["sizes"]).lower()
    adjective = get_random_array_item(STRINGS["modifiers"]).lower()
    if type == CharacterRaces.ALIEN.value:
        type = f"{get_random_array_item(creature_types).lower()}-like creature"
    return f"a {size}, {adjective}, {type}"


def generate_death_action():
    death = get_random_array_item(death_actions)
    attacker = get_random_array_item(killers)
    adj = get_random_array_item(people_adjectives)
    return f"{death} by a {adj} {attacker}"
