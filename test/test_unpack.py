from cyberbrain import Creation, Mutation


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
        "a": [
            Creation(target="a", value="h", sources=set()),
            Mutation(target="a", value=1, sources={"l1"}),
            Mutation(target="a", value=(1, 2, 1, 2, 3, 4), sources={"l1", "numbers"}),
            Mutation(target="a", value=[1, 2, 1, 2, 3, 4], sources={"l1", "numbers"}),
            Mutation(target="a", value={1, 2, 1, 2, 3, 4}, sources={"l1", "numbers"}),
            Mutation(target="a", value={1: 2}, sources={"m1", "m2"}),
        ],
        "b": [
            Creation(target="b", value="i", sources=set()),
            Mutation(target="b", value=2, sources={"l1"}),
        ],
        "first": [Creation(target="first", value=1, sources={"numbers"}),],
        "rest": [Creation(target="rest", value=[2, 3, 4], sources={"numbers"}),],
        "beginning": [
            Creation(target="beginning", value=[1, 2, 3], sources={"numbers"}),
        ],
        "last": [Creation(target="last", value=4, sources={"numbers"}),],
        "head": [Creation(target="head", value=1, sources={"numbers"}),],
        "middle": [Creation(target="middle", value=[2, 3], sources={"numbers"}),],
        "tail": [Creation(target="tail", value=4, sources={"numbers"}),],
    }
