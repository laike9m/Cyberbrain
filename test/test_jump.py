from cyberbrain import Mutation, Binding, InitialValue, Symbol
from utils import assert_GetFrame


def test_jump(tracer, rpc_stub):
    a = []
    b = "b"
    c = "c"

    tracer.init()

    if a:  # POP_JUMP_IF_FALSE
        pass  # JUMP_FORWARD
    else:
        x = 1

    if not a:  # POP_JUMP_IF_TRUE
        x = 2

    x = a != b != c  # JUMP_IF_FALSE_OR_POP
    x = a == b or c  # JUMP_IF_TRUE_OR_POP

    # TODO: Test JUMP_ABSOLUTE. This requires loop instructions to be Implemented.

    tracer.register()

    assert tracer.events == {
        "a": [InitialValue(target=Symbol("a"), value=[], lineno=12)],
        "b": [InitialValue(target=Symbol("b"), value="b", lineno=20)],
        "c": [InitialValue(target=Symbol("c"), value="c", lineno=20)],
        "x": [
            Binding(target=Symbol("x"), value=1, lineno=15),
            Mutation(target=Symbol("x"), value=2, lineno=18),
            # This is a known defect. We have no way to know `x` comes from `a`, because
            # the result of `a != b` only determines whether to jump to execute `b != c`
            # I think it's fine though.
            Mutation(
                target=Symbol("x"),
                value=True,
                sources={Symbol("b"), Symbol("c")},
                lineno=20,
            ),
            # Same defect here.
            Mutation(target=Symbol("x"), value="c", sources={Symbol("c")}, lineno=21),
        ],
    }

    assert_GetFrame(rpc_stub, "test_jump")
