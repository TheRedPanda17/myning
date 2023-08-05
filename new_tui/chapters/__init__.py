from dataclasses import dataclass
from functools import partial
from typing import Callable, Optional


@dataclass
class PickArgs:
    message: str
    options: list["Option"]
    subtitle: Optional[str] = None


Handler = Callable[..., PickArgs]
Option = tuple[str, Handler]
