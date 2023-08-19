import yaml

from myning.objects.mine import Mine
from myning.objects.species import Species
from myning.objects.upgrade import Upgrade, UpgradeType

XP_COST = 2


with open("myning/config.yaml", "r") as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)

with open("myning/strings.yaml", "r") as f:
    STRINGS = yaml.load(f, Loader=yaml.FullLoader)

with open("myning/mines.yaml", "r") as f:
    MINES = yaml.load(f, Loader=yaml.FullLoader)
    for name, mine in MINES.items():
        mine["name"] = name
        MINES[name] = Mine.from_dict(mine)

with open("myning/upgrades.yaml", "r") as f:
    UPGRADES = yaml.load(f, Loader=yaml.FullLoader)
    for id, upgrade in UPGRADES.items():
        upgrade["id"] = id
        UPGRADES[id] = Upgrade.from_dict(upgrade)

with open("myning/names.yaml", "r") as f:
    NAMES = yaml.load(f, Loader=yaml.FullLoader)

with open("myning/species.yaml", "r") as f:
    SPECIES = yaml.load(f, Loader=yaml.FullLoader)
    for id, race in SPECIES.items():
        SPECIES[id] = Species.from_dict(race)

with open("myning/research.yaml", "r") as f:
    RESEARCH = yaml.load(f, Loader=yaml.FullLoader)
    for id, research in RESEARCH.items():
        research["id"] = id
        RESEARCH[id] = Upgrade.from_dict(research, UpgradeType.RESEARCH)
