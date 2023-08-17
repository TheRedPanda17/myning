import inspect
import re
import time
from functools import partial
from typing import Callable

from new_tui.chapters import Handler, PickArgs, PickHandler, StoryArgs


def throttle(interval: float):
    def outer(func):
        last_called_time = 0

        def inner(*args, **kwargs):
            nonlocal last_called_time
            current_time = time.time()
            if current_time - last_called_time >= interval:
                func(*args, **kwargs)
                last_called_time = current_time

        return inner

    return outer


def confirm(
    message: str | Callable[..., str],
    no: PickHandler,
    validator: Callable[..., PickArgs | None] | None = None,
):
    """
    Wrap a Handler with a Yes/No confirmation.

    Parameters:
    message: The message to show in the confirmation pick. Can be a string or a callable that takes
    the same arguments as the wrapped function and returns a string.
    no: The callback for choosing no.
    validator: Optional validator to run before the function. Should return PickArgs if validation
    fails, otherwise None.

    Example
    ```python
    @confirm(f"Are you sure you want to buy {{0.name}}?", choose_action)
    def buy(item):
        player.inventory.add_item(item, /)
        return choose_action()
    ```
    """

    def decorator(func: Handler):
        f_sig = inspect.signature(func)
        f_name = f"{func.__module__}.{func.__name__}"
        if callable(message):
            message_sig = inspect.signature(message)
            if (
                len(message_sig.parameters) != len(f_sig.parameters)
                or message_sig.parameters.keys() != f_sig.parameters.keys()
            ):
                raise RuntimeError(
                    f"{f_name} uses the `confirm` decorator and has a callable message but the "
                    f"signature of the message and {f_name} do not match."
                )
        else:
            has_format_placeholders = re.search(r"\{.*?\}", message)
            has_ambiguous_params = any(
                param.kind
                not in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.KEYWORD_ONLY)
                for param in f_sig.parameters.values()
            )
            if has_format_placeholders and has_ambiguous_params:
                raise RuntimeError(
                    f"{f_name} uses the `confirm` decorator and has a format placeholder in the "
                    "message, so it must only use positional-only or keyword-only parameters."
                )
            for idx, (param_name, param) in enumerate(f_sig.parameters.items()):
                if int(param.kind) == inspect.Parameter.POSITIONAL_ONLY and (
                    matches := re.search(rf"{{{param_name}.*?}}", message)
                ):
                    raise RuntimeError(
                        f"{f_name} uses the `confirm` decorator and has a positional-only argument "
                        f"{param_name} included in the message as a keyword-formatted argument "
                        f"(like {{{matches[0]}}}) but it needs to be included as a "
                        f"positionally-formatted argument (like {{{{{idx}}}}})."
                    )

        def pick_confirm(*args, **kwargs):
            if validator and (validator_pick_args := validator(*args, **kwargs)):
                return validator_pick_args

            yes_callback = partial(func, *args, **kwargs)
            no_callback = partial(no, args[0]) if f_sig.parameters.get("self") else no

            return PickArgs(
                message=message(*args, **kwargs)
                if callable(message)
                else message.format(*args, **kwargs),
                options=[
                    ("Yes", yes_callback),
                    ("No", no_callback),
                ],
            )

        return pick_confirm

    return decorator


def story_builder(story_args_list: list[StoryArgs], final_handler: PickHandler):
    """
    Given a list of `StoryArgs`, build the chain of `PickArgs` backwards to present a series of
    single-option prompts.
    """

    next_handler = final_handler
    for story in reversed(story_args_list):
        next_handler = _story_to_pick_handler(story, next_handler)
    return next_handler()


def _story_to_pick_handler(story: StoryArgs, handler: PickHandler):
    return lambda: PickArgs(
        message=story.message,
        options=[(story.response, handler)],
        subtitle=story.subtitle,
    )
