import time

from new_tui.chapters import PickArgs, PickHandler, StoryArgs


def throttle(interval):
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


def _story_to_pick_handler(story: StoryArgs, handler: PickHandler):
    return lambda: PickArgs(
        message=story.message,
        options=[(story.response, handler)],
        subtitle=story.subtitle,
    )


def story_builder(story_args_list: list[StoryArgs], final_handler: PickHandler):
    """
    Given a list of `StoryArgs`, build the chain of `PickArgs` backwards to present a series of
    single-option prompts.
    """

    next_handler = final_handler
    for story in reversed(story_args_list):
        next_handler = _story_to_pick_handler(story, next_handler)
    return next_handler()
