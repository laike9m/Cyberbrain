from cyberbrain import Symbol  # noqa


def test_generator_function(trace):
    @trace
    def fib_gen(count):
        a, b = 1, 1
        count -= 1
        while count > 0:
            yield a
            a, b = b, a + b

    for x in fib_gen(10):
        print(x)
