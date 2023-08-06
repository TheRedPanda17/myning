import string

from rich.text import Text
from textual.app import events
from textual.containers import ScrollableContainer
from textual.reactive import Reactive
from textual.widgets import OptionList, Static

from myning.objects.player import Player
from new_tui.chapters import PickArgs, town
from new_tui.view.army import ArmyContents
from new_tui.view.currency import CurrencyWidget
from new_tui.view.inventory import InventoryContents, InventoryWidget

player = Player()


class Question(Static):
    message = Reactive("")
    subtitle = Reactive("")

    def render(self):
        content = f"[bold]{self.message}[/]"
        if self.subtitle:
            content += f"\n[grey53]{self.subtitle}[/]"
        return Text.from_markup(content)


RESERVED_HOTKEYS = {
    "d",
    "j",
    "k",
    "q",
    "u",
}


class ChapterWidget(ScrollableContainer):
    can_focus = True

    def __init__(self):
        self.question = Question()
        self.option_list = OptionList()
        self.option_list.can_focus = False
        self.handlers = []
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
        # self.select(1)

    async def on_key(self, key: events.Key):
        aliases = {
            "j": "down",
            "k": "up",
            "d": "page_down",
            "u": "page_up",
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
        self.option_list.clear_options()
        self.hotkeys = {}
        options = []
        for i, option in enumerate(args.options):
            label = option[0]
            if (
                not isinstance(label, Text)
                and i != len(args.options) - 1
                and (
                    hotkey := next(
                        (
                            char
                            for char in label
                            if char.lower() in string.ascii_lowercase
                            and char.lower() not in RESERVED_HOTKEYS | set(self.hotkeys.keys())
                        ),
                        None,
                    )
                )
            ):
                self.hotkeys[hotkey.lower()] = i
                label = label.replace(hotkey, f"[underline]{hotkey}[/]", 1)
            options.append(label)
        self.option_list.add_options(options)
        self.option_list.highlighted = 0
        self.handlers = [option[1] for option in args.options]

    def select(self, option_index: int):
        handler = self.handlers[option_index]
        module = handler.__module__.rpartition(".")[-1]
        if module != "functools":
            self.border_title = module.replace("_", " ").title()
        args = handler()
        if args.message == "__exit__":
            self.app.exit()
        self.pick(args)
