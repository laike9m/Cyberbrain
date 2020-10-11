from cyberbrain import trace


@trace
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    fib(3)
