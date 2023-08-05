from textual.app import App, events
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from new_tui.view.army import ArmyWidget
from new_tui.view.chapter import ChapterWidget
from new_tui.view.currency import CurrencyWidget
from new_tui.view.header import Header
from new_tui.view.inventory import InventoryWidget


class SideContainer(Static):
    def compose(self):
        yield ArmyWidget()
        yield CurrencyWidget()
        yield InventoryWidget()


class Body(Static):
    def compose(self):
        yield ChapterWidget()
        yield SideContainer()


class MyningGame(Screen):
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("tab", "focus_next", "Focus Next"),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
    ]

    def compose(self):
        yield Header()
        yield Body()
        yield Footer()

    async def on_key(self, key: events.Key):
        focused = self.focused
        if not focused:
            return
        aliases = {
            "h": "left",
            "j": "down",
            "k": "up",
            "l": "right",
            "d": "pagedown",
            "u": "pageup",
            "g": "home",
            "upper_g": "end",
        }
        _key = aliases.get(key.name, key.name)
        if binding := focused._bindings.keys.get(_key):
            await focused.run_action(binding.action)


class MyningApp(App):
    CSS_PATH = [
        "app.css",
        "header.css",
    ]
    TITLE = "Myning"

    def on_mount(self):
        self.push_screen(MyningGame())
