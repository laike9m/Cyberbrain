from cyberbrain import Binding, Mutation, InitialValue


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
        "l1": [InitialValue(target="l1", value=[1, 2], lineno=12)],
        "m1": [InitialValue(target="m1", value={1: 2}, lineno=19)],
        "m2": [InitialValue(target="m2", value={1: 2}, lineno=19)],
        "numbers": [InitialValue(target="numbers", value=[1, 2, 3, 4], lineno=13)],
        "a": [
            Binding(target="a", value="h", sources=set(), lineno=11),
            Mutation(target="a", value=1, sources={"l1"}, lineno=12),
            Mutation(
                target="a",
                value=(1, 2, 1, 2, 3, 4),
                sources={"l1", "numbers"},
                lineno=16,
            ),
            Mutation(
                target="a",
                value=[1, 2, 1, 2, 3, 4],
                sources={"l1", "numbers"},
                lineno=17,
            ),
            Mutation(
                target="a",
                value={1, 2, 1, 2, 3, 4},
                sources={"l1", "numbers"},
                lineno=18,
            ),
            Mutation(target="a", value={1: 2}, sources={"m1", "m2"}, lineno=19),
        ],
        "b": [
            Binding(target="b", value="i", sources=set(), lineno=11),
            Mutation(target="b", value=2, sources={"l1"}, lineno=12),
        ],
        "first": [Binding(target="first", value=1, sources={"numbers"}, lineno=13)],
        "rest": [
            Binding(target="rest", value=[2, 3, 4], sources={"numbers"}, lineno=13)
        ],
        "beginning": [
            Binding(target="beginning", value=[1, 2, 3], sources={"numbers"}, lineno=14)
        ],
        "last": [Binding(target="last", value=4, sources={"numbers"}, lineno=14)],
        "head": [Binding(target="head", value=1, sources={"numbers"}, lineno=15)],
        "middle": [
            Binding(target="middle", value=[2, 3], sources={"numbers"}, lineno=15)
        ],
        "tail": [Binding(target="tail", value=4, sources={"numbers"}, lineno=15)],
    }
