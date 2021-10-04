from cyberbrain import Binding, InitialValue, Symbol


def test_existing_variable_emit_initial_value(tracer, check_golden_file):
    x = "foo"
    tracer.start()
    y = x
    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("x"), value='"foo"', lineno=-1),
        Binding(target=Symbol("y"), value='"foo"', sources={Symbol("x")}, lineno=7),
    ]
