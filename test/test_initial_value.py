from cyberbrain import Binding, InitialValue, Symbol


def test_existing_variable_emit_initial_value(tracer):
    x = "foo"
    tracer.init()
    y = x
    tracer.register()

    assert tracer.events == {
        "x": [InitialValue(target=Symbol("x"), value="foo", lineno=7)],
        "y": [
            Binding(target=Symbol("y"), value="foo", sources={Symbol("x")}, lineno=7)
        ],
    }
