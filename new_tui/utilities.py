import time


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
