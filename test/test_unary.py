from cyberbrain import Creation, Mutation


def test_unary_operations(tracer):
    a = 1

    tracer.init()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.register()

    assert tracer.events == {
        "b": [
            Creation(target="b", value=1, sources={"a"}),
            Mutation(target="b", value=-1, sources={"a"}),
            Mutation(target="b", value=False, sources={"a"}),
            Mutation(target="b", value=-2, sources={"a"}),
        ]
    }
