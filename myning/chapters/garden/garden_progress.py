from textual.containers import Container
from textual.widgets import ProgressBar, Static

from myning.objects.garden import Garden
from myning.utilities.ui import get_time_str

garden = Garden()


class GardenProgress(Container):
    def __init__(self) -> None:
        super().__init__()
        self.progress_bar = ProgressBar(
            show_eta=False,
            total=sum(plant.total_time for row in garden.rows for plant in row if plant),
        )
        self.time_left = Static()

    def compose(self):
        yield Static("Overall Growth")
        yield self.progress_bar
        yield Static("Time Left")
        yield self.time_left

    def on_mount(self):
        self.tick()
        self.set_interval(1, self.tick)

    def tick(self):
        self.progress_bar.progress = sum(
            min(plant.elapsed_time, plant.total_time)
            for row in garden.rows
            for plant in row
            if plant
        )
        remaining = max(plant.time_left for row in garden.rows for plant in row if plant)
        self.time_left.update(get_time_str(int(remaining)))
