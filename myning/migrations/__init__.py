from . import garden_transfer, macfuffin_transfer, research_transfer, soul_credits, species_pokedex

MIGRATIONS = {
    1: species_pokedex,
    2: soul_credits,
    3: garden_transfer,
    4: research_transfer,
    5: macfuffin_transfer,
}
