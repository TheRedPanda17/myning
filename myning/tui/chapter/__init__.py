import string

from rich.text import Text
from textual import events
from textual.containers import ScrollableContainer
from textual.widgets import DataTable

from myning.chapters import (
    DynamicArgs,
    ExitArgs,
    Handler,
    OptionLabel,
    PickArgs,
    main_menu,
    mine,
    tutorial,
)
from myning.chapters.garden.garden_table import GardenTable
from myning.chapters.mine.screen import MineScreen
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.tui.army import ArmyWidget
from myning.tui.chapter.option_table import OptionTable
from myning.tui.chapter.question import Question
from myning.tui.currency import CurrencyWidget
from myning.tui.inventory import InventoryWidget
from myning.utilities.tab_title import TabTitle
from myning.utilities.ui import Icons

player = Player()
trip = Trip()


HOTKEY_ALIASES = {
    "j": "down",
    "k": "up",
    "ctrl_d": "pagedown",
    "ctrl_u": "pageup",
}
RESERVED_HOTKEYS = {"j", "k", "q"}


class ChapterWidget(ScrollableContainer):
    can_focus = True

    def __init__(self):
        self.question = Question()
        self.option_table = OptionTable()
        self.handlers: list[Handler] = []
        self.hotkeys: dict[str, int] = {}
        super().__init__()

    def compose(self):
        yield self.question
        yield self.option_table

    def on_mount(self):
        if trip.seconds_left != 0:
            self.app.push_screen(
                MineScreen(),
                lambda abandoned: self.pick(mine.complete_trip(abandoned)),
            )
        else:
            self.update_dashboard()
            args = main_menu.enter() if tutorial.is_complete() else tutorial.enter()
            self.pick(args)

    def on_click(self):
        self.focus()

    async def on_key(self, event: events.Key):
        event.stop()
        key = HOTKEY_ALIASES.get(event.name, event.name)
        if key == "tab":
            self.app.action_focus_next()
        elif key == "shift_tab":
            self.app.action_focus_previous()
        elif key in ("escape", "q"):
            if not self.option_table.rows or self.option_table.get_row_at(
                self.option_table.row_count - 1
            ) == [Icons.EXIT, "Exit"]:
                return  # Prevent exiting with escape or q in main menu
            self.select(-1)
        elif key in self.hotkeys:
            self.select(self.hotkeys[key])
        elif key.isdigit() and key != "0":
            self.option_table.move_cursor(row=int(key) - 1)
        elif key in ("upper_h", "ctrl_b"):
            self.option_table.scroll_page_left()
        elif key in ("upper_l", "ctrl_f"):
            self.option_table.scroll_page_right()
        elif garden_query := self.query("GardenTable"):
            garden_table = garden_query.first(GardenTable)
            await garden_table.handle_chapter_key(key)
        elif binding := self.option_table._bindings.keys.get(  # pylint: disable=protected-access
            key
        ):
            await self.option_table.run_action(binding.action)

    def on_data_table_row_selected(self, row: DataTable.RowSelected):
        self.select(row.cursor_row)

    def update_dashboard(self):
        if self.app.query("SideBar"):
            self.app.query_one("ArmyWidget", ArmyWidget).update()
            self.app.query_one("CurrencyWidget", CurrencyWidget).refresh()
            self.app.query_one("InventoryWidget", InventoryWidget).update()

    def pick(self, args: PickArgs):
        self.update_dashboard()
        if title := args.border_title:
            self.border_title = title
            TabTitle.change_tab_status(title)
        self.question.message = args.message
        self.question.subtitle = args.subtitle or ""
        labels = [o[0] for o in args.options]
        handlers = [o[1] for o in args.options]
        if self.query("GardenTable"):
            HOTKEY_ALIASES["h"] = "left"
            HOTKEY_ALIASES["l"] = "right"
            RESERVED_HOTKEYS.add("h")
            RESERVED_HOTKEYS.add("l")
        else:
            if "h" in RESERVED_HOTKEYS:
                del HOTKEY_ALIASES["h"]
                RESERVED_HOTKEYS.remove("h")
            if "l" in RESERVED_HOTKEYS:
                del HOTKEY_ALIASES["l"]
                RESERVED_HOTKEYS.remove("l")
        options, hotkeys = get_labels_and_hotkeys(labels)
        self.option_table.clear(columns=True)
        if options:
            column_count = max(len(option) for option in options)
            if args.column_titles:
                self.option_table.show_header = True
                while len(args.column_titles) < column_count:
                    args.column_titles.append("")
                self.option_table.add_columns(*args.column_titles)
            else:
                self.option_table.show_header = False
                self.option_table.add_columns(*(str(i) for i in range(column_count)))
            self.option_table.add_rows(options)
        self.hotkeys = hotkeys
        self.handlers = handlers

    def select(self, option_index: int):
        if not self.handlers:
            return
        handler = self.handlers[option_index]
        args = handler()
        if isinstance(args, ExitArgs):
            self.app.exit()
        elif isinstance(args, DynamicArgs):
            args.callback(self)
        else:
            if (module := handler.__module__.rpartition(".")[-1]) not in (
                "functools",
                "pick",
            ) and "base" not in module:
                title = module.replace("_", " ").title()
                self.border_title = title
                TabTitle.change_tab_status(title)
            self.pick(args)

    def clear(self):
        self.pick(PickArgs(message="", options=[]))


def get_labels_and_hotkeys(options: list[OptionLabel]):
    hotkeys: dict[str, int] = {}
    labels: list[list[str | Text]] = []
    options = [option if isinstance(option, list) else [option] for option in options]
    for option_index, option_arr in enumerate(options):
        if not isinstance(option_arr, list):
            option_arr = [option_arr]

        if option_index == len(options) - 1:  # No hotkey for last option
            labels.append(option_arr)
            continue

        text_option_index = None
        text_option = None
        for index, item in enumerate(option_arr):
            if isinstance(item, str) and any(c in string.ascii_letters for c in item):
                text_option = Text.from_markup(item)
                text_option_index = index
                break
            if isinstance(item, Text):
                text_option = item
                text_option_index = index
                break

        if text_option and text_option_index is not None:
            hotkey, hotkey_index = get_hotkey(text_option.plain, hotkeys)
            if hotkey and hotkey_index is not None:
                hotkeys[hotkey] = option_index
                text_option.stylize("underline", hotkey_index, hotkey_index + 1)
                option_arr[text_option_index] = text_option

        labels.append(option_arr)
    return labels, hotkeys


def get_hotkey(label: str, hotkeys: dict[str, int]):
    for hotkey_index, char in enumerate(label):
        hotkey = char.lower()
        if (
            "minutes" not in label
            and hotkey in string.ascii_lowercase
            and hotkey not in RESERVED_HOTKEYS | set(hotkeys)
        ):
            return hotkey, hotkey_index
    return None, None
