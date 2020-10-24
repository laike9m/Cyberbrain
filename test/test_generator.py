from cyberbrain import Symbol, Binding, InitialValue, JumpBackToLoopStart, Return


def test_generator_function(trace, rpc_stub):
    @trace
    def generator_function(count):
        a, b = 1, 1
        while count > 0:
            yield a
            a, b = b, a + b
            count -= 1

    for x in generator_function(2):
        print(f"get {x} from fib_gen")

    from utils import assert_GetFrame, get_value

    assert trace.events == [
        Binding(
            lineno=7,
            target=Symbol("a"),
            value="1",
            repr="1",
            sources=set(),
        ),
        Binding(
            lineno=7,
            target=Symbol("b"),
            value="1",
            repr="1",
            sources=set(),
        ),
        InitialValue(
            lineno=8,
            target=Symbol("count"),
            value="2",
            repr="2",
        ),
        Binding(
            lineno=10,
            target=Symbol("a"),
            value="1",
            repr="1",
            sources={Symbol("b")},
        ),
        Binding(
            lineno=10,
            target=Symbol("b"),
            value="2",
            repr="2",
            sources={Symbol("a"), Symbol("b")},
        ),
        Binding(
            lineno=11,
            target=Symbol("count"),
            value="1",
            repr="1",
            sources={Symbol("count")},
        ),
        JumpBackToLoopStart(lineno=11, jump_target=get_value({"py37": 10, "py38": 8})),
        Binding(
            lineno=10,
            target=Symbol("a"),
            value="2",
            repr="2",
            sources={Symbol("b")},
        ),
        Binding(
            lineno=10,
            target=Symbol("b"),
            value="3",
            repr="3",
            sources={Symbol("a"), Symbol("b")},
        ),
        Binding(
            lineno=11,
            target=Symbol("count"),
            value="0",
            repr="0",
            sources={Symbol("count")},
        ),
        JumpBackToLoopStart(lineno=11, jump_target=get_value({"py37": 10, "py38": 8})),
        Return(
            lineno=11,
            value="null",
            repr="None",
            sources=set(),
        ),
    ]

    assert_GetFrame(rpc_stub, "generator_function")
