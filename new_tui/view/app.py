from textual import events
from textual.app import App
from textual.binding import Binding
from textual.reactive import Reactive
from textual.widget import Widget
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


class MyningApp(App):
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("tab", "focus_next", "Focus Next"),
        Binding("shift+tab", "focus_previous", "Focus Previous"),
    ]
    CSS_PATH = [
        "app.css",
        "header.css",
    ]
    TITLE = "Myning"

    def compose(self):
        yield Header()
        yield Body()
        yield Footer()

    def action_test(self):
        print("")
