from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

from rich.console import RenderableType
from rich.text import Text

if TYPE_CHECKING:
    from new_tui.view.chapter import ChapterWidget


@dataclass
class PickArgs:
    message: str
    options: list["Option"]
    subtitle: Optional[RenderableType] = None
    border_title: Optional[str] = None
    column_titles: Optional[list[str | Text]] = None


@dataclass
class DynamicArgs:
    callback: Callable[["ChapterWidget"], None]


@dataclass
class ExitArgs:
    pass


PickHandler = Callable[..., PickArgs]
Handler = Callable[..., PickArgs | DynamicArgs | ExitArgs]
OptionLabel = str | Text | list[str | Text]
Option = tuple[OptionLabel, Handler]


@dataclass
class StoryArgs:
    message: str
    response: str = "Okay"
    subtitle: Optional[RenderableType] = None
