from typing import Callable

from rich.text import Text
from textual.app import events
from textual.containers import ScrollableContainer
from textual.reactive import Reactive
from textual.widgets import OptionList, Static

from new_tui.chapters import Handler, town


class Question(Static):
    message = Reactive("")

    def render(self):
        return Text.from_markup(self.message)


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
        message, options = town.enter()
        self.pick(message, options)

    async def on_key(self, key: events.Key):
        aliases = {
            "j": "down",
            "k": "up",
        }
        _key = aliases.get(key.name, key.name)

        if _key == "q":
            self.select(-1)
        elif _key.isdigit():
            self.option_list.highlighted = int(_key) - 1
        elif binding := self.option_list._bindings.keys.get(_key):
            await self.option_list.run_action(binding.action)
            key.stop()

    def on_option_list_option_selected(self, option: OptionList.OptionSelected):
        self.select(option.option_index)

    def pick(self, message: str, options: list[tuple[str, Callable[..., Handler]]]):
        self.question.message = message
        self.option_list.clear_options()
        self.option_list.add_options([option[0] for option in options])
        self.option_list.highlighted = 0
        self.handlers = [option[1] for option in options]

    def select(self, option_index: int):
        handler = self.handlers[option_index]
        module = handler.__module__.rpartition(".")[-1]
        if module != "functools":
            self.border_title = module.replace("_", " ").title()
        message, options = handler()
        self.pick(message, options)
