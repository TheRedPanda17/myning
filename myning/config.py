import yaml

from myning.objects.mine import Mine
from myning.objects.species import Species
from myning.objects.upgrade import Upgrade, UpgradeType

XP_COST = 2

MINES: dict[str, Mine] = {}
RESEARCH: dict[str, Upgrade] = {}
SPECIES: dict[str, Species] = {}
UPGRADES: dict[str, Upgrade] = {}


with open("myning/config.yaml", "r") as f:
    CONFIG: dict = yaml.load(f, Loader=yaml.FullLoader)

with open("myning/names.yaml", "r") as f:
    NAMES = yaml.load(f, Loader=yaml.FullLoader)

with open("myning/strings.yaml", "r") as f:
    STRINGS = yaml.load(f, Loader=yaml.FullLoader)

with open("myning/mines.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for name, mine in data.items():
        mine["name"] = name
        MINES[name] = Mine.from_dict(mine)

with open("myning/research.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for id, research in data.items():
        research["id"] = id
        RESEARCH[id] = Upgrade.from_dict(research, UpgradeType.RESEARCH)

with open("myning/species.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for id, species in data.items():
        SPECIES[id] = Species.from_dict(species)

with open("myning/upgrades.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for id, upgrade in data.items():
        upgrade["id"] = id
        UPGRADES[id] = Upgrade.from_dict(upgrade)
