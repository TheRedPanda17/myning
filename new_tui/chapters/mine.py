from functools import partial
from itertools import zip_longest

from rich.style import Style
from rich.table import Table

from myning.config import MINES, RACES
from myning.objects.mine import Mine
from myning.objects.player import Player
from myning.objects.race import Race
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.race_rarity import RACE_TIERS
from myning.utils.ui_consts import Icons
from new_tui.chapters import Option, PickArgs, town
from new_tui.formatter import Colors, columnate

player = Player()
trip = Trip()


def enter():
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
    options: list[Option] = [(f"{m} minutes", partial(start_mining, mine, m)) for m in minutes]
    options.append(("Go Back", enter))
    subtitle = Table.grid(padding=(0, 1, 0, 0))
    subtitle.add_column(style=Style(color=Colors.LOCKED))
    subtitle.add_column(style=Style(color=Colors.LOCKED))
    subtitle.add_row()
    if mine.win_criteria:
        subtitle.add_row("Progress:", mine.progress_bar)
        subtitle.add_row(
            "Minerals:",
            remaining_str(mine.player_progress.minerals, mine.win_criteria.minerals),
        )
        subtitle.add_row(
            "Kills:",
            remaining_str(mine.player_progress.kills, mine.win_criteria.kills),
        )
        subtitle.add_row(
            "Minutes Survived:",
            remaining_str(int(mine.player_progress.minutes), mine.win_criteria.minutes),
        )
    subtitle.add_row("Risk of Demise:", f"{Icons.DEATH} {mine.death_chance_tui_str}")
    if mine.companion_rarity:
        subtitle.add_row("Discoverable:", "".join(unlock_species_emojies(available_species(mine))))
    return PickArgs(
        message=f"How long would you like to mine in {mine.icon} {mine.name}?",
        options=options,
        subtitle=subtitle,
    )


def start_mining(mine: Mine, minutes: int):
    # trip.start_trip(minutes * 60)
    return PickArgs(
        message=f"You are going to mine in {mine.name} for {minutes} minutes",
        options=[("Cool", enter)],
    )


def pick_unlock_mine():
    mines: list[Mine] = [mine for mine in MINES.values() if mine not in player.mines_available]

    rows = columnate([mine.get_unlock_tui_arr(player.level) for mine in mines] + [["", "Go Back"]])
    handlers = [partial(unlock_mine, mine) for mine in mines] + [enter]
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
        options=[("Sweet!", enter)],
    )


def remaining_str(current: int, total: int):
    return f"{current}/{total}" if current < total else "Complete"


def available_species(mine: Mine) -> list[Race]:
    if not mine.companion_rarity:
        return []
    species = []
    for i in range(0, mine.companion_rarity):
        tier = RACE_TIERS[i]
        for s in tier:
            species.append(RACES[s])
    return species


def unlock_species_emojies(species: list[Race]) -> list[str]:
    player = Player()
    emojis = []
    for spec in species:
        if spec in player.discovered_races:
            emojis.append(spec.icon[0])
        else:
            emojis.append("❓")
    return emojis
