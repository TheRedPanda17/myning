import random
from functools import partial
from typing import TYPE_CHECKING

from rich.table import Table
from rich.text import Text

from myning.chapters import DynamicArgs, Option, PickArgs, main_menu
from myning.config import XP_COST
from myning.objects.character import Character
from myning.objects.player import Player
from myning.tui.input import IntInputScreen
from myning.utilities.fib import fibonacci
from myning.utilities.formatter import Formatter
from myning.utilities.generators import generate_character
from myning.utilities.pick import confirm
from myning.utilities.ui import Colors, Icons

if TYPE_CHECKING:
    from myning.tui.chapter import ChapterWidget

player = Player()


def enter():
    member_arrs = [member.abbreviated_arr for member in player.army]
    handlers = [partial(add_xp, member) for member in player.army]
    options = [Option(label, handler) for label, handler in zip(member_arrs, handlers)]

    if player.has_upgrade("auto_exp"):
        options.append(Option(["", "Auto-Add xp"], auto_add_xp))
    if player.has_upgrade("auto_ghost_xp"):
        options.append(Option(["", "Auto-Add xp to Ghosts Only"], auto_add_ghost_xp))

    options.extend(
        (
            Option(["", "Hire Muscle"], pick_hire_muscle),
            Option(["", "Fire Muscle"], pick_fire_muscle),
            Option(["", "Buy xp"], buy_xp),
            Option(["", "Go Back"], main_menu.enter),
        )
    )
    return PickArgs(
        message="Upgrade Your Allies or Hire More Warriors",
        options=options,
        subtitle=f"You have {player.exp_available} xp to distribute." if player.allies else None,
        column_titles=player.abbreviated_column_titles,
    )


def pick_hire_muscle():
    entities = [
        generate_character((1, 1), max_items=1, species=random.choice(player.discovered_species))
        for _ in range(20)
    ]
    entities.sort(key=lambda e: e.name)
    cost = [full_cost(len(player.army), entity) for entity in entities]
    options = [
        Option(
            [
                entity.icon,
                entity.name,
                Text.from_markup(f"[red1]{entity.stats['damage']}[/]", justify="right"),
                Text.from_markup(f"[dodger_blue1]{entity.stats['armor']}[/]", justify="right"),
                Text.from_markup(f"[cyan1]{entity.level}[/]", justify="right"),
                Text.from_markup(f"[green1]{entity.health_mod}[/]", justify="right"),
                Text.from_markup(Formatter.gold(cost[i]), justify="right"),
            ],
            partial(confirm_hire_muscle, entity, cost[i]),
        )
        for i, entity in enumerate(entities)
    ]
    options.append(Option(["", "Go Back"], enter))
    return PickArgs(
        message="Who would you like to hire?",
        options=options,
        column_titles=[
            "",
            "Name",
            Text(Icons.DAMAGE, justify="center"),
            Text(Icons.ARMOR, justify="center"),
            Text(Icons.LEVEL, justify="center"),
            Text(Icons.HEART, justify="center"),
            "",
        ],
    )


def confirm_hire_muscle(entity: Character, cost: int):
    if player.gold < cost:
        return PickArgs(
            message="Not enough gold.",
            options=[Option("Bummer", enter)],
        )
    return PickArgs(
        message=f"Are you sure you want to hire {entity.icon} {entity.name} "
        f"for {Formatter.gold(cost)}?",
        options=[
            Option("Yes", partial(hire_muscle, entity, cost)),
            Option("No", enter),
        ],
    )


def hire_muscle(entity: Character, cost: int):
    player.gold -= cost
    player.add_ally(entity)
    return enter()


def pick_fire_muscle():
    if not player.allies:
        return PickArgs(
            message="You ain't got nobody to fire!",
            options=[Option("I should have thought of that...", enter)],
        )
    member_arrs = [member.abbreviated_arr for member in player.allies]
    handlers = [partial(confirm_fire_muscle, member) for member in player.allies]
    options = [
        Option(label, handler, enable_hotkeys=False)
        for label, handler in zip(member_arrs, handlers)
    ]
    options.append(Option(["", "Go Back"], enter))
    return PickArgs(
        message="Which Ally do you want to fire?",
        options=options,
        column_titles=player.abbreviated_column_titles,
    )


def confirm_fire_muscle(member: Character):
    message = f"Are you sure you want to fire {member}?"
    subtitle = None
    if member.equipment.all_items:
        subtitle = Table.grid()
        subtitle.add_row(Formatter.locked("...and return the following to your inventory:\n"))
        subtitle.add_row(member.equipment.table)
    return PickArgs(
        message=message,
        options=[
            Option("Yes", partial(fire_muscle, member)),
            Option("No", enter),
        ],
        subtitle=subtitle,
    )


def fire_muscle(member: Character):
    player.fire_ally(member)
    return enter()


def add_xp(member: Character):
    if not player.exp_available:
        return PickArgs(
            message="You have no experience to distribute",
            options=[Option("Go Back", enter)],
        )
    if member is not player and member.level >= player.level:
        return PickArgs(
            message=f"You need to level up {player.name} before you can level up {member.name}",
            options=[Option("Go Back", enter)],
        )
    if player.has_upgrade("level_up_barracks"):
        xp_for_level = fibonacci(member.level + 1)
        xp_for_level -= member.experience
        return PickArgs(
            message="How would you like to add xp?",
            options=[
                Option(
                    f"Level {member.name} Up ([{Colors.XP}]{xp_for_level} xp[/] needed)",
                    partial(level_up, member),
                ),
                Option("Add xp Manually", partial(add_xp_manually, member)),
                Option("Go Back", enter),
            ],
            subtitle=f"You have {player.exp_available} xp to distribute.",
        )
    return add_xp_manually(member)


def level_up(member: Character):
    xp_for_level = fibonacci(member.level + 1)
    xp_for_level -= member.experience
    if xp_for_level > player.exp_available:
        return PickArgs(
            message=f"You don't have enough xp to level {member.name} up.",
            options=[Option("Bummer!", enter)],
        )
    player.remove_available_xp(xp_for_level)
    member.add_experience(xp_for_level)
    return enter()


def add_xp_manually(member: Character):
    xp_for_level = fibonacci(member.level + 1)
    xp_for_level -= member.experience
    question = (
        f"How much of your {Formatter.xp(player.exp_available)} "
        f"would you like to give {member.name} ({member.exp_str})?"
    )
    placeholder = f"{xp_for_level} xp until level {member.level+1}"

    def add_xp_callback(chapter: "ChapterWidget"):
        def screen_callback(xp: int | None):
            if xp is not None:
                player.remove_available_xp(xp)
                member.add_experience(xp)
                chapter.pick(enter())

        chapter.app.push_screen(
            IntInputScreen(
                question,
                placeholder=placeholder,
                minimum=1,
                maximum=player.exp_available,
            ),
            screen_callback,
        )

    return DynamicArgs(callback=add_xp_callback)


def buy_xp():
    question = f"How much xp would you like to buy for your allies? ({Formatter.gold(XP_COST)}/xp)"
    maximum = int(player.gold / XP_COST)
    placeholder = f"You can afford up to {maximum} xp"

    def buy_xp_callback(chapter: "ChapterWidget"):
        def screen_callback(xp: int | None):
            if xp is not None:
                player.gold -= xp * XP_COST
                player.add_available_xp(xp)
                chapter.pick(enter())

        chapter.app.push_screen(
            IntInputScreen(
                question,
                placeholder=placeholder,
                minimum=1,
                maximum=maximum,
            ),
            screen_callback,
        )

    return DynamicArgs(callback=buy_xp_callback)


@confirm("Are you sure you want to auto-add all your exp?", enter)
def auto_add_xp():
    if player.exp_available == 0:
        return PickArgs(
            message="You have no experience to distribute",
            options=[Option("I should have thought of that...", enter)],
        )

    player.army.reverse()
    while player.exp_available > 0:
        member = min(player.army, key=lambda m: m.level)
        if member.level >= player.level and member.name != player.name:
            member = player

        xp = fibonacci(member.level + 1)
        xp -= member.experience
        xp = min(xp, player.exp_available)
        player.remove_available_xp(xp)
        member.add_experience(xp)

    return enter()


@confirm("Are you sure you want to auto-add all your xp to your revived companions?", enter)
def auto_add_ghost_xp():
    if player.exp_available == 0:
        return PickArgs(
            message="You have no experience to distribute",
            options=[Option("I should have thought of that...", enter)],
        )

    player.army.reverse()
    ghosts = [m for m in player.army if m.is_ghost]
    while player.exp_available > 0:
        member = min(ghosts, key=lambda m: m.level)
        if member.level >= player.level and member.name != player.name:
            member = player

        xp = fibonacci(member.level + 1)
        xp -= member.experience
        xp = min(xp, player.exp_available)
        player.remove_available_xp(xp)
        member.add_experience(xp)

    return enter()


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
