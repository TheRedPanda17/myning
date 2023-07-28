from blessed.terminal import Terminal

from myning.utils.ui_consts import Colors

LINE_LIMIT = 100

term = Terminal()


def print_level_up(level):
    print(f"{term.green}\n Leveled up to level {Colors.LEVEL}{term.underline}{level}{term.normal}")


def print_name(name):
    print(term.bold(f"\n{name}:"), end="")


def print_entity_speech(player, text, wait=True):
    print_name(player.name)
    print(" ", end="")
    narrate(
        text,
        line_limit=LINE_LIMIT - len(player.name),
        indent_count=len(player.name) + 2,
        wait=wait,
    )


def narrate(*text, line_limit=LINE_LIMIT, indent_count=0, wait=True):
    text = "".join(text)
    words = text.split(" ")

    chars = 0
    line = ""
    indent = " " * indent_count if indent_count else ""
    for word in words:
        if chars + len(word) < line_limit:
            line += f"{word} "
            chars += len(word) + 1
        else:
            print(line, end="\n")

            chars = len(word) + 1 + indent_count
            line = f"{indent}{word} "

    print(line, end="")

    if wait:
        input()


def get_character_speech(player):
    print_name(player.name)
    print(" ... ", end="")
    return input()


def stat_string(stat_name, stat, newline=True):
    s = term.underline(f"{stat_name}:") + f" {stat}"
    if newline:
        s += "\n"

    return s


def damage_string(attacker, defender, damage, friendly_attacker, dodged, critted):
    if friendly_attacker:
        attacker_color = term.green
        defender_color = term.red
    else:
        attacker_color = term.red
        defender_color = term.green

    dodge = "🍃" if dodged else " "
    crit = "🩸" if critted else "  "
    killed = "❌" if defender.health <= 0 else " "
    return [
        attacker_color(attacker.name),
        f"{crit} ({damage}) {dodge}",
        defender_color(defender.name),
        killed,
    ]


def bonus_string(bonus: int):
    bonus = round(bonus, 2)
    if bonus > 1:
        return f"{term.bold}{term.green}{bonus * 100}{term.normal} % damage bonus"
    elif bonus == 1:
        return f"{term.bold}no{term.normal} damage bonus"
    return f"{term.bold}{term.red}{bonus * 100}{term.normal} % damage penalty"


def print_battle_results(victory):
    print(
        f"{term.green if victory else term.red}\n\nYou {'won' if victory else 'lost'} the battle!{term.normal}"
    )


def get_race_discovery_message(ally_name: str, race_name: str, race_icon: str):
    title = f"\n✨ You have discovered a new race! ✨"
    sub_title = f"\n{race_icon} {term.yellow}{term.bold}{race_name}{term.normal}"
    sub_title += f"\n\n{ally_name} has joined your army. Read and discover more about "
    sub_title += (
        f"{race_icon} {race_name}(s) in your {term.bold}{term.underline}journal{term.normal}."
    )
    return title, sub_title
