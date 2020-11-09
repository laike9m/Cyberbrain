from cyberbrain import Binding, InitialValue, Symbol


def test_unary_operations(tracer, test_server):
    a = 1

    tracer.start()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("a"), value="1", lineno=9),
        Binding(target=Symbol("b"), value="1", sources={Symbol("a")}, lineno=9),
        Binding(target=Symbol("b"), value="-1", sources={Symbol("a")}, lineno=10),
        Binding(target=Symbol("b"), value="false", sources={Symbol("a")}, lineno=11),
        Binding(target=Symbol("b"), value="-2", sources={Symbol("a")}, lineno=12),
    ]

    test_server.assert_frame_sent("test_unary_operations")
