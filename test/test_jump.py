from cyberbrain import Mutation, Creation, InitialValue


def test_jump(tracer):
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
        'a': [InitialValue(target='a', value=[])],
        'b': [InitialValue(target='b', value='b')],
        'c': [InitialValue(target='c', value='c')],
        "x": [
            Creation(target="x", value=1, sources=set()),
            Mutation(target="x", value=2, sources=set()),
            # This is a known defect. We have no way to know `x` comes from `a`, because
            # the result of `a != b` only determines whether to jump to execute `b != c`
            # I think it's fine though.
            Mutation(target="x", value=True, sources={"b", "c"}),
            # Same defect here.
            Mutation(target="x", value="c", sources={"c"}),
        ]
    }
