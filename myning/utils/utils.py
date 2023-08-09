import random
from collections import UserList
from datetime import datetime
from functools import cache
from typing import TypeVar, Callable, Optional

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


def boosted_random_choice(
    arr: list[T], selector: Callable[[T], bool], percent_boost: float = 0.0
) -> Optional[T]:
    if not arr:
        return None
    selected_indexes = [i for i, v in enumerate(arr) if selector(v)]
    selected_count = len(selected_indexes)
    default_weight = 1 / len(arr)
    selected_weight = default_weight
    unselected_weight = default_weight

    if selected_count and percent_boost != 0.0:
        # Compute boosted probability for each selected value
        selected_probability = selected_count / len(arr)
        selected_probability = selected_probability + selected_probability * percent_boost
        selected_weight = selected_probability / selected_count
        # Compute probability of all other values
        unselected_probability = 1 - selected_probability
        unselected_count = len(arr) - selected_count
        if unselected_count > 0:
            unselected_weight = unselected_probability / unselected_count

    weights = []
    for i, v in enumerate(arr):
        if i in selected_indexes:
            weights.append(selected_weight)
        else:
            weights.append(unselected_weight)
    return random.choices(arr, weights=weights)[0]


@cache
def fibonacci(n: int) -> int:
    match n:
        case 1:
            return 0
        case 2:
            return 1
        case 3:
            return 3
        case 4:
            return 5
        case _:
            return fibonacci(n - 1) + fibonacci(n - 2)


@cache
def fibonacci_sum(n: int):
    return sum(fibonacci(i) for i in range(1, n + 1))
