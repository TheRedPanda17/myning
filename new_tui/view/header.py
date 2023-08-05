from datetime import datetime

from textual.widgets import Static


class HeaderClock(Static):
    def render(self):
        return datetime.now().strftime("%X")

    def on_mount(self, _) -> None:
        self.set_interval(0.01, callback=self.refresh)


class Header(Static):
    DEFAULT_CLASSES = "container"

    def compose(self):
        yield Static("💎", id="header-icon")
        yield Static("Myning", id="header-title", classes="text-title")
        yield HeaderClock()
