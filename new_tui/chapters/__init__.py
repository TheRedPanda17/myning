from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional, TypeVar

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from new_tui.view.chapter import ChapterWidget


@dataclass
class PickArgs:
    message: str
    options: list["Option"]
    subtitle: Optional[RenderableType] = None
    border_title: Optional[str] = None


@dataclass
class DynamicArgs:
    callback: Callable[["ChapterWidget"], None]


@dataclass
class ExitArgs:
    pass


PickHandler = Callable[..., PickArgs]
Handler = Callable[..., PickArgs | DynamicArgs | ExitArgs]
Option = tuple[str | Text | Table, Handler]


@dataclass
class StoryArgs:
    message: str
    response: str = "Okay"
    subtitle: Optional[RenderableType] = None
