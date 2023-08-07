from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional
from rich.console import RenderableType

from rich.text import Text
from rich.table import Table

if TYPE_CHECKING:
    from new_tui.view.chapter import ChapterWidget


@dataclass
class PickArgs:
    message: str
    options: list["Option"]
    subtitle: Optional[RenderableType] = None


@dataclass
class DynamicArgs:
    callback: Callable[["ChapterWidget"], None]


@dataclass
class ExitArgs:
    pass


Handler = Callable[..., PickArgs | DynamicArgs | ExitArgs]
Option = tuple[str | Text | Table, Handler]
