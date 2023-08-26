from functools import partial

from myning.chapters import Option, PickArgs, main_menu
from myning.config import RESEARCH
from myning.objects.character import Character
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.objects.upgrade import Upgrade
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter

player = Player()
macguffin = Macguffin()
facility = ResearchFacility()


def enter():
    return PickArgs(
        message=f"Level {facility.level} Research Facility",
        options=[
            Option("Assign Researchers", pick_assign, enable_hotkeys=True),
            Option("Remove Reasearcher", pick_remove, enable_hotkeys=True),
            Option("Research", pick_research, enable_hotkeys=True),
            Option("Upgrade Facility", confirm_upgrade, enable_hotkeys=True),
            Option("Go Back", main_menu.enter),
        ],
        subtitle=f"{len(facility.army)}/{facility.level} researchers assigned\n"
        f"{facility.points_per_hour(macguffin.research_boost):.2f} research points / hr",
    )


def pick_assign():
    character_arrs = [character.abbreviated_arr for character in player.army[1:]]
    handlers = [partial(assign, character) for character in player.army[1:]]
    options = [Option(label, handler) for label, handler in zip(character_arrs, handlers)]
    options.append(Option(["", "Go Back"], enter))
    return PickArgs(
        message="Choose companion to assign to research",
        options=options,
        subtitle=f"{len(facility.army)}/{facility.level} researchers assigned\n"
        f"{facility.points_per_hour(macguffin.research_boost):.2f} research points / hr",
        column_titles=player.abbreviated_column_titles,
    )


def assign(character: Character):
    if not facility.has_free_space:
        return PickArgs(
            message="You can't add researchers until you upgrade your lab",
            options=[Option("Bummer!", enter)],
        )
    facility.add_researcher(character)
    player.move_ally_out(character)
    FileManager.multi_save(player, facility)
    return pick_assign()


def pick_remove():
    if not facility.army:
        return PickArgs(
            message="You have no companions currently researching",
            options=[Option("Go Back", enter)],
        )
    character_arrs = [character.abbreviated_arr for character in facility.army]
    handlers = [partial(remove, character) for character in facility.army]
    options = [Option(label, handler) for label, handler in zip(character_arrs, handlers)]
    options.append(Option(["", "Go Back"], enter))
    return PickArgs(
        message="Choose companion to remove from research",
        options=options,
        subtitle=f"{len(facility.army)}/{facility.level} researchers assigned\n"
        f"{facility.points_per_hour(macguffin.research_boost):2f} research points / hr",
        column_titles=player.abbreviated_column_titles,
    )


def remove(character: Character):
    facility.remove_researcher(character)
    player.add_ally(character)
    FileManager.multi_save(player, facility)
    return pick_remove()


def pick_research():
    available_research = [research for research in RESEARCH.values() if not research.max_level]
    options = [
        Option(research.arr, partial(purchase_research, research), enable_hotkeys=True)
        for research in available_research
    ]
    return PickArgs(
        message="What would you like to research?",
        options=[*options, Option("Go Back", enter)],
    )


def purchase_research(research: Upgrade):
    if facility.points < research.cost:
        return PickArgs(
            message="You don't have enough research points!",
            options=[Option("Bummer!", pick_research)],
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
            Option(f"Upgrade to level {facility.level + 1}", upgrade, enable_hotkeys=True),
            Option("Maybe Later", enter),
        ],
    )


def upgrade():
    if facility.points < facility.upgrade_cost:
        return PickArgs(
            message="You don't have enough research points",
            options=[Option("Bummer!", enter)],
        )
    facility.purchase(facility.upgrade_cost)
    facility.level_up()
    FileManager.save(facility)
    return confirm_upgrade()
