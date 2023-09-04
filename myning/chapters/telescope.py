from typing import TYPE_CHECKING

from chafa import Canvas, CanvasConfig, PixelType
from PIL import Image
from rich.text import Text
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
        options=[Option("Look through Telescope...", lambda: DynamicArgs(callback=view))],
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
        config = CanvasConfig()
        image = Image.open("./images/space.jpeg")
        config.width = self.parent.container_size.width - 1
        config.height = self.parent.container_size.height - 4
        config.calc_canvas_geometry(image.width, image.height, 11 / 24)
        bands = len(image.getbands())
        pixels = image.tobytes()
        canvas = Canvas(config)
        canvas.draw_all_pixels(
            PixelType.CHAFA_PIXEL_RGB8,
            pixels,  # type: ignore
            image.width,
            image.height,
            image.width * bands,
        )
        output = canvas.print()
        return Text.from_ansi(output.decode())
