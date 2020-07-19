from cyberbrain import Creation, Mutation, InitialValue


def test_unary_operations(tracer):
    a = 1

    tracer.init()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.register()

    assert tracer.events == {
        "a": [InitialValue(target="a", value=1, lineno=9)],
        "b": [
            Creation(target="b", value=1, sources={"a"}, lineno=9),
            Mutation(target="b", value=-1, sources={"a"}, lineno=10),
            Mutation(target="b", value=False, sources={"a"}, lineno=11),
            Mutation(target="b", value=-2, sources={"a"}, lineno=12),
        ],
    }
