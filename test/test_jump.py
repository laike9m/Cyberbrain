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
        "a": [InitialValue(target="a", value=[], lineno=11)],
        "b": [InitialValue(target="b", value="b", lineno=19)],
        "c": [InitialValue(target="c", value="c", lineno=19)],
        "x": [
            Creation(target="x", value=1, lineno=14),
            Mutation(target="x", value=2, lineno=17),
            # This is a known defect. We have no way to know `x` comes from `a`, because
            # the result of `a != b` only determines whether to jump to execute `b != c`
            # I think it's fine though.
            Mutation(target="x", value=True, sources={"b", "c"}, lineno=19),
            # Same defect here.
            Mutation(target="x", value="c", sources={"c"}, lineno=20),
        ],
    }
