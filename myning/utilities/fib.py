from functools import cache


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
