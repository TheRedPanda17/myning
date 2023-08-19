from myning.config import RESEARCH
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.ui import columnate, get_research_string


def play():
    macguffin = Macguffin()
    while True:
        facility = ResearchFacility()
        facility.check_in(macguffin.research_boost)
        FileManager.save(facility)
        title = f"Level {facility.level} Research ({get_research_string(facility.points)})"
        options = [
            "Assign Researchers",
            "Remove Reasearcher",
            "Research",
            "Upgrade Facility",
            "Go Back",
        ]
        option, index = pick(
            options,
            title,
            sub_title=f"{len(facility._researchers)}/{facility.level} researchers assigned\n"
            f"{round(facility.points_per_hour(macguffin.research_boost), 2)} research points / hr",
        )

        if option == "Go Back":
            return
        elif index == 0:
            assign_researchers()
        elif index == 1:
            fire_researchers()
        elif index == 2:
            purchase_research()
        else:
            upgrade_facility()


def assign_researchers():
    macguffin = Macguffin()
    while True:
        player = Player()
        facility = ResearchFacility()
        pph = facility.points_per_hour(macguffin.research_boost)

        title = f"Choose companions to start researching ({get_research_string(pph)} / hr)"
        options = player.army.abbreviated
        options.append("Go Back")

        option, index = pick(options, title)
        if option == "Go Back":
            return
        else:
            if not facility.has_free_space:
                pick(
                    ["Bummer!"],
                    "You can't add researchers until you upgrade your lab",
                )
                continue
            character = player.army[index]
            facility.add_researcher(character)
            player.move_ally_out(character)

            FileManager.multi_save(player, facility)


def fire_researchers():
    macguffin = Macguffin()
    while True:
        player = Player()
        facility = ResearchFacility()
        pph = facility.points_per_hour(macguffin.research_boost)

        title = f"Choose companions to stop researching ({get_research_string(pph)} / hr)"
        options = facility.army.abbreviated
        options.append("Go Back")

        option, index = pick(options, title)
        if option == "Go Back":
            return
        else:
            character = facility.army[index]
            facility.remove_researcher(character)
            player.add_ally(character)

            FileManager.multi_save(player, facility)


def purchase_research():
    while True:
        facility = ResearchFacility()

        available_research = [research for research in RESEARCH.values() if not research.max_level]

        options = columnate([research.string_arr for research in available_research])
        option, index = pick(
            [*options, "Go Back"],
            "What would you like to research?",
        )
        if option == "Go Back":
            return

        research = available_research[index]
        if research.cost < facility.points:
            facility.purchase(research.cost)
            research.level += 1
            if research.id not in [u.id for u in facility.research]:
                facility.research.append(research)
            FileManager.save(facility)


def upgrade_facility():
    while True:
        facility = ResearchFacility()

        _, index = pick(
            [f"Upgrade to level {facility.level + 1}", "Maybe Later"],
            f"Are you sure you want to upgrade your research for {get_research_string(facility.upgrade_cost)}?",
        )

        if index != 0:
            return None
        if facility.points < facility.upgrade_cost:
            pick(
                ["Bummer!"],
                "You don't have enough research points",
            )
            return
        facility.purchase(facility.upgrade_cost)
        facility.level_up()
        FileManager.save(facility)
