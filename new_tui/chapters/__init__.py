from dataclasses import dataclass
from typing import Callable, Optional

from rich.text import Text


@dataclass
class PickArgs:
    message: str
    options: list["Option"]
    subtitle: Optional[str] = None


Handler = Callable[..., PickArgs]
Option = tuple[str | Text, Handler]
