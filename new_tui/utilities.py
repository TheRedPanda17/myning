import time

from new_tui.chapters import PickArgs, StoryArgs


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


def story_builder(story_args_list: list[StoryArgs], final_pick: PickArgs):
    """
    Given a list of `StoryArgs`, build the chain of `PickArgs` backwards to present a series of
    single-option prompts.
    """
    next_pick = final_pick
    for story in reversed(story_args_list):
        next_pick = PickArgs(
            message=story.message,
            options=[(story.response, lambda pick_args=next_pick: pick_args)],
            subtitle=story.subtitle,
        )
    return next_pick
