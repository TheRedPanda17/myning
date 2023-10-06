from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Coroutine, Optional
import aiohttp

from rich.console import RenderableType
from rich.text import Text
from textual.widgets import ProgressBar

if TYPE_CHECKING:
    from myning.tui.chapter import ChapterWidget


@dataclass
class PickArgs:
    message: RenderableType
    options: list["Option"]
    subtitle: Optional[RenderableType] = None
    border_title: Optional[str] = None
    column_titles: Optional[list[str | Text]] = None


@dataclass
class DynamicArgs:
    callback: Callable[["ChapterWidget"], None]


@dataclass
class AsyncArgs:
    callback: Callable[["ChapterWidget"], Coroutine]


@dataclass
class ExitArgs:
    pass


PickHandler = Callable[..., PickArgs]
Handler = Callable[..., PickArgs | DynamicArgs | AsyncArgs | ExitArgs]
OptionLabel = str | Text | list[str | Text]


@dataclass
class Option:
    label: OptionLabel
    handler: Handler
    enable_hotkeys: bool = True
    """
    Will be overridden to False for the last Option in a list (assumes back button or continue)
    """


@dataclass
class StoryArgs:
    message: str
    response: str = "Okay"
    subtitle: Optional[RenderableType] = None
    border_title: Optional[str] = None


def api_request(loading_message: str, callback):
    def outer(func):
        async def inner(chapter: "ChapterWidget", *args, **kwargs):
            chapter.clear()
            chapter.question.message = loading_message
            progress = ProgressBar(show_percentage=False, show_eta=False)
            chapter.mount(progress, after=0)
            try:
                await func(chapter, *args, **kwargs)
            except aiohttp.ClientError as e:
                status = getattr(e, "status", "Unknown Error")
                message = f"Error contacting the API: {status}"
                if status == 401:
                    message += " you've been logged out, or your password has changed"
                chapter.pick(
                    PickArgs(
                        message=message,
                        options=[Option("Bummer!", callback)],
                    )
                )
            finally:
                progress.remove()

        return inner

    return outer
