from cyberbrain import Binding, Mutation, InitialValue, Symbol
from utils import assert_GetFrame


def test_unpack(tracer, rpc_stub):
    l1 = [1, 2]
    numbers = [1, 2, 3, 4]
    m1 = m2 = {1: 2}

    tracer.init()

    a, b = "hi"  # UNPACK_SEQUENCE
    a, b = l1  # UNPACK_SEQUENCE
    first, *rest = numbers  # UNPACK_EX
    *beginning, last = numbers  # UNPACK_EX
    head, *middle, tail = numbers  # UNPACK_EX
    a = *l1, *numbers
    a = [*l1, *numbers]
    a = {*l1, *numbers}
    a = {**m1, **m2}

    # TODO: Test dictionary items() unpack once iter_xx, call_xx, block_xx are done.

    tracer.register()

    assert tracer.events == {
        "l1": [InitialValue(target=Symbol("l1"), value=[1, 2], lineno=13)],
        "m1": [InitialValue(target=Symbol("m1"), value={1: 2}, lineno=20)],
        "m2": [InitialValue(target=Symbol("m2"), value={1: 2}, lineno=20)],
        "numbers": [
            InitialValue(target=Symbol("numbers"), value=[1, 2, 3, 4], lineno=14)
        ],
        "a": [
            Binding(target=Symbol("a"), value="h", sources=set(), lineno=12),
            Mutation(target=Symbol("a"), value=1, sources={Symbol("l1")}, lineno=13),
            Mutation(
                target=Symbol("a"),
                value=(1, 2, 1, 2, 3, 4),
                sources={Symbol("l1"), Symbol("numbers")},
                lineno=17,
            ),
            Mutation(
                target=Symbol("a"),
                value=[1, 2, 1, 2, 3, 4],
                sources={Symbol("l1"), Symbol("numbers")},
                lineno=18,
            ),
            Mutation(
                target=Symbol("a"),
                value={1, 2, 1, 2, 3, 4},
                sources={Symbol("l1"), Symbol("numbers")},
                lineno=19,
            ),
            Mutation(
                target=Symbol("a"),
                value={1: 2},
                sources={Symbol("m1"), Symbol("m2")},
                lineno=20,
            ),
        ],
        "b": [
            Binding(target=Symbol("b"), value="i", sources=set(), lineno=12),
            Mutation(target=Symbol("b"), value=2, sources={Symbol("l1")}, lineno=13),
        ],
        "first": [
            Binding(
                target=Symbol("first"), value=1, sources={Symbol("numbers")}, lineno=14
            )
        ],
        "rest": [
            Binding(
                target=Symbol("rest"),
                value=[2, 3, 4],
                sources={Symbol("numbers")},
                lineno=14,
            )
        ],
        "beginning": [
            Binding(
                target=Symbol("beginning"),
                value=[1, 2, 3],
                sources={Symbol("numbers")},
                lineno=15,
            )
        ],
        "last": [
            Binding(
                target=Symbol("last"), value=4, sources={Symbol("numbers")}, lineno=15
            )
        ],
        "head": [
            Binding(
                target=Symbol("head"), value=1, sources={Symbol("numbers")}, lineno=16
            )
        ],
        "middle": [
            Binding(
                target=Symbol("middle"),
                value=[2, 3],
                sources={Symbol("numbers")},
                lineno=16,
            )
        ],
        "tail": [
            Binding(
                target=Symbol("tail"), value=4, sources={Symbol("numbers")}, lineno=16
            )
        ],
    }

    assert_GetFrame(rpc_stub, "test_unpack")
