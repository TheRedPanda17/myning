from rich.table import Table
from textual import events
from textual.app import App
from textual.binding import Binding
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Static

from myning.view.army import ArmyWidget
from myning.view.chapter import ChapterWidget
from myning.view.currency import CurrencyWidget
from myning.view.header import Header
from myning.view.inventory import InventoryWidget


class SideBar(Static):
    def compose(self):
        yield ArmyWidget()
        yield CurrencyWidget()
        yield InventoryWidget()


class Body(Static):
    def compose(self):
        yield ChapterWidget()
        yield SideBar()


class MyningScreen(Screen):
    BINDINGS = [
        Binding("f1", "help", "Help", priority=True),
        Binding("f2", "toggle_sidebar", "Toggle Sidebar", priority=True),
    ]

    def compose(self):
        yield Header()
        yield Body()
        yield Footer()

    async def on_key(self, event: events.Key):
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
        key = aliases.get(event.name)
        if key and (binding := focused._bindings.keys.get(key)):  # pylint: disable=protected-access
            await focused.run_action(binding.action)

    async def action_toggle_sidebar(self):
        if sidebar := self.query("SideBar"):
            sidebar.remove()
        else:
            await self.query_one("Body", Body).mount(SideBar())
            self.query_one("ChapterWidget", ChapterWidget).update_dashboard()

    def action_help(self) -> None:
        """Action to display the help dialog."""
        self.app.push_screen(HelpScreen())


class HelpScreen(ModalScreen):
    def compose(self):
        table = Table.grid(padding=(0, 2))
        table.add_row("[bold dodger_blue1]Keyboard Shortcuts[/]")
        table.add_row("\n[bold dodger_blue1]Movement[/]")
        table.add_row("↑ or k", "Up")
        table.add_row("↓ or j", "Down")
        table.add_row("← or h", "Left")
        table.add_row("→ or l", "Right")
        table.add_row("Page up   (fn ↑) or Ctrl+u", "Scroll up")
        table.add_row("Page down (fn ↓) or Ctrl+d", "Scroll down")
        table.add_row("Shift+h          or Ctrl+b", "Scroll left")
        table.add_row("Shift+l          or Ctrl+f", "Scroll right")
        table.add_row("Home      (fn ←) or g", "Go to top")
        table.add_row("End       (fn →) or G", "Go to bottom")
        table.add_row("\n[bold dodger_blue1]Focus[/]")
        table.add_row("Tab", "Focus next")
        table.add_row("Shift+Tab", "Focus previous")
        table.add_row("\n[bold dodger_blue1]Selection[/]")
        table.add_row("Enter", "Select highlighted option")
        table.add_row("Escape or q", "Go back (selects last option)")
        table.add_row("Numbers 1-9", "Highlight option #")
        table.add_row("Underlined hotkeys", "Select hotkey option")
        table.add_row("\n[bold dodger_blue1]Press any key to close[/]")
        yield Static(table)

    def on_click(self):
        self.dismiss()

    def on_key(self):
        if self.app.screen is self:  # Prevent crash from holding F1
            self.dismiss()


class MyningApp(App):
    BINDINGS = [Binding("ctrl+c", "quit", "Quit", priority=True)]
    CSS_PATH = [
        "app.css",
        "header.css",
    ]
    TITLE = "Myning"

    def on_mount(self):
        self.push_screen(MyningScreen())
