from textual.coordinate import Coordinate
from textual.widgets import DataTable


class OptionTable(DataTable):
    def __init__(self):
        super().__init__()
        self.can_focus = False
        self.cursor_foreground_priority = "renderable"
        self.cursor_type = "row"
        self.show_header = False

    # https://github.com/Textualize/textual/pull/3093
    def action_page_down(self) -> None:
        """Move the cursor one page down."""
        self._set_hover_cursor(False)
        cursor_type = self.cursor_type
        if self.show_cursor and cursor_type in ("cell", "row"):
            height = self.size.height - (self.header_height if self.show_header else 0)

            # Determine how many rows constitutes a "page"
            offset = 0
            rows_to_scroll = 0
            row_index, column_index = self.cursor_coordinate
            for ordered_row in self.ordered_rows[row_index:]:
                offset += ordered_row.height
                if offset > height:
                    break
                rows_to_scroll += 1

            self.cursor_coordinate = Coordinate(row_index + rows_to_scroll - 1, column_index)
        else:
            super().action_page_down()

    # https://github.com/Textualize/textual/pull/3093
    def action_page_up(self) -> None:
        """Move the cursor one page up."""
        self._set_hover_cursor(False)
        cursor_type = self.cursor_type
        if self.show_cursor and cursor_type in ("cell", "row"):
            height = self.size.height - (self.header_height if self.show_header else 0)

            # Determine how many rows constitutes a "page"
            offset = 0
            rows_to_scroll = 0
            row_index, column_index = self.cursor_coordinate
            for ordered_row in self.ordered_rows[: row_index + 1]:
                offset += ordered_row.height
                if offset > height:
                    break
                rows_to_scroll += 1

            self.cursor_coordinate = Coordinate(row_index - rows_to_scroll + 1, column_index)
        else:
            super().action_page_up()

    # Override to allow circular wraparound
    def action_cursor_up(self):
        self._set_hover_cursor(False)
        if self.cursor_row > 0:
            super().action_cursor_up()
        else:
            self.move_cursor(row=self.row_count - 1)

    # Override to allow circular wraparound
    def action_cursor_down(self):
        self._set_hover_cursor(False)
        if self.cursor_row < self.row_count - 1:
            super().action_cursor_down()
        else:
            self.move_cursor(row=0)

    # Override to allow circular wraparound
    def action_cursor_left(self):
        self._set_hover_cursor(False)
        if self.cursor_column > 0:
            super().action_cursor_left()
        else:
            self.move_cursor(column=len(self.columns) - 1)

    # Override to allow circular wraparound
    def action_cursor_right(self):
        self._set_hover_cursor(False)
        if self.cursor_column < len(self.columns) - 1:
            super().action_cursor_right()
        else:
            self.move_cursor(column=0)
