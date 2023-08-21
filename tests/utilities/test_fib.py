from myning.utilities.fib import fibonacci, fibonacci_sum


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
