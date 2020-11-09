from cyberbrain import Symbol, Binding, InitialValue, JumpBackToLoopStart, Return
from utils import get_value  # noqa


def test_generator_function(trace, test_server):
    @trace
    def generator_function(count):
        while count > 0:
            x = yield count  # YIELD_VALUE, POP_TOP, triggers a return event.
            count -= 1

    gen = generator_function(2)
    for _ in gen:
        gen.send("foo")  # Remember that .send will yield the next value.

    trace.stop()

    assert trace.events == [
        InitialValue(
            lineno=8,
            target=Symbol("count"),
            value="2",
            repr="2",
        ),
        Binding(
            lineno=9,
            target=Symbol("x"),
            value='"foo"',
            repr='"foo"',
            sources=set(),
        ),
        Binding(
            lineno=10,
            target=Symbol("count"),
            value="1",
            repr="1",
            sources={Symbol("count")},
        ),
        JumpBackToLoopStart(
            lineno=10, jump_target=get_value({"py37": 2, "default": 0})
        ),
        Binding(
            lineno=9,
            target=Symbol("x"),
            value="null",
            repr="None",
            sources=set(),
        ),
        Binding(
            lineno=10,
            target=Symbol("count"),
            value="0",
            repr="0",
            sources={Symbol("count")},
        ),
        JumpBackToLoopStart(
            lineno=10, jump_target=get_value({"py37": 2, "default": 0})
        ),
        Return(
            lineno=10,
            value="null",
            repr="None",
            sources=set(),
        ),
    ]

    test_server.assert_frame_sent("generator_function")


def test_yield_from(trace, test_server):
    def inner():
        for i in range(2):
            yield i

    @trace
    def yield_from_function():
        yield from inner()  # CALL_FUNCTION, GET_YIELD_FROM_ITER, LOAD_CONST
        # The above line triggers two return events for sys.settrace

    for output in yield_from_function():
        print(output)

    trace.stop()

    assert trace.events == [
        InitialValue(
            lineno=77,
            target=Symbol("inner"),
            value='{"repr": "<function test_yield_from.<locals>.inner>"}',
            repr="<function test_yield_from.<locals>.inner>",
        ),
        Return(
            lineno=77,
            value="null",
            repr="None",
            sources=set(),
        ),
    ]

    test_server.assert_frame_sent("yield_from_function")
