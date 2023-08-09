import builtins
import string
import textwrap
from typing import Callable

from blessed import Terminal

from myning.config import MINES
from myning.objects.macguffin import Macguffin
from myning.objects.player import Player, get_title_string
from myning.objects.research_facility import ResearchFacility
from myning.objects.settings import Settings
from myning.utils.ui import columnate, get_gold_string, get_research_string, get_soul_string
from myning.utils.ui_consts import Icons

term = Terminal()

RESERVED_EXIT_PHRASES = (
    "back",
    "bummer!",
    "bummer",
    "exit",
    "go back",
    "i'll get on it",
    "maybe later",
    "no",
)
RESERVED_HOTKEYS = ["a", "e", "i", "j", "k", "q"]


def print(*values, **kwargs):
    """An override of the builtin print function that prefixes each line with two spaces."""
    if not values:
        builtins.print(**kwargs)
    else:
        for value in values:
            indented = textwrap.indent(str(value), "  ")
            builtins.print(indented, **kwargs)


def input(msg="", **kwargs):
    """An override of the builtin print function that prefixes each line with two spaces."""
    return builtins.input(f"  {msg}", **kwargs)


def get_dashboard(key=None):
    player = Player()
    compact = Settings().compact_mode
    research_facility = ResearchFacility()
    macguffin = Macguffin()

    if key:
        player._update_dashboard_settings(key)

    hide_army = player.dashboard_settings["a"]
    hide_equipment = player.dashboard_settings["e"]
    hide_inventory = player.dashboard_settings["i"]

    lines = []
    if compact:
        lines += player.army.summary_str.split("\n")
        lines += " "
    else:
        lines = [
            get_title_string("Your Army", "a"),
            "" if hide_army else str(player.army) + "\n",
        ]

        if len(player.army) == 1:
            lines.append(get_title_string("Equipment", "e"))
            if not hide_equipment:
                lines.append(str(player.equipment))
            lines.append("")

        lines.append(get_title_string("Inventory", "i"))
        lines.append("" if hide_inventory else str(player.inventory) + "\n")

    currencies = [[term.bold("Gold"), Icons.GOLD.value, get_gold_string(player.gold)]]

    if MINES["Large pit"] in player.mines_completed:
        currencies.append(
            [
                term.bold("Soul credits"),
                Icons.SOUL_CREDITS.value,
                get_soul_string(player.soul_credits),
            ]
        )

    if MINES["Cavern"] in player.mines_completed:
        research_facility.check_in(macguffin.research_boost)
        currencies.append(
            [
                term.bold("Research points"),
                Icons.RESEARCH_POINTS.value,
                get_research_string(research_facility.points),
            ]
        )
    if macguffin.xp_boost > 1:
        currencies.append(
            [
                term.bold("Macguffin"),
                Icons.MINERAL.value,
                f"{term.bold_gold(macguffin.mineral_percentage)} mineral value boost",
            ]
        )
        currencies.append(
            [
                "",
                Icons.XP.value,
                f"{term.bold_magenta(macguffin.xp_percentage)} xp boost",
            ]
        )
    if macguffin.research_boost > 1:
        currencies.append(
            [
                "",
                Icons.GRAVEYARD.value,
                f"{term.blue(macguffin.soul_credit_percentage)} soul credit boost",
            ]
        )
        currencies.append(
            [
                "",
                Icons.RESEARCH_FACILITY.value,
                f"{term.violetred1(macguffin.research_percentage)} research boost",
            ]
        )
        currencies.append(
            [
                "",
                Icons.PLANT.value,
                f"{term.green(macguffin.plant_percentage)} plant value boost",
            ]
        )

    return "\n".join(lines + columnate(currencies))


def get_int_input(
    prompt: str,
    subtitle: str = None,
    min_value: int = 0,
    max_value: int = None,
    dashboard: Callable[..., str] | None = None,
):
    if not dashboard:
        dashboard = get_dashboard

    def print_header():
        print(term.clear)
        print(dashboard())
        print()
        print(term.bold(prompt))
        if subtitle:
            print(term.snow4(subtitle))

    while True:
        with term.fullscreen():
            print_header()
            builtins.print(end="  ", flush=True)
            with term.cbreak():
                input_str = ""
                while True:
                    key = term.inkey()
                    if key.is_sequence:
                        if key.name == "KEY_ENTER":
                            break
                        elif key.name == "KEY_ESCAPE":
                            return
                        elif key.name == "KEY_BACKSPACE":
                            if input_str:
                                input_str = input_str[:-1]
                                builtins.print("\b \b", end="", flush=True)
                    elif key == "q":
                        return
                    elif key.isdigit():
                        input_str += key
                        builtins.print(key, end="", flush=True)

            try:
                value = int(input_str)
            except ValueError:
                prompt = "Please enter a valid number."
                continue
            if min_value is not None and value < min_value:
                prompt = f"Please enter a number greater than or equal to {min_value}."
                continue
            if max_value is not None and value > max_value:
                prompt = f"Please enter a number less than or equal to {max_value}."
                continue
            return value


def pick(
    options: list[str],
    message: str = "Select an option:",
    sub_title: str = None,
    dashboard: Callable[..., str] | None = None,
    dashboard_keys: list[str] = [],
    index: int = 0,
):
    assert all(
        key not in ("KEY_ENTER", "q", "KEY_ESCAPE", "j", "KEY_DOWN", "k", "KEY_UP")
        for key in dashboard_keys
    )

    if not dashboard:
        player = Player()
        dashboard = get_dashboard
        dashboard_keys = [key for key in player.dashboard_settings]

    def print_header(key=None):
        print(term.clear)
        if dashboard:
            if key:
                print(dashboard(key))
            else:
                print(dashboard())
            print()
        print(term.bold(message))
        if sub_title:
            print(term.snow4(sub_title))
        print()

    def print_options_and_get_hotkeys():
        hotkeys = {}
        for i, option in enumerate(options):
            # find first available hotkey character in valid parts of the option
            valid_words = "".join([word for word in option.split() if word.isalpha()])
            hotkey = next(
                (
                    char
                    for char in valid_words
                    if char.lower() in string.ascii_lowercase
                    and char.lower() not in RESERVED_HOTKEYS + list(hotkeys.keys())
                ),
                None,
            )

            # if it found one and it's not reserved, store and overwrite option with underlined
            # character valid == not an exit phrase or mine duration selection
            is_reserved_option = any(
                (phrase in option.lower() for phrase in RESERVED_EXIT_PHRASES + ("minutes",))
            )
            if hotkey and not is_reserved_option:
                hotkeys[hotkey.lower()] = i
                option = option.replace(hotkey, term.underline + hotkey + term.no_underline, 1)

            print(f"{f'{term.skyblue}>' if i == index else ' '} {option}{term.normal}")
        print(term.move_up(len(options) + 1))
        return hotkeys

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print_header()
        while True:
            hotkeys = print_options_and_get_hotkeys()
            key = term.inkey()

            # goto menu_option by index number
            if key.isdigit() and int(key) in range(min(len(options) + 1, 10)):
                index = int(key) - 1

            # goto and select menu_option by hotkey
            if key.lower() in hotkeys:
                index = hotkeys[key.lower()]
                break

            if key.name == "KEY_ENTER":
                break
            # If the last option is for going back
            elif (options[len(options) - 1].lower().strip() in RESERVED_EXIT_PHRASES) and (
                key == "q" or key.name == "KEY_ESCAPE"
            ):
                index = len(options) - 1
                break
            elif key == "j" or key.name == "KEY_DOWN":
                index += 1
                index %= len(options)
            elif key == "k" or key.name == "KEY_UP":
                index -= 1
                index %= len(options)
            elif key in dashboard_keys:
                print_header(key)

        return options[index], index


def confirm(
    message: str = "Are you sure?",
    *,
    yes: Callable | None = None,
    no: Callable | None = None,
):
    confirmed = pick(["Yes", "No"], message)[0] == "Yes"
    if confirmed and yes:
        yes()
    elif not confirmed and no:
        no()

    return confirmed
