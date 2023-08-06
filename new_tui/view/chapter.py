import string

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.app import events
from textual.containers import ScrollableContainer
from textual.reactive import Reactive
from textual.widgets import OptionList, Static

from myning.objects.player import Player
from new_tui.chapters import Handler, PickArgs, town
from new_tui.formatter import Colors
from new_tui.view.army import ArmyContents
from new_tui.view.currency import CurrencyWidget
from new_tui.view.inventory import InventoryContents, InventoryWidget

player = Player()


class Question(Static):
    message = Reactive("")
    subtitle: Reactive[str | RenderableType] = Reactive("")

    def render(self):
        table = Table.grid()
        table.add_row(f"[bold]{self.message}[/]")
        if self.subtitle:
            if isinstance(self.subtitle, str):
                self.subtitle = f"[{Colors.LOCKED}]{self.subtitle}[/]"
            table.add_row(self.subtitle)
        return table


RESERVED_HOTKEYS = {"j", "k", "q"}


class ChapterWidget(ScrollableContainer):
    can_focus = True

    def __init__(self):
        self.question = Question()
        self.option_list = OptionList(wrap=False)
        self.option_list.can_focus = False
        self.handlers: list[Handler] = []
        self.hotkeys: dict[str, int] = {}
        super().__init__()

    def compose(self):
        yield self.question
        yield self.option_list

    def on_mount(self):
        self.update_dashboard()
        self.border_title = "Town"
        self.pick(town.enter())
        # For dev, select options by 0-based index to skip to the screen
        self.select(0)
        self.select(-3)

    async def on_key(self, key: events.Key):
        aliases = {
            "j": "down",
            "k": "up",
        }
        _key = aliases.get(key.name, key.name)

        if _key == "q":
            if self.question.message == town.enter().message:
                return  # Prevent exiting with q in main menu
            self.select(-1)
        elif _key in self.hotkeys:
            self.select(self.hotkeys[_key])
        elif _key.isdigit():
            self.option_list.highlighted = int(_key) - 1
        elif binding := self.option_list._bindings.keys.get(_key):
            await self.option_list.run_action(binding.action)

    def on_option_list_option_selected(self, option: OptionList.OptionSelected):
        self.select(option.option_index)
        self.update_dashboard()

    def update_dashboard(self):
        self.app.query_one("ArmyContents", ArmyContents).update_army()
        self.app.query_one("CurrencyWidget", CurrencyWidget).refresh()
        self.app.query_one("InventoryContents", InventoryContents).update_inventory()
        self.app.query_one("InventoryWidget", InventoryWidget).update_border()

    def pick(self, args: PickArgs):
        self.question.message = args.message
        self.question.subtitle = args.subtitle or ""
        labels, handlers = zip(*args.options)
        options, hotkeys = get_labels_and_hotkeys(labels)
        self.option_list.clear_options()
        self.option_list.add_options(options)
        self.option_list.highlighted = 0
        self.hotkeys = hotkeys
        self.handlers = handlers

    def select(self, option_index: int):
        handler = self.handlers[option_index]
        module = handler.__module__.rpartition(".")[-1]
        if module != "functools":
            self.border_title = module.replace("_", " ").title()
        args = handler()
        if args.message == "__exit__":
            self.app.exit()
            return
        self.pick(args)


def get_labels_and_hotkeys(options: list[str]):
    hotkeys: dict[str, int] = {}
    labels: list[str] = []
    for i, option in enumerate(options):
        if isinstance(option, Text):
            label = option.plain
        elif isinstance(option, Table):
            cell: Text = option.columns[0]._cells[0]
            label = cell.plain
        else:
            label = option

        for hotkey_index, char in enumerate(label):
            hotkey = char.lower()
            if (
                i != len(options) - 1
                and "minutes" not in label
                and hotkey in string.ascii_lowercase
                and hotkey not in RESERVED_HOTKEYS | set(hotkeys.keys())
            ):
                hotkeys[hotkey] = i
                if isinstance(option, Text):
                    option.stylize("underline", hotkey_index, hotkey_index + 1)
                elif isinstance(option, Table):
                    cell: Text = option.columns[0]._cells[0]
                    cell.stylize("underline", hotkey_index, hotkey_index + 1)
                else:
                    option = label.replace(char, f"[underline]{char}[/]", 1)
                break
        labels.append(option)
    return labels, hotkeys
