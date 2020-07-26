from cyberbrain import Binding, Mutation, InitialValue, Symbol
from utils import assert_GetFrame


def test_unary_operations(tracer, rpc_stub):
    a = 1

    tracer.init()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.register()

    assert tracer.events == {
        "a": [InitialValue(target=Symbol("a"), value=1, lineno=10)],
        "b": [
            Binding(target=Symbol("b"), value=1, sources={Symbol("a")}, lineno=10),
            Mutation(target=Symbol("b"), value=-1, sources={Symbol("a")}, lineno=11),
            Mutation(target=Symbol("b"), value=False, sources={Symbol("a")}, lineno=12),
            Mutation(target=Symbol("b"), value=-2, sources={Symbol("a")}, lineno=13),
        ],
    }

    assert_GetFrame(rpc_stub, "test_unary_operations")
