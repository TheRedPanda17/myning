import random
from collections import UserList
from datetime import datetime
from functools import cache
from typing import TypeVar

T = TypeVar("T")
ListType = list[T] | UserList[T]
random.seed(datetime.now().timestamp())


def get_random_percentage():
    """Get a random percentage from 0 to 100."""
    return random.random() * 100


def get_random_int(a: int, b: int | None = None):
    """Get a random integer. Pass either a maximum (implies minimum = 0) or a range."""
    if a == 0:
        return 0
    if not b:
        b = a
        a = 0
    return random.randint(a, b)


def get_random_array_item_and_index(arr: ListType[T], max=None) -> tuple[T, int]:
    """Get a random item from an array and return it along with its index."""

    if not max or max > len(arr) - 1:
        max = len(arr) - 1
    index = get_random_int(max)
    return arr[index], index


def get_random_array_item(arr: ListType[T]) -> T:
    """Get a random item from an array."""
    return get_random_array_item_and_index(arr)[0]


@cache
def fibonacci(n: int) -> int:
    if n == 1:
        return 0
    elif n == 2:
        return 1
    elif n == 3:
        return 3
    elif n == 4:
        return 5
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


@cache
def fibonacci_sum(n: int):
    return sum(fibonacci(i) for i in range(1, n + 1))
