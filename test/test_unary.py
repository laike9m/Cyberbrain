from cyberbrain import Binding, InitialValue, Symbol
from utils import assert_GetFrame


def test_unary_operations(tracer, rpc_stub):
    a = 1

    tracer.start_tracing()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.stop_tracing()

    assert tracer.events == [
        InitialValue(target=Symbol("a"), value=1, lineno=10),
        Binding(target=Symbol("b"), value=1, sources={Symbol("a")}, lineno=10),
        Binding(target=Symbol("b"), value=-1, sources={Symbol("a")}, lineno=11),
        Binding(target=Symbol("b"), value=False, sources={Symbol("a")}, lineno=12),
        Binding(target=Symbol("b"), value=-2, sources={Symbol("a")}, lineno=13),
    ]

    assert_GetFrame(rpc_stub, "test_unary_operations")
