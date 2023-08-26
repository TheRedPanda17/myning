import random

import pytest

from myning.utilities.rand import boosted_random_choice


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
def test_boosted_random_choice(arr: list[int], boost_percent, expected_percent):
    random.seed(42)
    boosted_count = 0
    total = 10000
    for _ in range(total):
        choice = boosted_random_choice(arr, lambda x: x < 3, boost_percent)
        if choice < 3:
            boosted_count += 1
    percent_boosted = boosted_count / total
    assert abs(percent_boosted - expected_percent) < 0.01
