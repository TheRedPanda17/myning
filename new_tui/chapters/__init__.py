from typing import Callable

Handler = tuple[str, list[tuple[str, Callable[..., "Handler"]]]]
