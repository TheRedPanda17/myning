import math
import random

from blessed import Terminal

from myning.chapters import enter_combat, enter_mining
from myning.config import MINES, RESEARCH, SPECIES
from myning.objects.macguffin import Macguffin
from myning.objects.mine import Mine, MineType
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.species import Species
from myning.objects.stats import IntegerStatKeys, Stats
from myning.objects.trip import LOST_RATIO, Trip
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_character, generate_equipment
from myning.utils.io import pick
from myning.utils.output import get_species_discovery_message, print_entity_speech
from myning.utils.species_rarity import SPECIES_TIERS, get_recruit_species
from myning.utils.string_generation import generate_death_action
from myning.utils.tab_title import TabTitle
from myning.utils.ui import columnate
from myning.utils.ui_consts import Icons
from myning.utils.user_input import get_idle_time, slow_print, timed_input
from myning.utils.utils import get_random_array_item

term = Terminal()


def play():
    player = Player()
    trip = Trip()

    while True:
        mine = get_mine()
        if not mine:
            return
        trip.mine = mine
        subtitle = ""
        if mine.win_criteria:
            subtitle += "\n" + term.snow4(mine.progress)
        subtitle += "\nRisk of Demise:   " + mine.death_chance_str
        if mine.companion_rarity:
            subtitle += "\nDiscoverable:     "
            subtitle += "".join(unlock_species_emojies(available_species(mine)))

        message = f"How long would you like to mine in {mine.icon} {term.blue(mine.name)}?"
        if t := get_idle_time(player.level, message, subtitle):
            break

    trip.start_trip(t * 60)
    FileManager.save(trip)
    begin()


def begin():
    player = Player()
    trip = Trip()
    minutes = trip.seconds_left / 60
    while trip.seconds_left > 0 and player.alive:
        TabTitle.change_tab_status(f"{int(trip.seconds_left/60) + 1}m left in {trip.mine.name}")
        print("\nMining...")
        start_mining()

    if minutes == 0:
        return

    TabTitle.change_tab_status("Done!")
    print("\nDone mining")
    print("\a")
    add_trip_to_player()
    print(trip)
    input()
    check_progress()
    trip.clear()
    FileManager.save(player)


def start_mining():
    trip = Trip()
    actions = [o["action"] for o in trip.mine.odds]
    chances = [o["chance"] for o in trip.mine.odds]
    selected_action = random.choices(actions, weights=chances)[0]
    {
        "combat": enter_combat.play,
        "equipment": acquire_equipment,
        "mineral": enter_mining.play,
        "recruit": recruit_ally,
        "lose_ally": lose_ally,
    }[selected_action]()


def acquire_equipment():
    trip = Trip()
    equipment = generate_equipment(trip.mine.max_item_level)
    trip.add_item(equipment)
    slow_print(equipment.get_new_text())
    FileManager.multi_save(equipment, trip)


def lose_ally():
    player = Player()
    if len(player.allies) < 1:
        return
    trip = Trip()
    ally = get_random_array_item(player.allies)
    reason = generate_death_action()

    if ally.is_ghost:
        print(
            f"\n{term.blue}{ally.name} was almost {reason}.{term.normal} Luckily, they're a ghost"
        )
        _, _ = timed_input(timeout=5)
    else:
        player.kill_ally(ally)
        trip.remove_ally(ally)

        print(f"\n{term.red}Oh no! {ally.name} has died!{term.normal}\nCause of death: {reason}")
        _, _ = timed_input(timeout=5)
        FileManager.multi_save(trip, player)


def recruit_ally():
    trip = Trip()

    # Allies should be less powerful than enemies
    levels = trip.mine.character_levels
    levels = [max(1, math.ceil(level * 0.75)) for level in levels]

    species = get_recruit_species(trip.mine.companion_rarity)
    ally = generate_character(levels, species=species)

    print_entity_speech(ally, f"{ally.introduction} I'd like to join your army.", wait=False)

    trip.add_ally(ally)
    FileManager.multi_save(ally, trip)


def get_mine() -> Mine | None:
    player = Player()
    options = columnate([mine.str_arr for mine in player.mines_available])
    has_death_mine = any(f"{Icons.DEATH}" in mine for mine in options)
    go_back_string = "   Go back"
    unlock_string = "   Unlock New Mine"

    option, index = pick(
        [*options, unlock_string, go_back_string],
        "Which mine would you like to enter?",
        sub_title=f"{Icons.DEATH}: Risk of Companion Demise" if has_death_mine else None,
    )

    if option == unlock_string:
        unlock_mines()
        return get_mine()
    elif option == go_back_string:
        return None
    return player.mines_available[index]


def unlock_mines():
    player = Player()
    mines: list[Mine] = [mine for _, mine in MINES.items() if mine not in player.mines_available]

    options = columnate(
        [mine.get_unlock_str_arr(player.level >= mine.min_player_level) for mine in mines]
    )
    go_back_string = "   Go back"

    option, index = pick(
        [*options, go_back_string],
        "Which mine would you like to unlock?",
        sub_title=f"""{Icons.MINERAL}: Normal Mine
{Icons.RESOURCE}: Resource Mine
{Icons.DAMAGE}: Combat Zone
{Icons.DEATH}: Risk of Companian Demise""",
    )

    if option == go_back_string:
        return

    mine = mines[index]
    if mine.min_player_level > player.level:
        pick(["Bummer!"], "You aren't a high enough level for this mine")
        return

    if player.pay(
        mine.cost,
        failure_msg="You don't have enough gold to unlock this mine",
        failure_option="Bummer!",
    ):
        player.mines_available.append(mine)
        FileManager.save(player)
        pick(["Sweet!"], message=f"You have unlocked {mine.name}")


def add_trip_to_player():
    player = Player()
    trip = Trip()
    macguffin = Macguffin()
    stats = Stats()

    stats.increment_int_stat(IntegerStatKeys.ENEMIES_DEFEATED, trip.enemies_defeated)
    stats.increment_int_stat(IntegerStatKeys.BATTLES_WON, trip.battles_won)
    stats.increment_int_stat(IntegerStatKeys.MINERALS_MINED, len(trip.minerals_mined))
    if player.army.defeated:
        print(
            f"You were defeated. You lost 1/{LOST_RATIO} of the items you found and xp you gained."
        )
        trip.subtract_losses()
        stats.increment_int_stat(IntegerStatKeys.ARMY_DEFEATS)
    else:
        stats.increment_int_stat(IntegerStatKeys.TRIPS_FINISHED)

    for ally in trip.allies_gained:
        player.add_ally(ally)
        if ally.species not in player.discovered_species:
            player.discovered_species.append(ally.species)
            message, subtitle = get_species_discovery_message(
                ally.name, ally.species.name, ally.species.icon
            )
            pick(["Awesome!"], message=message, sub_title=subtitle)

    if len(player.army) > 1:
        xp = int(trip.experience_gained * 1 / 2 * len(player.army) * macguffin.xp_boost)
        player.add_available_xp(xp)
    else:
        player.add_experience(int(trip.experience_gained * macguffin.xp_boost))

    if trip.mine.type == MineType.COMBAT:
        print("The goods collected on the trip were donated to the training facility.")
        trip.minerals_mined = []
        trip.items_found = []

    FileManager.save(stats)
    player.inventory.add_items(trip.items_found + trip.minerals_mined)


def check_progress():
    player = Player()
    trip = Trip()
    research_facility = ResearchFacility()

    progress = trip.mine.player_progress
    if research_facility.has_research("speed_up_time"):
        increase = RESEARCH["speed_up_time"].player_value + 100
        trip.total_seconds = int(increase / 100 * trip.total_seconds)

    progress.minutes += trip.total_seconds / 60.0
    progress.kills += trip.enemies_defeated
    progress.minerals += len(trip.minerals_mined)

    mine = trip.mine
    if mine.win_criteria:
        if mine.complete and mine not in player.mines_completed:
            player.mines_completed.append(mine)

            pick(["Heck yeah!"], f"You have completed {mine.icon} {term.blue(mine.name)}! 🎉")
        elif not mine.complete:
            pick(
                ["Thanks for the update"],
                f"You have completed a mining trip in {mine.icon} {term.blue(mine.name)}",
                sub_title="\n" + mine.progress,
            )


def available_species(mine: Mine) -> list[Species]:
    if not mine.companion_rarity:
        return []

    species = []
    for i in range(0, mine.companion_rarity):
        tier = SPECIES_TIERS[i]
        for s in tier:
            species.append(SPECIES[s])

    return species


def unlock_species_emojies(species: list[Species]) -> list[str]:
    player = Player()
    emojis = []
    for spec in species:
        if spec in player.discovered_species:
            emojis.append(spec.icon)
        else:
            emojis.append("❓")

    return emojis
