from textual import events
from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from myning.objects.trip import Trip
from new_tui.chapters import mine
from new_tui.chapters.mine.screen import MineScreen
from new_tui.view.army import ArmyWidget
from new_tui.view.chapter import ChapterWidget
from new_tui.view.currency import CurrencyWidget
from new_tui.view.header import Header
from new_tui.view.inventory import InventoryWidget

trip = Trip()


class SideContainer(Static):
    def compose(self):
        yield ArmyWidget()
        yield CurrencyWidget()
        yield InventoryWidget()


class Body(Static):
    def compose(self):
        yield ChapterWidget()
        yield SideContainer()


class MyningScreen(Screen):
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
            "ctrl_d": "pagedown",
            "ctrl_u": "pageup",
            "g": "home",
            "upper_g": "end",
        }
        _key = aliases.get(key.name, key.name)
        if binding := focused._bindings.keys.get(_key):  # pylint: disable=protected-access
            await focused.run_action(binding.action)


class MyningApp(App):
    CSS_PATH = [
        "app.css",
        "header.css",
    ]
    SCREENS = {"myning": MyningScreen(name="myning")}
    TITLE = "Myning"

    async def on_mount(self):
        self.push_screen("myning")
        if trip.seconds_left > 0:

            def screen_callback(abandoned: bool):
                chapter = self.query_one("ChapterWidget", ChapterWidget)
                return chapter.pick(mine.complete_trip(abandoned))

            self.push_screen(MineScreen(), screen_callback)
