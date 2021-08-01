from cyberbrain import Binding, Return, Symbol


def test_multiple_decorators(trace):
    def my_decorator(f):
        def inner(*args):
            a = 1
            f(*args)
            b = a

        return inner

    @my_decorator
    @my_decorator
    @my_decorator
    @trace
    def original_func():
        a = [1, 2, 3]

    original_func()

    assert trace.events == [
        Binding(
            lineno=18,
            target=Symbol("a"),
            value="[1,2,3]",
            repr="[1, 2, 3]",
            sources=set(),
        ),
        Return(
            lineno=18,
            value="null",
            repr="None",
            sources=set(),
        ),
    ]
