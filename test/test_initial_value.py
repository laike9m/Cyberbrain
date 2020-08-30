from cyberbrain import Binding, InitialValue, Symbol
from utils import assert_GetFrame


def test_existing_variable_emit_initial_value(tracer, rpc_stub):
    x = "foo"
    tracer.start()
    y = x
    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("x"), value="foo", lineno=8),
        Binding(target=Symbol("y"), value="foo", sources={Symbol("x")}, lineno=8),
    ]

    assert_GetFrame(rpc_stub, "test_existing_variable_emit_initial_value")
