import yaml

from myning.objects.mine import Mine
from myning.objects.race import Race
from myning.objects.upgrade import Upgrade, UpgradeType

EXP_COST = 2


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

with open("myning/races.yaml", "r") as f:
    RACES = yaml.load(f, Loader=yaml.FullLoader)
    for id, race in RACES.items():
        RACES[id] = Race.from_dict(race)
    # Required for data stability and fixing the typo
    RACES["Yuan-TiPureblood"] = RACES["Yuan-Ti Pureblood"]

with open("myning/research.yaml", "r") as f:
    RESEARCH = yaml.load(f, Loader=yaml.FullLoader)
    for id, research in RESEARCH.items():
        research["id"] = id
        RESEARCH[id] = Upgrade.from_dict(research, UpgradeType.RESEARCH)
