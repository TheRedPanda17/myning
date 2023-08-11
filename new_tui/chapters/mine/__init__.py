from functools import partial
from itertools import zip_longest

from rich.table import Table

from myning.config import MINES, RACES
from myning.objects.mine import Mine, MineType
from myning.objects.player import Player
from myning.objects.race import Race
from myning.objects.trip import LOST_RATIO, Trip
from myning.utils.file_manager import FileManager
from myning.utils.race_rarity import RACE_TIERS
from myning.utils.ui_consts import Icons
from new_tui.chapters import DynamicArgs, Option, PickArgs, StoryArgs, town
from new_tui.chapters.mine.screen import MineScreen
from new_tui.formatter import Colors, columnate
from new_tui.utilities import story_builder
from new_tui.view.chapter import ChapterWidget

player = Player()
trip = Trip()


def pick_mine():
    # ProgressBar cannot be columnated, but individual Table rows cannot be extracted to print
    # separately. Since we know that progress is always the same length, columnate everything else
    # then combine into single-row Tables
    rows = columnate(
        [mine.tui_arr for mine in player.mines_available]
        + [
            ["", "Unlock New Mine"],
            ["", "Go Back"],
        ]
    )
    rows_with_progress = []
    for row, mine in zip_longest(rows, player.mines_available):
        table = Table.grid(padding=(0, 1, 0, 0))
        if mine and mine.win_criteria:
            if mine.complete:
                table.add_row(row, "✨ cleared ✨")
            else:
                table.add_row(row, mine.progress_bar)
        else:
            table.add_row(row, "")
        for col in table.columns:
            col.no_wrap = True
        rows_with_progress.append(table)

    handlers = [partial(pick_time, mine) for mine in player.mines_available] + [
        pick_unlock_mine,
        town.enter,
    ]
    has_death_mine = any(mine.has_death_action for mine in player.mines_available)

    return PickArgs(
        message="Which mine would you like to enter?",
        options=list(zip(rows_with_progress, handlers)),
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
                ("Take me there!", partial(town.unimplemented, "Healer")),
                ("Got it, thanks.", town.enter),
            ],
        )

    trip.mine = mine
    trip.start_trip(minutes * 60)
    return DynamicArgs(callback=mine_callback)


def mine_callback(chapter: ChapterWidget):
    def screen_callback(abandoned: bool):
        return chapter.pick(complete_trip(abandoned))

    chapter.app.push_screen(MineScreen(), screen_callback)


def pick_unlock_mine():
    mines: list[Mine] = [mine for mine in MINES.values() if mine not in player.mines_available]

    rows = columnate([mine.get_unlock_tui_arr(player.level) for mine in mines] + [["", "Go Back"]])
    handlers = [partial(unlock_mine, mine) for mine in mines] + [pick_mine]
    return PickArgs(
        message="Which mine would you like to unlock?",
        options=list(zip(rows, handlers)),
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
        return town.enter()

    story_args_list: list[StoryArgs] = []

    if player.army.defeated:
        trip.subtract_losses()
        story_args_list.append(
            StoryArgs(
                message=f"You were defeated in {trip.mine.icon} [dodger_blue1]{trip.mine.name}[/]. "
                f"You lost 1/{LOST_RATIO} of the items you found and xp you gained.",
                response="Bummer!",
                subtitle=f"You survived {int(trip.total_seconds / 60)} minute(s)",
            )
        )
    player.add_xp(trip.experience_gained)
    player.incr_trip()

    if trip.mine.type == MineType.COMBAT:
        trip.minerals_mined = []
        trip.items_found = []
        story_args_list.append(
            StoryArgs(
                message="The goods collected on your trip in the ⚔️ Combat Zone "
                "were donated to the training facility.",
            )
        )
    player.inventory.add_items(trip.items_found + trip.minerals_mined)

    for ally in trip.allies_gained:
        player.add_ally(ally)
        if ally.race not in player.discovered_races:
            player.discovered_races.append(ally.race)
            message = "✨ You have discovered a new species! ✨\n"
            subtitle = (
                f"{ally.race.icon} [bold yellow1]{ally.race.name}[/]\n\n"
                f"{ally.name} has joined your army. Read and discover more about "
                f"{ally.race.icon} {ally.race.name}(s) in your [bold underline]Journal[/]"
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
    return story_builder(story_args_list, town.enter())


def available_species(mine: Mine) -> list[Race]:
    if not mine.companion_rarity:
        return []
    species = []
    for i in range(mine.companion_rarity):
        tier = RACE_TIERS[i]
        species.extend(RACES[s] for s in tier)
    return species


def unlock_species_emojies(species: list[Race]) -> list[str]:
    return [s.icon if s in player.discovered_races else "❓" for s in species]
