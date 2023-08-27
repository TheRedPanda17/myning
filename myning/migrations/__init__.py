from . import (
    blacksmith_upgrade,
    garden_transfer,
    generate_ids,
    graveyard_transfer,
    inventory_transfer,
    macfuffin_transfer,
    research_transfer,
    soul_credits,
    species_pokedex,
    stats_transfer,
)

MIGRATIONS = {
    1: species_pokedex,
    2: soul_credits,
    3: garden_transfer,
    4: research_transfer,
    5: macfuffin_transfer,
    6: stats_transfer,
    7: generate_ids,
    8: blacksmith_upgrade,
    9: graveyard_transfer,
    10: inventory_transfer,
}
