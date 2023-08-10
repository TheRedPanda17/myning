import random

import pytest

from myning.utils.utils import boosted_random_choice, fibonacci, fibonacci_sum


def test_fibonacci():
    fibonacci_sequence = [fibonacci(i) for i in range(1, 11)]
    assert fibonacci_sequence == [0, 1, 3, 5, 8, 13, 21, 34, 55, 89]


def test_fibonacci_sum():
    assert fibonacci_sum(1) == 0
    assert fibonacci_sum(2) == 1
    assert fibonacci_sum(3) == 1 + 3
    assert fibonacci_sum(4) == 1 + 3 + 5
    assert fibonacci_sum(5) == 1 + 3 + 5 + 8
    assert fibonacci_sum(10) == 1 + 3 + 5 + 8 + 13 + 21 + 34 + 55 + 89


@pytest.mark.parametrize(
    "arr,boost_percent,expected_percent",
    [
        ([1, 2, 3, 4, 5], 0.2, 0.48),
        ([1, 2, 3, 4, 5], 0.5, 0.6),
        ([1, 2, 3, 4, 5], 0.0, 0.4),
        ([1, 2, 3, 4, 5], 1.0, 0.8),
        ([3, 4, 5, 7, 8, 9, 200], 0.5, 0.0),
        ([-1, 0, 1], 0.5, 1.0),
        ([3, 2, 1, 0, -1, -2], 0.4, 0.99),
    ],
)
def test_boosted_random_choice(arr, boost_percent, expected_percent):
    random.seed(42)
    boosted_count = 0
    total = 10000
    for _ in range(total):
        choice = boosted_random_choice(arr, lambda x: x < 3, boost_percent)
        if choice < 3:
            boosted_count += 1
    percent_boosted = boosted_count / total
    assert abs(percent_boosted - expected_percent) < 0.01
