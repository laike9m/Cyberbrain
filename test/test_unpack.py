from cyberbrain import Binding, Mutation, InitialValue, Symbol


def test_unpack(tracer):
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
        "l1": [InitialValue(target=Symbol("l1"), value=[1, 2], lineno=12)],
        "m1": [InitialValue(target=Symbol("m1"), value={1: 2}, lineno=19)],
        "m2": [InitialValue(target=Symbol("m2"), value={1: 2}, lineno=19)],
        "numbers": [
            InitialValue(target=Symbol("numbers"), value=[1, 2, 3, 4], lineno=13)
        ],
        "a": [
            Binding(target=Symbol("a"), value="h", sources=set(), lineno=11),
            Mutation(target=Symbol("a"), value=1, sources={Symbol("l1")}, lineno=12),
            Mutation(
                target=Symbol("a"),
                value=(1, 2, 1, 2, 3, 4),
                sources={Symbol("l1"), Symbol("numbers")},
                lineno=16,
            ),
            Mutation(
                target=Symbol("a"),
                value=[1, 2, 1, 2, 3, 4],
                sources={Symbol("l1"), Symbol("numbers")},
                lineno=17,
            ),
            Mutation(
                target=Symbol("a"),
                value={1, 2, 1, 2, 3, 4},
                sources={Symbol("l1"), Symbol("numbers")},
                lineno=18,
            ),
            Mutation(
                target=Symbol("a"),
                value={1: 2},
                sources={Symbol("m1"), Symbol("m2")},
                lineno=19,
            ),
        ],
        "b": [
            Binding(target=Symbol("b"), value="i", sources=set(), lineno=11),
            Mutation(target=Symbol("b"), value=2, sources={Symbol("l1")}, lineno=12),
        ],
        "first": [
            Binding(
                target=Symbol("first"), value=1, sources={Symbol("numbers")}, lineno=13
            )
        ],
        "rest": [
            Binding(
                target=Symbol("rest"),
                value=[2, 3, 4],
                sources={Symbol("numbers")},
                lineno=13,
            )
        ],
        "beginning": [
            Binding(
                target=Symbol("beginning"),
                value=[1, 2, 3],
                sources={Symbol("numbers")},
                lineno=14,
            )
        ],
        "last": [
            Binding(
                target=Symbol("last"), value=4, sources={Symbol("numbers")}, lineno=14
            )
        ],
        "head": [
            Binding(
                target=Symbol("head"), value=1, sources={Symbol("numbers")}, lineno=15
            )
        ],
        "middle": [
            Binding(
                target=Symbol("middle"),
                value=[2, 3],
                sources={Symbol("numbers")},
                lineno=15,
            )
        ],
        "tail": [
            Binding(
                target=Symbol("tail"), value=4, sources={Symbol("numbers")}, lineno=15
            )
        ],
    }
