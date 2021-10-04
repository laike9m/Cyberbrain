from cyberbrain import Binding, Symbol


def test_hello(tracer, check_golden_file):
    tracer.start()
    x = "hello world"  # LOAD_CONST, STORE_FAST
    y = x  # LOAD_FAST, STORE_FAST
    x, y = y, x  # ROT_TWO, STORE_FAST
    tracer.stop()

    assert tracer.events == [
        Binding(target=Symbol("x"), value='"hello world"', lineno=6),
        Binding(
            target=Symbol("y"), value='"hello world"', sources={Symbol("x")}, lineno=7
        ),
        Binding(
            target=Symbol("x"), value='"hello world"', sources={Symbol("y")}, lineno=8
        ),
        Binding(
            target=Symbol("y"), value='"hello world"', sources={Symbol("x")}, lineno=8
        ),
    ], tracer.events
