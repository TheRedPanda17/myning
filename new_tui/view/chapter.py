from rich.text import Text
from textual.app import events
from textual.containers import ScrollableContainer
from textual.reactive import Reactive
from textual.widgets import OptionList, Static

from new_tui.chapters import PickArgs, town


class Question(Static):
    message = Reactive("")
    subtitle = Reactive("")

    def render(self):
        content = f"[bold]{self.message}[/]"
        if self.subtitle:
            content += f"\n[grey53]{self.subtitle}[/]"
        return Text.from_markup(content)


class ChapterWidget(ScrollableContainer):
    can_focus = True

    def __init__(self):
        self.question = Question()
        self.option_list = OptionList()
        self.option_list.can_focus = False
        super().__init__()

    def compose(self):
        yield self.question
        yield self.option_list

    def on_mount(self):
        self.border_title = "Town"
        self.pick(town.enter())
        # For developing, select options by 0-based index to skip to the screen
        # self.select(1)
        # self.select(0)

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
        elif _key.isdigit():
            self.option_list.highlighted = int(_key) - 1
        elif binding := self.option_list._bindings.keys.get(_key):
            await self.option_list.run_action(binding.action)
            key.stop()

    def on_option_list_option_selected(self, option: OptionList.OptionSelected):
        self.select(option.option_index)

    def pick(self, args: PickArgs):
        self.question.message = args.message
        self.question.subtitle = args.subtitle or ""
        self.option_list.clear_options()
        self.option_list.add_options([option[0] for option in args.options])
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
