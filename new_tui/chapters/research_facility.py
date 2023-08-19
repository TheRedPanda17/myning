from functools import partial

from myning.config import RESEARCH
from myning.objects.character import Character
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.upgrade import Upgrade
from myning.utils.file_manager import FileManager
from new_tui.chapters import Option, PickArgs, main_menu
from new_tui.formatter import Formatter

player = Player()
facility = ResearchFacility()
RESEARCH: dict[str, Upgrade]


def enter():
    return PickArgs(
        message=f"Level {facility.level} Research Facility",
        options=[
            ("Assign Researchers", pick_assign),
            ("Remove Reasearcher", pick_remove),
            ("Research", pick_research),
            ("Upgrade Facility", confirm_upgrade),
            ("Go Back", main_menu.enter),
        ],
        subtitle=f"{len(facility.army)}/{facility.level} researchers assigned\n"
        f"{round(facility.points_per_hour, 2)} research points / hr",
    )


def pick_assign():
    character_arrs = [character.abbreviated_tui_arr for character in player.army[1:]]
    handlers = [partial(assign, character) for character in player.army[1:]]
    options: list[Option] = list(zip(character_arrs, handlers))
    options.append((["", "Go Back"], enter))
    return PickArgs(
        message="Choose companion to assign to research",
        options=options,
        subtitle=f"{len(facility.army)}/{facility.level} researchers assigned\n"
        f"{round(facility.points_per_hour, 2)} research points / hr",
        column_titles=player.abbreviated_tui_column_titles,
    )


def assign(character: Character):
    if not facility.has_free_space:
        return PickArgs(
            message="You can't add researchers until you upgrade your lab",
            options=[("Bummer!", enter)],
        )
    facility.add_researcher(character)
    player.move_ally_out(character)
    FileManager.multi_save(player, facility)
    return pick_assign()


def pick_remove():
    if not facility.army:
        return PickArgs(
            message="You have no companions currently researching",
            options=[("Go Back", enter)],
        )
    character_arrs = [character.abbreviated_tui_arr for character in facility.army]
    handlers = [partial(remove, character) for character in facility.army]
    options: list[Option] = list(zip(character_arrs, handlers))
    options.append((["", "Go Back"], enter))
    return PickArgs(
        message="Choose companion to remove from research",
        options=options,
        subtitle=f"{len(facility.army)}/{facility.level} researchers assigned\n"
        f"{round(facility.points_per_hour, 2)} research points / hr",
        column_titles=player.abbreviated_tui_column_titles,
    )


def remove(character: Character):
    facility.remove_researcher(character)
    player.add_ally(character)
    FileManager.multi_save(player, facility)
    return pick_remove()


def pick_research():
    available_research = [research for research in RESEARCH.values() if not research.max_level]
    options = [
        (research.arr, partial(purchase_research, research)) for research in available_research
    ]
    return PickArgs(
        message="What would you like to research?",
        options=[*options, ("Go Back", enter)],
    )


def purchase_research(research: Upgrade):
    if facility.points < research.cost:
        return PickArgs(
            message="You don't have enough research points!",
            options=[("Bummer!", pick_research)],
        )
    facility.purchase(research.cost)
    research.level += 1
    if research.id not in [u.id for u in facility.research]:
        facility.research.append(research)
    FileManager.save(facility)
    return pick_research()


def confirm_upgrade():
    return PickArgs(
        message="Are you sure you want to upgrade your research for "
        f"{Formatter.research_points(facility.upgrade_cost)}?",
        options=[
            (f"Upgrade to level {facility.level + 1}", upgrade),
            ("Maybe Later", enter),
        ],
    )


def upgrade():
    if facility.points < facility.upgrade_cost:
        return PickArgs(
            message="You don't have enough research points",
            options=[("Bummer!", enter)],
        )
    facility.purchase(facility.upgrade_cost)
    facility.level_up()
    FileManager.save(facility)
    return confirm_upgrade()
