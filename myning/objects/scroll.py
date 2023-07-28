from time import sleep
from typing import List

from blessed import Terminal
from grapheme import length

term = Terminal()

# region: Borders
TOP_LEFT = [" .-._", "((0))", " '-'_"]
TOP_EXTENDER = ["_", " ", "_"]
TOP_RIGHT = [".-. ", "   )", "__/ "]
LEFT = "   ⌇"
RIGHT = "⌇   "
BOT_LEFT = [" .-._", "((0))", " '-'_"]
BOT_EXTENDER = ["_", " ", "_"]
BOT_RIGHT = [".-. ", "   )", "__/ "]
# endregion
# Terminal Window Spacing (Top and Left)
LEFT_SPACING = 2
TOP_SPACING = 1


class Scroll:
    def __init__(self, height: int = 16, width: int = 34, padding: int = 2):
        self.height = height
        self.width = width
        self.padding = padding
        self.lines = []
        self.window_start_index = 0

    def scroll_up(self):
        if self.window_start_index > 0:
            self.window_start_index -= 1

    def scroll_down(self):
        if len(self.lines) - self.height > self.window_start_index:
            self.window_start_index += 1

    def __str__(self):
        top = self.__build_header_footer(TOP_LEFT, TOP_EXTENDER, TOP_RIGHT)
        body = self.__build_body(LEFT, RIGHT)
        bot = self.__build_header_footer(BOT_LEFT, BOT_EXTENDER, BOT_RIGHT)
        return term.move_down(TOP_SPACING) + top + body + bot

    def animate(self, duration: float = 1.5):
        """
        Animate opening the scroll.
        Duration in seconds
        """
        original_height = self.height
        if original_height == 0:
            tick = 0
        else:
            tick = duration / (original_height + 1)

        with term.fullscreen(), term.hidden_cursor():
            for i in range(0, original_height + 1):
                self.height = i
                print(term.clear)
                print(self.__str__())
                sleep(tick)

    def __build_header_footer(self, left: List[str], extender: List[str], right: List[str]):
        s = ""
        for col_index, segment in enumerate(left):
            s += term.move_right(LEFT_SPACING) + segment
            s += extender[col_index] * self.width
            s += right[col_index]
            s += "\n"
        return s

    def __build_body(self, left: str, right: str):
        s = ""
        for i in range(0, self.height):
            s += term.move_right(LEFT_SPACING) + left
            if i + self.window_start_index < len(self.lines):
                line = self.lines[i + self.window_start_index]
            else:
                line = " " * (self.width - self.padding * 2)

            padding = " " * self.padding
            line = f"{padding}{line}{padding}"
            s += line
            s += right + "\n"
        return s

    def build_title(self, text: str):
        """
        Center Align. Add spacing before and after.
        """
        min_title_padding = 2
        line_limit = self.width - (self.padding * 2) - (min_title_padding * 2)
        blank_line = " " * (self.width - self.padding * 2)

        lines_wrapped = term.wrap(text, width=line_limit)
        lines_centered = [
            term.bold(self.__center_line(line, line_limit + (min_title_padding * 2)))
            for line in lines_wrapped
        ]
        lines = [blank_line] + lines_centered + [blank_line]

        self.lines += lines

    def build_heading(self, text: str):
        """
        Left Align. Add spacing before.
        """
        line_limit = self.width - (self.padding * 2)

        # Add spacing before
        spacing_before = " " * line_limit
        lines = [spacing_before]

        lines += term.wrap(
            term.bold(text),
            width=line_limit,
        )

        self.lines += self.__trailing_spaces(lines, line_limit)

    def build_indented_paragraph(self, text: str):
        """
        Indented. No spacing.
        """
        indent = 2
        line_limit = self.width - (self.padding * 2)
        lines = term.wrap(
            text, width=line_limit, initial_indent=" " * indent, subsequent_indent=" " * indent
        )

        self.lines += self.__trailing_spaces(lines, line_limit)

    def build_paragraph(self, text: str):
        """
        Left Align. No spacing before or after.
        """
        line_limit = self.width - (self.padding * 2)
        lines = term.wrap(text, width=line_limit)

        self.lines += self.__trailing_spaces(lines, line_limit)

    @staticmethod
    def __center_line(line: str, limit: int):
        """
        Pad the line with spaces (to essentially center the text).
        """
        if length(line) < limit:
            count = limit - length(line) - 1
            for i in range(0, count):
                # Pad right out first just as preference in case odd number
                if i % 2 == 0:
                    line = line + " "
                else:
                    line = " " + line
        return line

    @staticmethod
    def __trailing_spaces(lines: List[str], limit: int):
        """
        Add remaining white spaces to the end of line
        """
        return [f"{line}{' ' * (limit - term.length(line))}" for line in lines]
