from typing import TYPE_CHECKING

from rich_pixels import Pixels
from textual.widget import Widget
from textual.widgets import Static

from myning.chapters import DynamicArgs, Option, PickArgs, main_menu
from myning.utilities.ui import Icons

if TYPE_CHECKING:
    from myning.tui.chapter import ChapterWidget


def enter():
    return PickArgs(
        # pylint: disable=line-too-long
        message=f"As you arrive at the center of the {Icons.MINERAL} Meteor Crater, you notice a lot of rubble and what appears to be space wreckage in the area.",
        options=[Option("Investigate...", investigate)],
    )


def investigate():
    return PickArgs(
        # pylint: disable=line-too-long
        message=f"You're not sure what to make of the pieces lying around just yet, but you find a {Icons.TELESCOPE} telescope!",
        options=[Option("Look Through Telescope...", lambda: DynamicArgs(callback=view))],
    )


def view(chapter: "ChapterWidget"):
    chapter.mount(Telescope(), after=0)
    chapter.pick(
        PickArgs(
            message="You look through the telescope and wonder: what could the future hold...?",
            options=[Option("Go Back", lambda: DynamicArgs(callback=go_back))],
        )
    )


def go_back(chapter: "ChapterWidget"):
    chapter.query_one("Telescope").remove()
    chapter.pick(main_menu.enter())


class Telescope(Static):
    def render(self):
        if not isinstance(self.parent, Widget):
            return None
        aspect_ratio = 300 / 168
        max_width = self.parent.container_size.width // 2  # each pixel is 2 characters wide
        max_height = self.parent.container_size.height - 4  # leave room for question and option
        if (width := int(max_height * aspect_ratio)) < max_width:
            height = max_height
        else:
            width, height = max_width, int(max_width / aspect_ratio)
        return Pixels.from_image_path("images/space.jpeg", resize=(width, height))
