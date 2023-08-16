from typing import Optional

from myning.config import XP_COST
from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_character
from myning.utils.io import get_int_input, pick
from myning.utils.output import narrate
from myning.utils.ui import columnate, get_exp_string, get_gold_string
from myning.utils.utils import fibonacci, get_random_array_item


def play():
    player = Player()
    cont = True
    while cont:
        title = "Upgrade Your Allies or Hire More Warriors"
        if player.allies:
            sub_title = f"You have {player.exp_available} xp to distribute."
            options = player.army.abbreviated
        else:
            sub_title = ""
            options = []

        if player.has_upgrade("auto_exp"):
            options.append("Auto-Add Xp")
        if player.has_upgrade("auto_ghost_xp"):
            options.append("Auto-Add Xp to Ghosts Only")
        options.append("Hire Muscle")
        options.append("Fire Muscle")
        options.append("Buy Exp")
        options.append("Go Back")

        option, index = pick(options, title, sub_title=sub_title)
        if option == "Go Back":
            return
        elif option == "Hire Muscle":
            if (member := hire_muscle(player)) is not None:
                player.add_ally(member)
        elif option == "Fire Muscle":
            member = fire_muscle(player.army[1:])
            if member:
                player.fire_ally(member)
        elif option == "Buy Exp":
            buy_exp(player)
        elif option == "Auto-Add Xp":
            auto_add_exp()
        elif option == "Auto-Add Xp to Ghosts Only":
            auto_add_ghost_xp()
        else:
            add_exp(player.army[index])

        FileManager.save(player)


def add_exp(member: Character):
    player = Player()

    if player.exp_available == 0:
        pick(
            ["Go Back"],
            "You have no experience to distribute",
        )
        return
    if member.level >= player.level and member.name != player.name:
        pick(
            ["Go Back"],
            f"You need to level up {player.name} before you can level up {member.name}",
        )
        return

    xp_for_level = fibonacci(member.level + 1)
    xp_for_level -= member.experience

    if player.has_upgrade("level_up_barracks"):
        option, i = pick(
            [f"Level {member.name} Up", "Add xp Manually", "Go Back"],
            "How would you like to add xp?",
        )
        if option == "Go Back":
            return
        if i == 0:
            if xp_for_level > player.exp_available:
                pick(["Bummer!"], f"You don't have enough xp to level {member.name} up.")
                return

            player.remove_available_xp(xp_for_level)
            member.add_experience(xp_for_level, display=False)
            return

    input_text = f"How much of your {get_exp_string(player.exp_available)} would you like to give {member.name} ({member.exp_str})?"
    xp = get_int_input(
        input_text,
        subtitle=f"{xp_for_level} xp until level {member.level + 1}",
        max_value=player.exp_available,
    )
    if xp:
        player.remove_available_xp(xp)
        member.add_experience(xp, display=False)


def auto_add_exp():
    player = Player()

    option, _ = pick(["Yes", "No"], "Are you sure you want to auto-add all your exp?")
    if option == "No":
        return
    if player.exp_available == 0:
        pick(
            ["I should have thought of that..."],
            "You have no experience to distribute",
        )
        return

    player.army.reverse()
    while player.exp_available > 0:
        member = min(player.army, key=lambda m: m.level)
        if member.level >= player.level and member.name != player.name:
            member = player

        exp = fibonacci(member.level + 1)
        exp -= member.experience
        if exp > player.exp_available:
            exp = player.exp_available
        player.remove_available_xp(exp)
        member.add_experience(exp, display=False)


def auto_add_ghost_xp():
    player = Player()

    option, _ = pick(
        ["Yes", "No"], "Are you sure you want to auto-add all your xp to your revived companions?"
    )
    if option == "No":
        return
    if player.exp_available == 0:
        pick(
            ["I should have thought of that..."],
            "You have no experience to distribute",
        )
        return

    player.army.reverse()
    ghosts = list(filter(lambda m: m.is_ghost, player.army))

    while player.exp_available > 0:
        member = min(ghosts, key=lambda m: m.level)
        if member.level >= player.level and member.name != player.name:
            member = player

        exp = fibonacci(member.level + 1)
        exp -= member.experience
        if exp > player.exp_available:
            exp = player.exp_available
        player.remove_available_exp(exp)
        member.add_experience(exp, display=False)


def hire_muscle(player: Player) -> Optional[Character]:
    entities = [
        generate_character(
            [1, 1], max_items=1, species=get_random_array_item(player.discovered_species)
        )
        for _ in range(20)
    ]
    entities.sort(key=lambda e: e.name)

    while True:
        gold = [full_cost(len(player.army), entity) for entity in entities]
        options = columnate(
            [
                [
                    entity.icon,
                    entity.name,
                    entity.level_str,
                    f"⚔️ {entity.stats['damage']}",
                    f"🛡️ {entity.stats['armor']}",
                    f"❤️‍ {entity.health_mod} ",
                    get_gold_string(gold[i]),
                ]
                for i, entity in enumerate(entities)
            ]
        )

        option, i = pick([*options, "Go Back"], "Who would you like to hire?")
        if option == "Go Back":
            return None

        if player.pay(
            gold[i],
            failure_msg="Not enough gold.",
            failure_option="Bummer",
            confirmation_msg=f"Are you sure you want to hire "
            f"{entities[i].name} for {gold[i]} gold?",
        ):
            return entities[i]
        return None


def fire_muscle(army: Army):
    while True:
        if not army:
            narrate("\nYou ain't got nobody to fire!")
            return

        # choose member
        message = "Which Ally do you want to fire?"
        options = army.abbreviated

        option, index = pick([*options, "Go Back"], message)
        if option == "Go Back":
            return
        member = army[index]

        # confirm selection
        confirm_copy = {"message": f"Are you sure you want to fire {member}?"}
        if member.equipment.all_items:
            confirm_copy[
                "sub_title"
            ] = f"...and return the following to your inventory: \n{member.equipment}"
        confirmed, _ = pick(["Yes", "No"], **confirm_copy)

        if confirmed == "Yes":
            return member


def full_cost(army_size: int, entity: Character) -> int:
    gold = entity_cost(army_size)
    return int(max((gold / 2 * entity.premium), gold))


def entity_cost(army_size: int):
    multiplier = 1
    ratio = 0
    for i in range(army_size):
        ratio += 0.075 * i
        multiplier += ratio
    return int(50 * multiplier)


def buy_exp(player: Player):
    xp = get_int_input(
        f"How much xp would you like to buy for your allies? ({XP_COST}g/xp)",
        max_value=int(player.gold / XP_COST),
    )
    if xp and player.pay(xp * XP_COST):
        player.add_available_xp(xp)
