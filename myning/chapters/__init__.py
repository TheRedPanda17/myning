from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Coroutine, Optional

from rich.console import RenderableType
from rich.text import Text

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
    enable_hotkeys: bool = False

    def label_as_list(self) -> list[str | Text]:
        if not isinstance(self.label, list):
            return [self.label]
        return self.label


@dataclass
class StoryArgs:
    message: str
    response: str = "Okay"
    subtitle: Optional[RenderableType] = None
    border_title: Optional[str] = None
