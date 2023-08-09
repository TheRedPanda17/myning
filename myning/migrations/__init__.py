from . import garden_transfer, macfuffin_transfer, species_pokedex, research_transfer, soul_credits

MIGRATIONS = {
    1: species_pokedex,
    2: soul_credits,
    3: garden_transfer,
    4: research_transfer,
    5: macfuffin_transfer,
}
