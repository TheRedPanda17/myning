from textual.app import events
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.events import Event
from textual.reactive import Reactive
from textual.widgets import OptionList, Static

from myning.utils.ui_consts import Icons

CHAPTERS = [
    (f"{Icons.UNKNOWN} Tutorial", "Tutorial"),
    (f"{Icons.PICKAXE} Mine", "Mine"),
    (f"{Icons.STORE} Store", "Store"),
]


class ChapterWidget(ScrollableContainer):
    content = Reactive("[bold]Where would you like to go next?[/]")
    can_focus = True

    def compose(self):
        yield Static(self.content)
        option_list = OptionList(*[x[0] for x in CHAPTERS])
        option_list.can_focus = False
        yield option_list

    async def on_key(self, key: events.Key):
        option_list: OptionList = self.query_one("OptionList")
        binding = option_list._bindings.keys.get(key.name)
        if binding:
            await option_list.run_action(binding.action)

    def on_option_list_option_selected(self, option: OptionList.OptionSelected):
        print(option.option.prompt)
        print(option.option_index)
