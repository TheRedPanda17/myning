from functools import partial
from itertools import zip_longest
from typing import TYPE_CHECKING

from rich.table import Table

from myning.config import MINES, RESEARCH, SPECIES
from myning.objects.macguffin import Macguffin
from myning.objects.mine import Mine, MineType
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.species import Species
from myning.objects.stats import IntegerStatKeys, Stats
from myning.objects.trip import LOST_RATIO, Trip
from myning.utils.file_manager import FileManager
from myning.utils.species_rarity import SPECIES_TIERS
from myning.utils.ui_consts import Icons
from new_tui.chapters import DynamicArgs, Option, PickArgs, StoryArgs, healer, main_menu, tutorial
from new_tui.chapters.mine.screen import MineScreen
from new_tui.formatter import Colors, Formatter
from new_tui.utilities import story_builder

if TYPE_CHECKING:
    from new_tui.view.chapter import ChapterWidget

player = Player()
macguffin = Macguffin()
facility = ResearchFacility()
stats = Stats()
trip = Trip()


def exit_mine():
    return (main_menu.enter if tutorial.is_complete() else tutorial.learn_healer)()


def pick_mine():
    options = [(mine.tui_arr, partial(pick_time, mine)) for mine in player.mines_available] + [
        (["", "Unlock New Mine"], pick_unlock_mine),
        (["", "Go Back"], exit_mine),
    ]
    has_death_mine = any(mine.has_death_action for mine in player.mines_available)
    return PickArgs(
        message="Which mine would you like to enter?",
        options=options,  # type: ignore
        subtitle=f"{Icons.DEATH}: Risk of Companion Demise" if has_death_mine else None,
    )


def pick_time(mine: Mine):
    minutes = [
        int(player.level * 0.5) if player.level > 1 else 1,
        player.level * 1,
        player.level * 2,
        player.level * 4,
        player.level * 8,
    ]
    options: list[Option] = [(f"{m} minutes", partial(start_mine, mine, m)) for m in minutes]
    options.append(("Go Back", pick_mine))
    subtitle = mine.tui_progress
    subtitle.add_row("Risk of Demise:", f"{Icons.DEATH} {mine.death_chance_tui_str}")
    if mine.companion_rarity:
        subtitle.add_row("Discoverable:", "".join(unlock_species_emojies(available_species(mine))))
    for column in subtitle.columns:
        column.style = Colors.LOCKED
    return PickArgs(
        message=f"How long would you like to mine in {mine.icon} {mine.name}?\n",
        options=options,
        subtitle=subtitle,
    )


def start_mine(mine: Mine, minutes: int):
    if player.army.defeated:
        return PickArgs(
            message=f"{'Everyone in your army has' if player.allies else 'You have'} no health.\n"
            "You should probably go visit the healer before heading into the mines.",
            options=[
                ("Could you repeat that please?", partial(start_mine, mine, minutes)),
                ("Take me there!", healer.enter),
                ("Got it, thanks.", exit_mine),
            ],
        )

    trip.mine = mine
    trip.start_trip(minutes * 60)
    return DynamicArgs(callback=mine_callback)


def mine_callback(chapter: "ChapterWidget"):
    def screen_callback(abandoned: bool):
        return chapter.pick(complete_trip(abandoned))

    chapter.clear()
    chapter.app.push_screen(MineScreen(), screen_callback)


def pick_unlock_mine():
    mines: list[Mine] = [mine for mine in MINES.values() if mine not in player.mines_available]
    options = [
        (mine.get_unlock_tui_arr(player.level), partial(unlock_mine, mine)) for mine in mines
    ] + [
        (["", "Go Back"], pick_mine),
    ]
    return PickArgs(
        message="Which mine would you like to unlock?",
        options=options,  # type:ignore
        subtitle=f"""{Icons.MINERAL}: Normal Mine
{Icons.RESOURCE}: Resource Mine
{Icons.DAMAGE}: Combat Zone
{Icons.DEATH}: Risk of Companian Demise""",
    )


def unlock_mine(mine: Mine):
    if player.level < mine.min_player_level:
        return PickArgs(
            message="You aren't a high enough level for this mine",
            options=[("Bummer!", pick_unlock_mine)],
        )
    if player.gold < mine.cost:
        return PickArgs(
            message="You don't have enough gold to unlock this mine",
            options=[("Bummer!", pick_unlock_mine)],
        )
    player.gold -= mine.cost
    player.mines_available.append(mine)
    FileManager.save(player)
    return PickArgs(
        message=f"You have unlocked {mine.name}",
        options=[("Sweet!", pick_mine)],
    )


def complete_trip(abandoned: bool):
    if abandoned:
        trip.clear()
        return exit_mine()

    story_args_list: list[StoryArgs] = []

    stats.increment_int_stat(IntegerStatKeys.ENEMIES_DEFEATED, trip.enemies_defeated)
    stats.increment_int_stat(IntegerStatKeys.BATTLES_WON, trip.battles_won)
    stats.increment_int_stat(IntegerStatKeys.MINERALS_MINED, len(trip.minerals_mined))
    if player.army.defeated:
        stats.increment_int_stat(IntegerStatKeys.ARMY_DEFEATS)
        trip.subtract_losses()
        story_args_list.append(
            StoryArgs(
                message="[red1]You lost the battle![/]\n\n"
                f"You were defeated in {trip.mine.icon} [dodger_blue1]{trip.mine.name}[/]. "
                f"You lost 1/{LOST_RATIO} of the items you found and xp you gained.",
                response="Bummer!",
                subtitle=f"You survived {int(trip.total_seconds / 60)} minute(s)",
            )
        )
    else:
        stats.increment_int_stat(IntegerStatKeys.TRIPS_FINISHED)

    starting_level = player.level
    if len(player.army) > 1:
        xp = int(trip.experience_gained * 1 / 2 * len(player.army) * macguffin.xp_boost)
        player.add_available_xp(xp)
    else:
        player.add_experience(int(trip.experience_gained * macguffin.xp_boost))

    if player.level > starting_level:
        story_args_list.append(
            StoryArgs(
                # pylint: disable=line-too-long
                message=f"[green1]\n You leveled up from {Icons.LEVEL} {Formatter.level(starting_level)} to {Icons.LEVEL} {Formatter.level(player.level)}.",
                response="Sweet!",
            )
        )

    if trip.mine.type == MineType.COMBAT:
        trip.minerals_mined = []
        trip.items_found = []
        story_args_list.append(
            StoryArgs(
                message="The goods collected on your trip in the ⚔️  Combat Zone "
                "were donated to the training facility.",
            )
        )
    player.inventory.add_items(trip.items_found + trip.minerals_mined)

    for ally in trip.allies_gained:
        player.add_ally(ally)
        if ally.species not in player.discovered_species:
            player.discovered_species.append(ally.species)
            message = "✨ You have discovered a new species! ✨\n"
            subtitle = (
                f"{ally.species.icon} [bold yellow1]{ally.species.name}[/]\n\n"
                f"{ally.name} has joined your army. Read and discover more about "
                f"{ally.species.icon} {ally.species.name}(s) in your [bold underline]Journal[/]"
            )
            story_args_list.append(
                StoryArgs(message=message, response="Awesome!", subtitle=subtitle)
            )

    story_args_list.append(
        StoryArgs(
            message=f"Your mining trip in {trip.mine.icon} [dodger_blue1]{trip.mine.name}[/]\n",
            subtitle=trip.tui_table,
        )
    )

    if facility.has_research("speed_up_time"):
        increase = RESEARCH["speed_up_time"].player_value + 100
        trip.total_seconds = int(trip.total_seconds * increase / 100)

    progress = trip.mine.player_progress
    progress.minutes += trip.total_seconds / 60.0
    progress.kills += trip.enemies_defeated
    progress.minerals += len(trip.minerals_mined)
    if trip.mine.win_criteria:
        if trip.mine.complete and trip.mine not in player.mines_completed:
            player.mines_completed.append(trip.mine)
            story_args_list.append(
                StoryArgs(
                    message=f"You have completed {trip.mine.icon} "
                    f"[dodger_blue1]{trip.mine.name}[/]! 🎉",
                    response="Heck yeah!",
                )
            )
        elif not trip.mine.complete:
            story_args_list.append(
                StoryArgs(
                    message=f"You have completed a mining trip in {trip.mine.icon} "
                    f"[dodger_blue1]{trip.mine.name}[/].\n",
                    subtitle=trip.mine.tui_progress,
                    response="Thanks for the update",
                )
            )

    trip.clear()
    FileManager.multi_save(player, stats, trip)
    return story_builder(story_args_list, exit_mine)


def available_species(mine: Mine) -> list[Species]:
    if not mine.companion_rarity:
        return []
    species = []
    for i in range(mine.companion_rarity):
        tier = SPECIES_TIERS[i]
        species.extend(SPECIES[s] for s in tier)
    return species


def unlock_species_emojies(species: list[Species]) -> list[str]:
    return [s.icon if s in player.discovered_species else "❓" for s in species]
