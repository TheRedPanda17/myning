from typing import TYPE_CHECKING

from rich.text import Text
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from myning.objects.garden import Garden
from myning.tui.chapter.option_table import OptionTable

if TYPE_CHECKING:
    from myning.tui.chapter import ChapterWidget

garden = Garden()


class GardenTable(OptionTable):  # pylint: disable=too-many-ancestors
    def __init__(self):
        super().__init__()
        self.parent: ChapterWidget | None
        self.cursor_type = "cell"

    def on_mount(self):
        for i in range(garden.level):
            self.add_column(str(i))
        self.update()
        self.set_interval(1, self.update)

    def on_resize(self):
        self.styles.height = garden.level + self.scrollbar_size_horizontal + 2  # 2 for borders
        if self.parent:
            self.styles.max_height = (
                self.parent.container_size.height
                - self.parent.question.container_size.height
                - self.parent.option_table.row_count
                - self.scrollbar_size_horizontal
                - 3  # offset for margins and spacing
            )

    def on_data_table_cell_selected(self, event: DataTable.CellSelected):
        event.stop()
        if not self.parent:
            return

        # pylint: disable=import-outside-toplevel
        from myning.chapters.garden.manage import manage_plant

        self.parent.option_table.show_cursor = True
        self.parent.pick(manage_plant(event.coordinate.row, event.coordinate.column))
        self.remove()

    def update(self):
        if not self.row_count:
            self.add_rows(
                [
                    [
                        Text.from_markup(plant.growth_icon, justify="center") if plant else "  "
                        for plant in row
                    ]
                    for row in garden.rows
                ]
            )
        else:
            for i, row in enumerate(garden.rows):
                for j, plant in enumerate(row):
                    self.update_cell_at(
                        Coordinate(i, j),
                        Text.from_markup(plant.growth_icon, justify="center") if plant else "  ",
                    )

    async def handle_chapter_key(self, key: str):
        if not self.parent:
            return
        option_table = self.parent.option_table
        active, inactive = (self, option_table) if self.show_cursor else (option_table, self)
        if key == "up" and active.cursor_row == 0:
            active.show_cursor, inactive.show_cursor = inactive.show_cursor, active.show_cursor
            inactive.move_cursor(row=inactive.row_count - 1)
        elif key == "down" and active.cursor_row == active.row_count - 1:
            active.show_cursor, inactive.show_cursor = inactive.show_cursor, active.show_cursor
            inactive.move_cursor(row=0)
        elif binding := active._bindings.keys.get(key):  # pylint: disable=protected-access
            await active.run_action(binding.action)
