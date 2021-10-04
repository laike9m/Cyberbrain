from cyberbrain import Symbol, InitialValue, Return


def test_recursion_decorator(trace, check_golden_file):
    @trace
    def fib(n):
        if n <= 1:
            return n
        else:
            return fib(n - 1) + fib(n - 2)

    print(fib(3))


def test_recursion_tracer(tracer, check_golden_file):
    def fib(n):
        return n if n <= 1 else fib(n - 1) + fib(n - 2)

    # tracer.stop can't be placed inside fib, because it will be called first by inner
    # calls. And tracer.start() has to be called in the same frame as tracer.stop().
    tracer.start()
    print(fib(3))
    tracer.stop()
